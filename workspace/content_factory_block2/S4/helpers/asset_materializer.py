# DEPRECATED — This file is no longer part of the active S4 pipeline.
# Replaced by the V3 asset_pipeline (s4_query_generator + s4_image_collector + s4_visual_evaluator).
# Retained temporarily for reference. See S4_ARCHITECTURE_V2.md for current architecture.
"""S4 Asset Materializer — downloads best candidate assets and creates page records.

Separate materialization layer:
- Does NOT modify raw candidate_set.json
- Does NOT modify evaluated_candidate_set.json
- Produces asset_materialization_report.json per target
- Downloads images from open domains to targets/{tid}/assets/
- Creates page record JSONs in targets/{tid}/captures/
- Skips rights-reserved domains with explicit failure_reason
- Uses Firecrawl CLI for image extraction and page scraping
"""
import json
import re
import subprocess
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

from artifact_io import read_json, write_json, utc_now
from paths import evaluated_set_path, candidate_set_path, sanitize_target_id
from schema_validator import validate_artifact_strict

# ---------------------------------------------------------------------------
# Domain classification
# ---------------------------------------------------------------------------

# Domains where direct image download is allowed (free/open license)
OPEN_DOWNLOAD_DOMAINS = {
    "pixabay.com", "unsplash.com", "www.loc.gov", "loc.gov",
    "commons.wikimedia.org", "upload.wikimedia.org",
    "artsandculture.google.com",
}

# Domains where we extract metadata only (rights reserved / walled garden)
SKIP_DOMAINS = {
    "www.gettyimages.com", "www.gettyimages.com.br", "gettyimages.com",
    "www.istockphoto.com", "istockphoto.com",
    "br.freepik.com", "www.freepik.com", "freepik.com",
    "www.shutterstock.com", "shutterstock.com",
    "www.facebook.com", "facebook.com",
    "www.instagram.com", "instagram.com",
    "www.tiktok.com", "tiktok.com",
}

# Domains good for page records (factual content worth capturing)
PAGE_RECORD_DOMAINS = {
    "en.wikipedia.org", "pt.wikipedia.org", "es.wikipedia.org",
    "www.britannica.com", "britannica.com",
    "oglobo.globo.com", "www.bbc.com", "bbc.com",
    "www.imdb.com", "imdb.com",
}

DOWNLOAD_TIMEOUT = 30  # seconds per download attempt
FIRECRAWL_TIMEOUT = 45  # seconds per firecrawl scrape
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36"


# ---------------------------------------------------------------------------
# Download helpers
# ---------------------------------------------------------------------------

def _sanitize_filename(name: str, max_len: int = 80) -> str:
    """Create safe filename from label."""
    cleaned = name.lower().strip()
    cleaned = re.sub(r"[^a-z0-9_\-]", "_", cleaned)
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")
    return cleaned[:max_len]


def _domain_short(domain: str) -> str:
    """Shorten domain for filename."""
    return domain.replace("www.", "").replace(".com", "").replace(".org", "").replace(".gov", "")[:20]


