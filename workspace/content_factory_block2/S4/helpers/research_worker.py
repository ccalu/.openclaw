# DEPRECATED — This file is no longer part of the active S4 pipeline.
# Replaced by the V3 asset_pipeline (s4_query_generator + s4_image_collector + s4_visual_evaluator).
# Retained temporarily for reference. See S4_ARCHITECTURE_V2.md for current architecture.
"""S4 Research Worker -- performs real web research for one target.

Search strategy: Brave Search (free, primary) + Firecrawl (scrape/fallback).
"""
import os
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

import requests

from artifact_io import read_json, write_json, utc_now
from paths import candidate_set_path
from schema_validator import validate_artifact_strict

import shutil

FIRECRAWL_TIMEOUT_MS = 60000
SEARCH_LIMIT = 5
FIRECRAWL_CMD = shutil.which("firecrawl") or r"C:\Users\User-OEM\AppData\Roaming\npm\firecrawl.cmd"
BRAVE_API_KEY = os.environ.get("BRAVE_API_KEY", "BSAbvnhyIJg1dOp4r7O7izXiEd--RXQ")
BRAVE_SEARCH_URL = "https://api.search.brave.com/res/v1/web/search"


def _run_brave_search(query: str, limit: int = SEARCH_LIMIT) -> list:
    """Run Brave Search API (free tier, primary search source).

    Returns list of dicts with keys: title, url, snippet.
    """
    try:
        resp = requests.get(
            BRAVE_SEARCH_URL,
            headers={"X-Subscription-Token": BRAVE_API_KEY, "Accept": "application/json"},
            params={"q": query, "count": limit},
            timeout=30,
        )
        if resp.status_code != 200:
            print(f"[research_worker] Brave Search error (status={resp.status_code})")
            return []
        data = resp.json()
        results = []
        for r in data.get("web", {}).get("results", []):
            results.append({
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "snippet": r.get("description", ""),
            })
        return results
    except Exception as exc:
        print(f"[research_worker] Brave Search exception: {exc}")
        return []


def _run_firecrawl_search(query: str, limit: int = SEARCH_LIMIT) -> list:
    """Run firecrawl search and parse the plain-text output.

    Firecrawl outputs blocks like:
        Title Text
          URL: https://example.com/page
          Snippet text...

    Returns list of dicts with keys: title, url, snippet.
    """
    try:
        cmd = [FIRECRAWL_CMD, "search", query, "--limit", str(limit),
               "--timeout", str(FIRECRAWL_TIMEOUT_MS)]
        if sys.platform == "win32" and FIRECRAWL_CMD.lower().endswith((".cmd", ".bat")):
            cmd = ["cmd", "/c"] + cmd
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=90,
        )
    except subprocess.TimeoutExpired:
        print(f"[research_worker] firecrawl timeout for query: {query}")
        return []
    except FileNotFoundError:
        print("[research_worker] firecrawl CLI not found on PATH")
        return []

    if result.returncode != 0:
        print(f"[research_worker] firecrawl error (rc={result.returncode}): {result.stderr[:300]}")
        return []

    output = result.stdout.strip()
    if not output:
        return []

    # Parse plain-text output
    results = []
    lines = output.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        # Skip empty lines
        if not line:
            i += 1
            continue

        # Title line (not indented, not starting with URL:)
        if not line.startswith("  "):
            title = line.strip()
            url = ""
            snippet = ""

            # Next line should be URL
            if i + 1 < len(lines):
                url_line = lines[i + 1].strip()
                if url_line.startswith("URL:"):
                    url = url_line[4:].strip()
                    i += 2
                else:
                    i += 1

                # Next line(s) are snippet
                if i < len(lines):
                    snippet_line = lines[i].strip()
                    if snippet_line and not snippet_line.startswith("URL:"):
                        snippet = snippet_line
                        i += 1
                    else:
                        i += 1
                else:
                    i += 1
            else:
                i += 1

            if url:
                results.append({"title": title, "url": url, "snippet": snippet})
        else:
            i += 1

    return results


def _extract_domain(url: str) -> str:
    """Extract domain from URL."""
    try:
        parsed = urlparse(url)
        return parsed.netloc or "unknown"
    except Exception:
        return "unknown"


def _classify_result(title: str, url: str, snippet: str, target_type: str) -> str:
    """Preliminary classification based on source domain and content."""
    domain = _extract_domain(url).lower()
    title_lower = title.lower()
    snippet_lower = snippet.lower()

    # Wikipedia/encyclopedia -> factual_evidence
    if "wikipedia" in domain or "britannica" in domain or "enciclopedia" in domain:
        return "factual_evidence"

    # Image/photo sites -> visual_reference
    image_domains = [
        "flickr", "unsplash", "pexels", "pinterest", "getty", "alamy",
        "shutterstock", "istockphoto", "dreamstime",
    ]
    if any(d in domain for d in image_domains):
        return "visual_reference"

    # Content with "photo", "image", "foto" in title -> visual_reference
    if any(kw in title_lower for kw in ["photo", "foto", "image", "imagem", "picture"]):
        return "visual_reference"

    # History/architecture keywords -> factual_evidence
    if any(kw in title_lower for kw in ["history", "historia", "histori", "architecture", "arquitetura"]):
        return "factual_evidence"

    # Art/design/style -> stylistic_inspiration
    if any(kw in title_lower for kw in ["art", "style", "estilo", "design", "aesthetic"]):
        return "stylistic_inspiration"

    # Default based on target_type
    if target_type in ("architectural_anchor", "person_historical", "event_reference"):
        return "factual_evidence"
    return "visual_reference"


