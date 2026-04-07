# DEPRECATED — This file is no longer part of the active S4 pipeline.
# Replaced by the V3 asset_pipeline (s4_query_generator + s4_image_collector + s4_visual_evaluator).
# Retained temporarily for reference. See S4_ARCHITECTURE_V2.md for current architecture.
"""S4 Visual Evaluator — Gemini Vision via KMS evaluates downloaded images.

Replaces the textual candidate_evaluator. This evaluator actually SEES
each image and judges relevance, quality, and usability for the target.

Uses GeminiClient from dataset_system with KMS cascade:
  Gemini 3 Flash → 3.1 Flash Lite → 2.5 Flash (free)
  → same sequence on tier1 → OpenRouter (paid)
"""
import asyncio
import base64
import json
import shutil
import sys
from pathlib import Path

from artifact_io import read_json, write_json, utc_now
from paths import sanitize_target_id
from schema_validator import validate_artifact_strict

# KMS imports — path to dataset_system (need both root and shared for imports)
DATASET_ROOT = Path(r"C:\Users\User-OEM\Desktop\content-factory\dataset_system")
DATASET_SHARED = DATASET_ROOT / "shared"
sys.path.insert(0, str(DATASET_ROOT))
sys.path.insert(0, str(DATASET_SHARED))
sys.path.insert(0, str(DATASET_SHARED / "clients"))

EVAL_SEMAPHORE_LIMIT = 3  # max parallel target evaluations (limited by Gemini RPM per key)
KMS_URL = "https://web-production-0a8dd.up.railway.app"
KMS_MACHINE_ID = "M1"
MODEL_GROUP = "dataset_collect"  # reuse existing model group with Gemini cascade

SYSTEM_PROMPT = """You are a visual asset evaluator for a documentary video production pipeline.
You receive a batch of candidate images for a specific visual target (person, building, landscape, object, etc.).
Your job is to evaluate each image and decide which ones are good enough for production use.

Respond ONLY in valid JSON format."""

USER_PROMPT_TEMPLATE = """Target: {label} ({target_type})
Context: {context}

I am showing you {count} candidate images for this target.
For each image (numbered 1 to {count}), evaluate:

Respond as a JSON object:
{{
  "evaluations": [
    {{
      "image_index": 1,
      "relevance": 8,
      "quality": 7,
      "type": "photograph",
      "reason": "Clear historical photo of the target building"
    }}
  ],
  "summary": "Brief summary of what was found and what's missing"
}}

Rules:
- relevance: 1-10 (how well does this image represent the target? 7+ means it's aligned and useful)
- quality: 1-10 (resolution, composition, clarity)
- type: "photograph" | "illustration" | "stock_generic" | "logo" | "map" | "irrelevant" | "photograph_watermarked"
- Be strict: generic stock photos, logos, maps, and completely irrelevant images should get relevance below 7
- If an image has a watermark but is otherwise good and relevant, mark it as "photograph_watermarked" and still give it the relevance it deserves
- If NONE of the images are relevant to the target, give all of them relevance below 7 — that is an honest and valid result
"""