def _guess_extension(url: str, content_type: str = "") -> str:
    """Guess file extension from URL or content type."""
    url_lower = url.lower().split("?")[0]
    for ext in [".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".tiff"]:
        if url_lower.endswith(ext):
            return ext
    if "jpeg" in content_type or "jpg" in content_type:
        return ".jpg"
    if "png" in content_type:
        return ".png"
    if "gif" in content_type:
        return ".gif"
    if "webp" in content_type:
        return ".webp"
    return ".jpg"  # default


def _try_download_image(url: str, dest_path: Path) -> bool:
    """Attempt to download an image. Returns True on success."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=DOWNLOAD_TIMEOUT) as resp:
            content_type = resp.headers.get("Content-Type", "")
            # Verify it's actually an image
            if "image" not in content_type and "octet-stream" not in content_type:
                return False
            data = resp.read(10 * 1024 * 1024)  # max 10MB
            if len(data) < 1000:  # too small, probably error page
                return False
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            dest_path.write_bytes(data)
            return True
    except Exception:
        return False


def _try_find_image_url(page_url: str, domain: str) -> str | None:
    """Try to extract a direct image URL from a page URL."""
    # Wikipedia: try to get the main image via API
    if "wikipedia.org" in domain:
        parts = page_url.rstrip("/").split("/")
        if len(parts) >= 2:
            title = parts[-1]
            lang = "en"
            if "pt.wikipedia" in domain:
                lang = "pt"
            api_url = f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{title}"
            try:
                req = urllib.request.Request(api_url, headers={"User-Agent": USER_AGENT})
                with urllib.request.urlopen(req, timeout=15) as resp:
                    data = json.loads(resp.read())
                    thumb = data.get("thumbnail", {}).get("source")
                    original = data.get("originalimage", {}).get("source")
                    return original or thumb
            except Exception:
                pass
    return None


def _firecrawl_scrape(url: str, output_path: Path, with_images: bool = True) -> dict | None:
    """Use Firecrawl CLI to scrape a page. Returns parsed JSON or None on failure."""
    fmt = "markdown,images" if with_images else "markdown"
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        result = subprocess.run(
            ["firecrawl.cmd", "scrape", url, "--format", fmt, "--json",
             "-o", str(output_path)],
            capture_output=True, text=True, timeout=FIRECRAWL_TIMEOUT,
        )
        if result.returncode != 0:
            print(f"[materializer] firecrawl failed for {url[:80]}: exit {result.returncode}")
            return None
        if output_path.exists():
            return json.loads(output_path.read_text(encoding="utf-8"))
        return None
    except Exception as e:
        print(f"[materializer] firecrawl exception for {url[:80]}: {e}")
        return None


def _firecrawl_extract_best_image(scrape_data: dict, label: str) -> str | None:
    """Pick the best image URL from Firecrawl scrape results."""
    images = scrape_data.get("images", [])
    if not images:
        return None

    # Filter out icons, logos, tiny UI elements, SVGs
    skip_patterns = ["logo", "icon", "sprite", "favicon", "button", "arrow",
                     "Commons-logo", "OOjs_UI", "edit-ltr", "osm-intl",
                     "social-media", "badge", "widget", "avatar",
                     "20px-", "15px-", "10px-", ".svg"]
    good_images = []
    for img_url in images:
        if not isinstance(img_url, str):
            continue
        if any(pat in img_url for pat in skip_patterns):
            continue
        # Must look like an actual image URL
        if not any(ext in img_url.lower() for ext in [".jpg", ".jpeg", ".png", ".webp", ".gif", "image-services", "storage-services", "thumb/"]):
            continue
        good_images.append(img_url)

    if not good_images:
        return None

    # Score by relevance to label + resolution
    label_words = set(w for w in label.lower().split() if len(w) > 3)
    scored = []
    for img_url in good_images:
        url_lower = img_url.lower()
        score = sum(2 for w in label_words if w in url_lower)
        # Resolution scoring
        if any(s in img_url for s in ["960px", "1024px", "1280px", "/full/", "original"]):
            score += 3
        elif any(s in img_url for s in ["500px", "640px", "800px"]):
            score += 2
        elif any(s in img_url for s in ["250px", "330px", "400px"]):
            score += 1
        elif "150px" in img_url or "100px" in img_url:
            score -= 1
        # Prefer content-hosting domains
        if any(d in img_url for d in ["upload.wikimedia", "tile.loc.gov", "artsandculture"]):
            score += 2
        scored.append((score, img_url))

    scored.sort(key=lambda x: -x[0])
    return scored[0][1] if scored else good_images[0]


def _create_page_record(url: str, title: str, domain: str, candidate_id: str,
                         dest_path: Path) -> bool:
    """Create a page record JSON with metadata and text excerpt."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=DOWNLOAD_TIMEOUT) as resp:
            content = resp.read(100 * 1024).decode("utf-8", errors="replace")  # max 100KB

        # Extract text content (strip HTML tags crudely)
        text = re.sub(r"<script[^>]*>.*?</script>", "", content, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        excerpt = text[:2000]  # first 2000 chars

        record = {
            "candidate_id": candidate_id,
            "source_url": url,
            "page_title": title,
            "source_domain": domain,
            "excerpt": excerpt,
            "captured_at": utc_now(),
        }
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        write_json(dest_path, record)
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Main materializer
# ---------------------------------------------------------------------------

def materialize_target(
    sector_root: Path,
    target_id: str,
    job_id: str,
) -> Path:
    """Materialize best candidates for one target.

    Returns path to the materialization report.
    """
    sr = sector_root.resolve()
    tid = sanitize_target_id(target_id)
    target_dir = sr / "targets" / tid

    # Read evaluated set to find best candidates
    eval_path = evaluated_set_path(sr, target_id)
    if not eval_path.exists():
        print(f"[materializer] {tid}: no evaluated set, skipping")
        return _write_empty_report(target_dir, target_id, job_id)

    eval_set = read_json(eval_path)
    best_ids = set(eval_set.get("best_candidate_ids", []))

    if not best_ids:
        print(f"[materializer] {tid}: no best candidates, skipping")
        return _write_empty_report(target_dir, target_id, job_id)

    # Read raw candidate set for URLs
    cs_path = candidate_set_path(sr, target_id)
    if not cs_path.exists():
        print(f"[materializer] {tid}: no candidate set, skipping")
        return _write_empty_report(target_dir, target_id, job_id)

    raw_set = read_json(cs_path)
    candidates_by_id = {c["candidate_id"]: c for c in raw_set.get("candidates", [])}

    # Materialize each best candidate
    entries = []
    downloaded = 0
    page_records = 0
    skipped = 0
    failed = 0

    for cid in sorted(best_ids):
        candidate = candidates_by_id.get(cid)
        if not candidate:
            entries.append({
                "candidate_id": cid,
                "materialization_status": "failed",
                "acquisition_mode": "reference_only",
                "local_asset_path": None,
                "capture_path": None,
                "failure_reason": "candidate_id not found in raw set",
            })
            failed += 1
            continue

        url = candidate.get("source_url", "")
        domain = candidate.get("source_domain", "")
        title = candidate.get("page_title", "")
        domain_clean = _domain_short(domain)
        label_clean = _sanitize_filename(title or cid)

        # Check if domain should be skipped
        if any(skip in domain for skip in SKIP_DOMAINS):
            entries.append({
                "candidate_id": cid,
                "materialization_status": "skipped",
                "acquisition_mode": "reference_only",
                "local_asset_path": None,
                "capture_path": None,
                "failure_reason": f"rights_reserved domain ({domain})",
            })
            skipped += 1
            print(f"[materializer] {tid}/{cid}: skipped ({domain})")
            continue

        # Strategy: Firecrawl scrape → extract image → download image → page record fallback
        asset_downloaded = False
        firecrawl_json = target_dir / "captures" / f"{cid}_{domain_clean}_firecrawl.json"

        # Step 1: Try Firecrawl scrape to extract images + content
        scrape_data = _firecrawl_scrape(url, firecrawl_json, with_images=True)

        if scrape_data:
            # Step 2: Try to find and download the best image from the scrape
            best_img = _firecrawl_extract_best_image(scrape_data, title or candidate.get("canonical_label", ""))
            if best_img:
                ext = _guess_extension(best_img)
                asset_path = target_dir / "assets" / f"{cid}_{domain_clean}_{label_clean}{ext}"
                if _try_download_image(best_img, asset_path):
                    asset_downloaded = True

        # Step 3: If Firecrawl didn't work, try direct download (urllib fallback)
        if not asset_downloaded:
            img_url = _try_find_image_url(url, domain)
            if img_url:
                ext = _guess_extension(img_url)
                asset_path = target_dir / "assets" / f"{cid}_{domain_clean}_{label_clean}{ext}"
                if _try_download_image(img_url, asset_path):
                    asset_downloaded = True

        if asset_downloaded:
            entries.append({
                "candidate_id": cid,
                "materialization_status": "downloaded",
                "acquisition_mode": "direct_download",
                "local_asset_path": str(asset_path),
                "capture_path": None,
                "failure_reason": None,
            })
            downloaded += 1
            size_kb = round(asset_path.stat().st_size / 1024, 1)
            print(f"[materializer] {tid}/{cid}: downloaded ({size_kb}KB)")
            # Clean up firecrawl temp file if we got the asset
            if firecrawl_json.exists():
                firecrawl_json.unlink()
            continue

        # Step 4: Page record fallback — use Firecrawl markdown or urllib
        capture_file = target_dir / "captures" / f"{cid}_{domain_clean}_{label_clean}.json"
        if scrape_data and scrape_data.get("markdown"):
            # Use Firecrawl markdown as page record
            excerpt = scrape_data["markdown"][:3000]
            record = {
                "candidate_id": cid,
                "source_url": url,
                "page_title": scrape_data.get("metadata", {}).get("title", title),
                "source_domain": domain,
                "excerpt": excerpt,
                "captured_at": utc_now(),
                "source": "firecrawl",
            }
            capture_file.parent.mkdir(parents=True, exist_ok=True)
            write_json(capture_file, record)
            # Clean up raw firecrawl json
            if firecrawl_json.exists() and firecrawl_json != capture_file:
                firecrawl_json.unlink()
            entries.append({
                "candidate_id": cid,
                "materialization_status": "page_record",
                "acquisition_mode": "metadata_extract",
                "local_asset_path": None,
                "capture_path": str(capture_file),
                "failure_reason": None,
            })
            page_records += 1
            print(f"[materializer] {tid}/{cid}: page_record via firecrawl ({domain})")
            continue
        elif _create_page_record(url, title, domain, cid, capture_file):
            entries.append({
                "candidate_id": cid,
                "materialization_status": "page_record",
                "acquisition_mode": "metadata_extract",
                "local_asset_path": None,
                "capture_path": str(capture_file),
                "failure_reason": None,
            })
            page_records += 1
            print(f"[materializer] {tid}/{cid}: page_record via urllib ({domain})")
            continue

        # Everything failed
        entries.append({
            "candidate_id": cid,
            "materialization_status": "failed",
            "acquisition_mode": "best_effort",
            "local_asset_path": None,
            "capture_path": None,
            "failure_reason": f"firecrawl + urllib both failed for {url}",
        })
        failed += 1
        print(f"[materializer] {tid}/{cid}: failed")

    # Write report
    report = {
        "contract_version": "s4.asset_materialization_report.v1",
        "target_id": target_id,
        "job_id": job_id,
        "materialized_at": utc_now(),
        "entries": entries,
        "summary": {
            "total_best_candidates": len(best_ids),
            "downloaded": downloaded,
            "page_records": page_records,
            "skipped": skipped,
            "failed": failed,
        },
    }

    validate_artifact_strict(report, "asset_materialization_report")

    report_path = target_dir / f"{tid}_asset_materialization_report.json"
    write_json(report_path, report)
    print(f"[materializer] {tid}: report written ({downloaded} assets, {page_records} records, {skipped} skipped)")
    return report_path


def _write_empty_report(target_dir: Path, target_id: str, job_id: str) -> Path:
    """Write an empty materialization report."""
    tid = sanitize_target_id(target_id)
    report = {
        "contract_version": "s4.asset_materialization_report.v1",
        "target_id": target_id,
        "job_id": job_id,
        "materialized_at": utc_now(),
        "entries": [],
        "summary": {
            "total_best_candidates": 0,
            "downloaded": 0,
            "page_records": 0,
            "skipped": 0,
            "failed": 0,
        },
    }
    report_path = target_dir / f"{tid}_asset_materialization_report.json"
    write_json(report_path, report)
    return report_path


def materialize_all(sector_root: Path, job_id: str) -> None:
    """Materialize assets for all targets in the sector."""
    from paths import intake_path
    sr = sector_root.resolve()
    intake = read_json(intake_path(sr))
    targets = intake["research_targets"]

    print(f"[materializer] materializing assets for {len(targets)} targets")
    total_downloaded = 0
    total_records = 0
    total_skipped = 0

    for target in targets:
        tid = target["target_id"]
        report_path = materialize_target(sr, tid, job_id)
        report = read_json(report_path)
        s = report["summary"]
        total_downloaded += s["downloaded"]
        total_records += s["page_records"]
        total_skipped += s["skipped"]

    print(f"[materializer] DONE: {total_downloaded} assets, {total_records} page records, {total_skipped} skipped")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: asset_materializer.py <sector_root> <job_id>")
    materialize_all(Path(sys.argv[1]), sys.argv[2])