def _estimate_confidence(title: str, url: str, canonical_label: str) -> float:
    """Estimate confidence based on how well the result matches the target."""
    label_lower = canonical_label.lower()
    title_lower = title.lower()
    url_lower = url.lower()

    score = 0.5  # baseline

    # Label appears in title
    label_words = label_lower.split()
    matching_words = sum(1 for w in label_words if w in title_lower)
    if matching_words == len(label_words):
        score += 0.3
    elif matching_words > 0:
        score += 0.15

    # Wikipedia/authoritative domain bonus
    domain = _extract_domain(url).lower()
    if "wikipedia" in domain:
        score += 0.1
    elif any(d in domain for d in ["britannica", "archdaily", "cultura"]):
        score += 0.05

    return min(score, 1.0)


def _licensing_hint(url: str) -> str:
    """Rough licensing hint from domain."""
    domain = _extract_domain(url).lower()
    if "wikipedia" in domain or "wikimedia" in domain:
        return "public_domain_or_cc"
    if any(d in domain for d in ["getty", "alamy", "shutterstock", "istockphoto"]):
        return "rights_reserved"
    if any(d in domain for d in ["unsplash", "pexels", "pixabay"]):
        return "free_license"
    return "unknown"


def build_search_queries(brief: dict) -> list:
    """Generate search queries from the brief."""
    label = brief["canonical_label"]
    target_type = brief["target_type"]
    queries = []

    if target_type == "architectural_anchor":
        queries = [
            f"{label} historical photos",
            f"{label} architecture exterior interior",
        ]
    elif target_type == "person_historical":
        queries = [
            f"{label} historical portrait",
            f"{label} biography photos",
        ]
    elif target_type == "location_historical":
        queries = [
            f"{label} historical photographs",
            f"{label} modern aerial view",
        ]
    elif target_type == "interior_space":
        queries = [
            f"{label} interior design photographs",
            f"{label} architecture interior details",
        ]
    elif target_type == "environment_reference":
        queries = [
            f"{label} visual reference photography",
        ]
    elif target_type == "object_artifact":
        queries = [
            f"{label} reference images",
            f"{label} historical artifact",
        ]
    elif target_type == "symbolic_sequence":
        queries = [
            f"{label} visual symbolism art",
        ]
    elif target_type == "event_reference":
        queries = [
            f"{label} historical documentation photos",
        ]
    else:
        queries = [f"{label} reference images"]

    return queries


def research_target(brief_path: Path, sector_root: Path) -> Path:
    """Run web research for a single target using Firecrawl.

    Reads the target brief, generates search queries, runs firecrawl,
    and builds a candidate_set artifact.

    Returns:
        Path to the written candidate_set.json.
    """
    brief = read_json(brief_path)
    tid = brief["target_id"]
    label = brief["canonical_label"]
    target_type = brief["target_type"]

    print(f"[research_worker] researching target: {tid} ({label})")

    queries = build_search_queries(brief)
    all_results = []
    worker_notes = []

    for query in queries:
        print(f"[research_worker] searching (Brave): {query}")
        results = _run_brave_search(query)
        if results:
            worker_notes.append(f"brave '{query}' -> {len(results)} results")
            all_results.extend(results)
        else:
            print(f"[research_worker] Brave returned 0, falling back to Firecrawl: {query}")
            results = _run_firecrawl_search(query)
            worker_notes.append(f"firecrawl '{query}' -> {len(results)} results")
            all_results.extend(results)

    # Deduplicate by URL
    seen_urls = set()
    unique_results = []
    for r in all_results:
        if r["url"] not in seen_urls:
            seen_urls.add(r["url"])
            unique_results.append(r)

    worker_notes.append(f"total unique results: {len(unique_results)}")

    # Build candidates
    candidates = []
    for idx, r in enumerate(unique_results, start=1):
        cid = f"c{idx:03d}"
        classification = _classify_result(r["title"], r["url"], r["snippet"], target_type)
        confidence = _estimate_confidence(r["title"], r["url"], label)
        licensing = _licensing_hint(r["url"])

        candidates.append({
            "candidate_id": cid,
            "source_url": r["url"],
            "page_title": r["title"],
            "source_domain": _extract_domain(r["url"]),
            "preliminary_classification": classification,
            "rationale": r["snippet"] if r["snippet"] else f"Found via search for '{label}'",
            "confidence": round(confidence, 2),
            "licensing_note": licensing,
            "acquisition_mode": "reference_only",
            "local_asset_path": None,
            "preview_path": None,
            "capture_path": None,
            "timestamp": utc_now(),
        })

    warnings = []
    if not candidates:
        warnings.append("no candidates found from any search query")

    candidate_set = {
        "contract_version": "s4.candidate_set.v1",
        "target_id": tid,
        "canonical_label": label,
        "target_type": target_type,
        "scene_ids": brief["scene_ids"],
        "candidates": candidates,
        "worker_notes": worker_notes,
        "warnings": warnings,
    }

    validate_artifact_strict(candidate_set, "candidate_set")

    out = candidate_set_path(sector_root, tid)
    write_json(out, candidate_set)
    print(f"[research_worker] wrote candidate_set: {out} ({len(candidates)} candidates)")
    return out


def main():
    if len(sys.argv) != 3:
        raise SystemExit("usage: research_worker.py <brief_path> <sector_root>")
    research_target(Path(sys.argv[1]), Path(sys.argv[2]))


if __name__ == "__main__":
    main()