async def evaluate_target(
    target: dict,
    sector_root: Path,
    gemini_client,
    context: str = "",
) -> dict:
    """Evaluate all candidate images for one target.

    Sends all images to Gemini Vision in a single call.
    Moves approved images from candidates/ to assets/.
    Returns materialization report.
    """
    tid = target["target_id"]
    stid = sanitize_target_id(tid)
    label = target["canonical_label"]
    target_type = target.get("target_type", "")

    candidates_dir = sector_root / "targets" / stid / "candidates"
    assets_dir = sector_root / "targets" / stid / "assets"

    if not candidates_dir.exists():
        print(f"[visual_eval] {tid}: no candidates/ dir, skipping")
        return _empty_report(tid, label)

    # Collect candidate images
    image_files = sorted([
        f for f in candidates_dir.iterdir()
        if f.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp", ".gif")
    ])

    if not image_files:
        print(f"[visual_eval] {tid}: no image files in candidates/, skipping")
        return _empty_report(tid, label)

    # Build image batch for Gemini
    images_data = []
    for img_file in image_files:
        try:
            img_bytes = img_file.read_bytes()
            mime = "image/jpeg"
            if img_file.suffix.lower() == ".png":
                mime = "image/png"
            elif img_file.suffix.lower() == ".webp":
                mime = "image/webp"
            images_data.append((img_bytes, mime))
        except Exception:
            continue

    if not images_data:
        print(f"[visual_eval] {tid}: could not read any images, skipping")
        return _empty_report(tid, label)

    # Call Gemini Vision with all images
    user_prompt = USER_PROMPT_TEMPLATE.format(
        label=label,
        target_type=target_type,
        context=context or f"Documentary video requiring visual references for {label}",
        count=len(images_data),
    )

    try:
        result = await gemini_client.generate_with_images(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            images=images_data,
            temperature=0.1,
            max_output_tokens=4096,
        )
    except Exception as e:
        print(f"[visual_eval] {tid}: Gemini call failed: {e}")
        return _empty_report(tid, label)

    # Parse result
    evaluations = result.get("evaluations", [])
    summary = result.get("summary", "")

    # Move approved images (relevance >= 7) to assets/, delete the rest
    assets_dir.mkdir(parents=True, exist_ok=True)
    entries = []
    approved_count = 0
    rejected_count = 0

    for eval_item in evaluations:
        idx = eval_item.get("image_index", 0)
        if idx < 1 or idx > len(image_files):
            continue

        img_file = image_files[idx - 1]
        cid = img_file.stem.split("_")[0]  # e.g. "c001" from "c001_candidate.jpg"
        relevance = eval_item.get("relevance", 0)
        quality = eval_item.get("quality", 0)

        if relevance >= 7:
            # Approved — move to assets/
            dest = assets_dir / img_file.name
            shutil.copy2(img_file, dest)
            entries.append({
                "candidate_id": cid,
                "image_index": idx,
                "materialization_status": "downloaded",
                "acquisition_mode": "direct_download",
                "local_asset_path": str(dest),
                "capture_path": None,
                "failure_reason": None,
                "relevance": relevance,
                "quality": quality,
                "type": eval_item.get("type", "unknown"),
                "reason": eval_item.get("reason", ""),
            })
            approved_count += 1
        else:
            # Rejected — will be deleted
            entries.append({
                "candidate_id": cid,
                "image_index": idx,
                "materialization_status": "skipped",
                "acquisition_mode": "reference_only",
                "local_asset_path": None,
                "capture_path": None,
                "failure_reason": f"relevance={relevance} (below threshold 7)",
                "relevance": relevance,
                "quality": quality,
                "type": eval_item.get("type", "unknown"),
                "reason": eval_item.get("reason", ""),
            })
            rejected_count += 1

    # Delete all candidates (approved ones already copied to assets/)
    for f in candidates_dir.iterdir():
        f.unlink()
    if candidates_dir.exists() and not any(candidates_dir.iterdir()):
        candidates_dir.rmdir()

    report = {
        "contract_version": "s4.asset_materialization_report.v1",
        "target_id": tid,
        "job_id": "",  # filled by caller
        "materialized_at": utc_now(),
        "entries": entries,
        "summary": {
            "total_best_candidates": approved_count,
            "downloaded": approved_count,
            "page_records": 0,
            "skipped": rejected_count,
            "failed": 0,
        },
        "visual_summary": summary,
    }

    print(f"[visual_eval] {tid} ({label}): {approved_count} approved, {rejected_count} rejected")
    return report


def _empty_report(tid: str, label: str) -> dict:
    return {
        "contract_version": "s4.asset_materialization_report.v1",
        "target_id": tid,
        "job_id": "",
        "materialized_at": utc_now(),
        "entries": [],
        "summary": {
            "total_best_candidates": 0,
            "downloaded": 0,
            "page_records": 0,
            "skipped": 0,
            "failed": 0,
        },
        "visual_summary": f"No candidate images available for {label}",
    }


async def evaluate_all_targets(
    intake_path: Path,
    sector_root: Path,
    job_id: str,
) -> None:
    """Evaluate images for all targets using Gemini Vision via KMS."""
    from kms_client_sync import KmsSyncClient
    from gemini_client import GeminiClient

    sr = sector_root.resolve()
    intake = read_json(intake_path)
    targets = intake["research_targets"]

    kms_context = {
        "account_code": intake["metadata"].get("account_id", ""),
        "language": intake["metadata"].get("language", ""),
        "system_name": "s4_asset_research",
        "video_title": intake["metadata"].get("video_id", ""),
    }

    semaphore = asyncio.Semaphore(EVAL_SEMAPHORE_LIMIT)
    total_approved = 0
    total_rejected = 0

    def _create_gemini():
        """Create a fresh KMS client + GeminiClient per call to avoid key collision."""
        kms = KmsSyncClient(base_url=KMS_URL, machine_id=KMS_MACHINE_ID)
        gemini = GeminiClient(kms_client=kms, model_group=MODEL_GROUP)
        gemini._kms_context = kms_context
        return gemini

    async def _eval_with_semaphore(target):
        async with semaphore:
            gemini = _create_gemini()
            return await evaluate_target(target, sr, gemini)

    # Run evaluations in parallel — each gets its own KMS client + key
    tasks = [_eval_with_semaphore(t) for t in targets]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    for target, result in zip(targets, results):
        tid = target["target_id"]
        stid = sanitize_target_id(tid)

        if isinstance(result, Exception):
            print(f"[visual_eval] {tid}: FAILED with exception: {result}")
            result = _empty_report(tid, target["canonical_label"])

        # Set job_id
        result["job_id"] = job_id

        # Write report
        report_path = sr / "targets" / stid / f"{stid}_asset_materialization_report.json"
        write_json(report_path, result)

        s = result["summary"]
        total_approved += s["downloaded"]
        total_rejected += s["skipped"]

    print(f"[visual_eval] DONE: {total_approved} approved, {total_rejected} rejected across {len(targets)} targets")


def run_evaluations(intake_path: Path, sector_root: Path, job_id: str) -> None:
    """Synchronous wrapper."""
    asyncio.run(evaluate_all_targets(intake_path, sector_root, job_id))


if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise SystemExit("usage: visual_evaluator.py <intake_path> <sector_root> <job_id>")
    run_evaluations(Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3])
