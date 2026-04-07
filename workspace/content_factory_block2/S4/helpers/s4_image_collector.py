"""S4 Image Collector — Serper Google Images API + parallel download + pHash dedup.

Adapted from dataset_system/agents/base_agent.py (_search_with_strategy + _download_and_dedup).

For each target:
1. Reads queries from search_queries.json
2. Calls Serper.dev Images API (20 results per query)
3. Downloads images in parallel (aiohttp, Semaphore(50))
4. Deduplicates via pHash (ImageDeduplicator)
5. Saves unique images to targets/{tid}/candidates/
6. Writes serper_results.json
"""
import asyncio
import json
import sys
from pathlib import Path

import aiohttp
import requests

from artifact_io import read_json, write_json, utc_now
from paths import sanitize_target_id, search_queries_path, serper_results_path
from shared.image_deduplicator import ImageDeduplicator

SERPER_API_URL = "https://google.serper.dev/images"
SERPER_API_KEY = "f901d25910ed0a9e83a06d2ef9e709f62df43a0c"
RESULTS_PER_QUERY = 10

TARGET_SEMAPHORE_LIMIT = 4
DOWNLOAD_SEMAPHORE_LIMIT = 50
DOWNLOAD_TIMEOUT = 20
MIN_IMAGE_SIZE = 5_000      # 5KB
MAX_IMAGE_SIZE = 15_000_000  # 15MB
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36"


def _guess_extension(url: str, content_type: str = "") -> str:
    url_lower = url.lower().split("?")[0]
    for ext in [".jpg", ".jpeg", ".png", ".gif", ".webp"]:
        if url_lower.endswith(ext):
            return ext
    if "png" in content_type:
        return ".png"
    if "gif" in content_type:
        return ".gif"
    if "webp" in content_type:
        return ".webp"
    return ".jpg"


def _search_serper(query: str) -> list[dict]:
    """Call Serper.dev Images API for one query. Returns list of image candidates."""
    try:
        resp = requests.post(
            SERPER_API_URL,
            json={"q": query, "num": RESULTS_PER_QUERY},
            headers={"X-API-KEY": SERPER_API_KEY},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"[collector] Serper error for '{query[:50]}': {e}")
        return []

    images = data.get("images", [])
    results = []
    for img in images:
        url = img.get("imageUrl", "")
        if url:
            results.append({
                "image_url": url,
                "page_url": img.get("link", ""),
                "title": img.get("title", ""),
                "source": img.get("source", ""),
                "width": img.get("imageWidth", 0),
                "height": img.get("imageHeight", 0),
            })
    return results


async def _download_one(
    session: aiohttp.ClientSession,
    semaphore: asyncio.Semaphore,
    url: str,
) -> bytes | None:
    """Download a single image, return bytes or None."""
    async with semaphore:
        try:
            async with session.get(
                url,
                timeout=aiohttp.ClientTimeout(total=DOWNLOAD_TIMEOUT),
                headers={"User-Agent": USER_AGENT},
            ) as resp:
                if resp.status != 200:
                    return None
                ct = resp.headers.get("Content-Type", "")
                if "image" not in ct and "octet-stream" not in ct:
                    return None
                data = await resp.read()
                if len(data) < MIN_IMAGE_SIZE or len(data) > MAX_IMAGE_SIZE:
                    return None
                return data
        except Exception:
            return None


