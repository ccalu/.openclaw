# DEPRECATED — This file is no longer part of the active S4 pipeline.
# Replaced by the V3 asset_pipeline (s4_query_generator + s4_image_collector + s4_visual_evaluator).
# Retained temporarily for reference. See S4_ARCHITECTURE_V2.md for current architecture.
"""S4 Image Downloader — parallel download of candidate images.

Downloads images from Serper results into targets/{tid}/candidates/
for visual evaluation by the visual_evaluator.
"""
import asyncio
import sys
from pathlib import Path

import aiohttp

from artifact_io import read_json, write_json, utc_now
from paths import sanitize_target_id

MAX_CONCURRENT_DOWNLOADS = 50
DOWNLOAD_TIMEOUT = 20  # seconds per image
MIN_IMAGE_SIZE = 5_000  # 5KB minimum (skip tiny icons/placeholders)
MAX_IMAGE_SIZE = 15_000_000  # 15MB maximum
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


async def _download_one(
    session: aiohttp.ClientSession,
    semaphore: asyncio.Semaphore,
    image_url: str,
    dest_path: Path,
) -> bool:
    """Download a single image. Returns True on success."""
    async with semaphore:
        try:
            async with session.get(
                image_url,
                timeout=aiohttp.ClientTimeout(total=DOWNLOAD_TIMEOUT),
                headers={"User-Agent": USER_AGENT},
            ) as resp:
                if resp.status != 200:
                    return False
                content_type = resp.headers.get("Content-Type", "")
                if "image" not in content_type and "octet-stream" not in content_type:
                    return False
                data = await resp.read()
                if len(data) < MIN_IMAGE_SIZE or len(data) > MAX_IMAGE_SIZE:
                    return False

                ext = _guess_extension(image_url, content_type)
                final_path = dest_path.with_suffix(ext)
                final_path.parent.mkdir(parents=True, exist_ok=True)
                final_path.write_bytes(data)
                return True
        except Exception:
            return False


async def download_target_images(
    serper_result: dict,
    sector_root: Path,
) -> dict:
    """Download all candidate images for one target.

    Returns dict with download results: which succeeded, which failed.
    """
    tid = serper_result["target_id"]
    stid = sanitize_target_id(tid)
    candidates = serper_result.get("candidates", [])
    candidates_dir = sector_root / "targets" / stid / "candidates"
    candidates_dir.mkdir(parents=True, exist_ok=True)

    semaphore = asyncio.Semaphore(MAX_CONCURRENT_DOWNLOADS)
    downloaded = []
    failed = []

    async with aiohttp.ClientSession() as session:
        tasks = []
        for candidate in candidates:
            cid = candidate["candidate_id"]
            url = candidate.get("image_url", "")
            if not url:
                failed.append(cid)
                continue
            dest = candidates_dir / f"{cid}_candidate"
            tasks.append((cid, url, _download_one(session, semaphore, url, dest)))

        results = await asyncio.gather(*[t[2] for t in tasks], return_exceptions=True)

        for (cid, url, _), result in zip(tasks, results):
            if result is True:
                downloaded.append(cid)
            else:
                failed.append(cid)

    return {
        "target_id": tid,
        "candidates_dir": str(candidates_dir),
        "downloaded": downloaded,
        "failed": failed,
        "total_downloaded": len(downloaded),
        "total_failed": len(failed),
    }


async def download_all_targets(
    sector_root: Path,
) -> list[dict]:
    """Download images for all targets that have serper results."""
    sr = sector_root.resolve()
    targets_dir = sr / "targets"
    all_results = []
    total_downloaded = 0
    total_failed = 0

    for td in sorted(targets_dir.iterdir()):
        if not td.is_dir():
            continue
        stid = td.name
        serper_file = td / f"{stid}_serper_results.json"
        if not serper_file.exists():
            continue

        serper_result = read_json(serper_file)
        result = await download_target_images(serper_result, sr)
        all_results.append(result)
        total_downloaded += result["total_downloaded"]
        total_failed += result["total_failed"]

        print(f"[downloader] {stid}: {result['total_downloaded']} downloaded, {result['total_failed']} failed")

    print(f"[downloader] DONE: {total_downloaded} downloaded, {total_failed} failed across {len(all_results)} targets")
    return all_results


def run_downloads(sector_root: Path) -> list[dict]:
    """Synchronous wrapper for download_all_targets."""
    return asyncio.run(download_all_targets(sector_root))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: image_downloader.py <sector_root>")
    run_downloads(Path(sys.argv[1]))
