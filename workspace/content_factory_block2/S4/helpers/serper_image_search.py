# DEPRECATED — This file is no longer part of the active S4 pipeline.
# Replaced by the V3 asset_pipeline (s4_query_generator + s4_image_collector + s4_visual_evaluator).
# Retained temporarily for reference. See S4_ARCHITECTURE_V2.md for current architecture.
"""S4 Serper Image Search — Google Images discovery via Serper.dev API.

Replaces research_worker.py (Brave Search textual URLs) as the primary
visual discovery mechanism. Returns direct image URLs with metadata.
"""
import json
import os
import sys
from pathlib import Path

import requests

from artifact_io import read_json, write_json, utc_now
from paths import sanitize_target_id

SERPER_API_URL = "https://google.serper.dev/images"
SERPER_API_KEY = os.environ.get("SERPER_API_KEY", "f901d25910ed0a9e83a06d2ef9e709f62df43a0c")
RESULTS_PER_TARGET = 20


def search_images_for_target(
    target: dict,
    brief: dict,
    sector_root: Path,
) -> dict:
    """Search Google Images for one target using Serper.dev.

    Args:
        target: research target dict from intake (target_id, canonical_label, target_type, etc.)
        brief: target research brief dict (search_goals, etc.)
        sector_root: S4 sector root path

    Returns:
        Dict with candidate image results and metadata.
    """
    tid = target["target_id"]
    label = target["canonical_label"]
    target_type = target.get("target_type", "")

    # Build search query from brief search_goals
    search_goals = brief.get("search_goals", [])
    if search_goals:
        query = search_goals[0]  # Use primary search goal
    else:
        query = f"{label} photograph high quality"

    # Add context for better results
    if target_type in ("person_historical",):
        query += " portrait photograph"
    elif target_type in ("architectural_anchor", "interior_space"):
        query += " photograph"
    elif target_type in ("symbolic_sequence",):
        query += " artistic reference"

    if not SERPER_API_KEY:
        print(f"[serper] WARNING: no SERPER_API_KEY, skipping {tid}")
        return _empty_result(tid, label, query)

    try:
        response = requests.post(
            SERPER_API_URL,
            json={"q": query, "num": RESULTS_PER_TARGET},
            headers={"X-API-KEY": SERPER_API_KEY},
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"[serper] ERROR for {tid} ({label}): {e}")
        return _empty_result(tid, label, query)

    images = data.get("images", [])
    candidates = []
    for i, img in enumerate(images):
        candidates.append({
            "candidate_id": f"c{i+1:03d}",
            "image_url": img.get("imageUrl", ""),
            "page_url": img.get("link", ""),
            "title": img.get("title", ""),
            "source": img.get("source", ""),
            "width": img.get("imageWidth", 0),
            "height": img.get("imageHeight", 0),
        })

    result = {
        "target_id": tid,
        "canonical_label": label,
        "query_used": query,
        "candidates_found": len(candidates),
        "candidates": candidates,
        "searched_at": utc_now(),
    }

    print(f"[serper] {tid} ({label}): {len(candidates)} images found for '{query[:60]}'")
    return result


def _empty_result(tid: str, label: str, query: str) -> dict:
    return {
        "target_id": tid,
        "canonical_label": label,
        "query_used": query,
        "candidates_found": 0,
        "candidates": [],
        "searched_at": utc_now(),
    }


def search_all_targets(
    intake_path: Path,
    sector_root: Path,
) -> list[dict]:
    """Search images for all targets. Returns list of results per target."""
    intake = read_json(intake_path)
    targets = intake["research_targets"]
    sr = sector_root.resolve()

    all_results = []
    for target in targets:
        tid = target["target_id"]
        stid = sanitize_target_id(tid)

        # Read brief for search goals
        brief_path = sr / "targets" / stid / f"{stid}_brief.json"
        if brief_path.exists():
            brief = read_json(brief_path)
        else:
            brief = {"search_goals": [f"{target['canonical_label']} photograph"]}

        result = search_images_for_target(target, brief, sr)

        # Save search results per target
        out_path = sr / "targets" / stid / f"{stid}_serper_results.json"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        write_json(out_path, result)

        all_results.append(result)

    total = sum(r["candidates_found"] for r in all_results)
    print(f"[serper] DONE: {len(all_results)} targets, {total} total candidates")
    return all_results


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: serper_image_search.py <intake_path> <sector_root>")
    search_all_targets(Path(sys.argv[1]), Path(sys.argv[2]))