async def collect_for_target(
    target: dict,
    sector_root: Path,
) -> dict:
    """Search + download + dedup for one target.

    Reads queries from search_queries.json, calls Serper for each,
    downloads all results, deduplicates via pHash, saves to candidates/.

    Returns serper_results dict.
    """
    tid = target["target_id"]
    stid = sanitize_target_id(tid)
    label = target["canonical_label"]
    sr = sector_root.resolve()

    # Read queries
    queries_path = search_queries_path(sr, tid)
    if not queries_path.exists():
        print(f"[collector] {tid}: no search_queries.json, skipping")
        return _empty_result(tid, label)

    queries_data = read_json(queries_path)
    queries = queries_data.get("queries", [])
    if not queries:
        print(f"[collector] {tid}: no queries, skipping")
        return _empty_result(tid, label)

    # Search all queries via Serper
    all_candidates = []
    seen_urls = set()
    for query in queries:
        results = _search_serper(query)
        for r in results:
            url = r["image_url"]
            if url not in seen_urls:
                seen_urls.add(url)
                all_candidates.append(r)

    if not all_candidates:
        print(f"[collector] {tid}: 0 results from Serper")
        return _empty_result(tid, label)

    print(f"[collector] {tid}: {len(all_candidates)} unique URLs from {len(queries)} queries")

    # Download in parallel
    candidates_dir = sr / "targets" / stid / "candidates"
    candidates_dir.mkdir(parents=True, exist_ok=True)

    dl_semaphore = asyncio.Semaphore(DOWNLOAD_SEMAPHORE_LIMIT)
    deduplicator = ImageDeduplicator(threshold=10)

    downloaded_count = 0
    dedup_count = 0
    failed_count = 0
    saved_candidates = []

    async with aiohttp.ClientSession() as session:
        download_tasks = [
            _download_one(session, dl_semaphore, c["image_url"])
            for c in all_candidates
        ]
        results = await asyncio.gather(*download_tasks)

    for candidate, data in zip(all_candidates, results):
        if data is None:
            failed_count += 1
            continue

        # pHash dedup
        is_dup, reason = deduplicator.is_duplicate(candidate["image_url"], data)
        if is_dup:
            dedup_count += 1
            continue

        # Save to candidates/
        cid = f"c{downloaded_count + 1:03d}"
        ext = _guess_extension(candidate["image_url"])
        dest = candidates_dir / f"{cid}_candidate{ext}"
        dest.write_bytes(data)
        downloaded_count += 1

        saved_candidates.append({
            "candidate_id": cid,
            "image_url": candidate["image_url"],
            "page_url": candidate.get("page_url", ""),
            "title": candidate.get("title", ""),
            "source": candidate.get("source", ""),
            "local_path": str(dest),
        })

    result = {
        "target_id": tid,
        "canonical_label": label,
        "queries_used": queries,
        "total_urls": len(all_candidates),
        "downloaded": downloaded_count,
        "duplicates_removed": dedup_count,
        "failed_downloads": failed_count,
        "candidates": saved_candidates,
        "collected_at": utc_now(),
    }

    # Save serper results
    out_path = serper_results_path(sr, tid)
    write_json(out_path, result)

    print(f"[collector] {tid} ({label}): {downloaded_count} saved, {dedup_count} deduped, {failed_count} failed")
    return result


def _empty_result(tid: str, label: str) -> dict:
    return {
        "target_id": tid,
        "canonical_label": label,
        "queries_used": [],
        "total_urls": 0,
        "downloaded": 0,
        "duplicates_removed": 0,
        "failed_downloads": 0,
        "candidates": [],
        "collected_at": utc_now(),
    }


async def collect_all_targets(
    intake_path: Path,
    sector_root: Path,
) -> list[dict]:
    """Collect images for all targets with Semaphore(4)."""
    sr = sector_root.resolve()
    intake = read_json(intake_path)
    all_targets = intake["research_targets"]
    targets = [t for t in all_targets if t.get("handling_mode") != "skip_visual_retrieval"]

    semaphore = asyncio.Semaphore(TARGET_SEMAPHORE_LIMIT)

    async def _collect_with_semaphore(target):
        async with semaphore:
            return await collect_for_target(target, sr)

    tasks = [_collect_with_semaphore(t) for t in targets]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    valid = []
    for target, result in zip(targets, results):
        if isinstance(result, Exception):
            print(f"[collector] {target['target_id']}: FAILED: {result}")
            continue
        valid.append(result)

    total_saved = sum(r["downloaded"] for r in valid)
    total_dedup = sum(r["duplicates_removed"] for r in valid)
    print(f"[collector] DONE: {len(valid)}/{len(targets)} targets, {total_saved} images saved, {total_dedup} deduped")
    return valid


def run_collection(intake_path: Path, sector_root: Path) -> list[dict]:
    """Synchronous wrapper."""
    return asyncio.run(collect_all_targets(intake_path, sector_root))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: s4_image_collector.py <intake_path> <sector_root>")
    run_collection(Path(sys.argv[1]), Path(sys.argv[2]))
