"""S4 Visual Evaluator — GPT-5.4-nano evaluates downloaded images in batches of 5.

Uses OpenAI API directly. Receives video_context for era/style coherence checks.
Rejects images from wrong era, toys/miniatures, anachronistic modern content.

For each target:
1. Reads images from targets/{tid}/candidates/
2. Splits into batches of 5
3. Sends each batch to GPT-5.4-nano with evaluation prompt + video context
4. relevance >= 7 → copy to assets/
5. relevance < 7 → delete
6. Writes asset_materialization_report.json
"""
import asyncio
import base64
import json
import shutil
import sys
from pathlib import Path

from openai import AsyncOpenAI

from artifact_io import read_json, write_json, utc_now
from paths import sanitize_target_id, asset_report_path

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"
MODEL = "gpt-5.4-nano"
EVAL_SEMAPHORE_LIMIT = 10
BATCH_SIZE = 5
RELEVANCE_THRESHOLD = 7


def _mime_for_ext(ext: str) -> str:
    ext = ext.lower()
    if ext in (".jpg", ".jpeg"):
        return "image/jpeg"
    if ext == ".png":
        return "image/png"
    if ext == ".webp":
        return "image/webp"
    if ext == ".gif":
        return "image/gif"
    return "image/jpeg"


def _build_context_block(video_context: dict) -> str:
    """Build the VIDEO CONTEXT coherence rules for the evaluator."""
    if not video_context or not video_context.get("title"):
        return ""

    parts = ["VIDEO CONTEXT (use this to judge coherence):"]
    if video_context.get("title"):
        parts.append(f"  Title: {video_context['title']}")
    if video_context.get("subject"):
        parts.append(f"  Subject: {video_context['subject']}")
    if video_context.get("era"):
        parts.append(f"  Era: {video_context['era']}")
    if video_context.get("style"):
        parts.append(f"  Style: {video_context['style']}")
    if video_context.get("visual_era_guidance"):
        parts.append(f"  Visual guidance: {video_context['visual_era_guidance']}")

    parts.append("")
    parts.append("COHERENCE RULES (based on video context):")
    parts.append("- If the target refers to a SPECIFIC place/building from the video,")
    parts.append("  generic similar places from elsewhere score LOWER (max 5-6, not 7+).")
    parts.append("- Reject images from clearly wrong era (e.g. modern minimalist architecture")
    parts.append("  when the video is about a 1940s art déco hotel).")
    parts.append("- Reject toys, miniatures, replicas, board game pieces — unless the target")
    parts.append("  explicitly asks for those.")
    parts.append("- For historical documentaries: prefer vintage/period photographs over")
    parts.append("  contemporary photos of the same subject.")
    parts.append("- An image of the ACTUAL specific place/building/person from the video")
    parts.append("  is worth much more than a generic similar one.")
    parts.append("")

    return "\n".join(parts)


def _write_reference_ready_sidecar(
    asset_path: Path,
    evaluation: dict,
    target_id: str,
    target_label: str,
    target_type: str,
) -> None:
    """Write a .reference_ready.json sidecar next to the approved asset."""
    candidate_id = asset_path.stem.split("_")[0]
    sidecar = {
        "asset_id": candidate_id,
        "source_target_id": target_id,
        "source_target_label": target_label,
        "source_target_type": target_type,
        "filepath": str(asset_path),
        "relevance": evaluation.get("relevance", 0),
        "quality": evaluation.get("quality", 0),
        "depicts": evaluation.get("depicts", ""),
        "depiction_type": evaluation.get("depiction_type", "mixed"),
        "reference_value": evaluation.get("reference_value", []),
        "preserve_if_used": evaluation.get("preserve_if_used", []),
        "reasoning_summary": evaluation.get("reasoning_summary", ""),
    }
    sidecar_path = asset_path.with_suffix(".reference_ready.json")
    write_json(sidecar_path, sidecar)


async def evaluate_target(
    target: dict,
    sector_root: Path,
    client: AsyncOpenAI,
    system_prompt: str,
    video_context: dict,
    tracker=None,
) -> dict:
    """Evaluate all candidate images for one target using GPT-5.4-nano vision."""
    tid = target["target_id"]
    stid = sanitize_target_id(tid)
    label = target["canonical_label"]
    target_type = target.get("target_type", "")

    candidates_dir = sector_root / "targets" / stid / "candidates"
    assets_dir = sector_root / "targets" / stid / "assets"

    if not candidates_dir.exists():
        print(f"[visual_eval] {tid}: no candidates/ dir, skipping")
        return _empty_report(tid, label)

    image_files = sorted([
        f for f in candidates_dir.iterdir()
        if f.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp", ".gif")
    ])

    if not image_files:
        print(f"[visual_eval] {tid}: no image files in candidates/, skipping")
        return _empty_report(tid, label)

    # Read brief for context
    brief_path = sector_root / "targets" / stid / f"{stid}_brief.json"
    if brief_path.exists():
        brief = read_json(brief_path)
        context = brief.get("research_needs", f"Documentary video about {label}")
        if isinstance(context, list):
            context = "; ".join(context)
    else:
        context = f"Documentary video requiring visual references for {label}"

    context_block = _build_context_block(video_context)

    assets_dir.mkdir(parents=True, exist_ok=True)
    all_entries = []
    approved_count = 0
    rejected_count = 0

    # Process in batches of 5
    for batch_start in range(0, len(image_files), BATCH_SIZE):
        batch_files = image_files[batch_start:batch_start + BATCH_SIZE]

        # Build content array with images as base64
        content_parts = [
            {"type": "text", "text": (
                f"{context_block}"
                f"Target: {label} ({target_type})\n"
                f"Context: {context}\n\n"
                f"I am showing you {len(batch_files)} candidate images for this target.\n"
                f"Evaluate each image (numbered 1 to {len(batch_files)}).\n\n"
                f"For each image, score relevance (1-10), quality (1-10), classify the type, "
                f"and explain your reasoning. relevance >= 7 means the image is approved for production.\n\n"
                f"Respond ONLY with valid JSON: {{\"evaluations\": [...], \"summary\": \"...\"}}"
            )}
        ]

        valid_files = []
        for img_file in batch_files:
            try:
                img_bytes = img_file.read_bytes()
                mime = _mime_for_ext(img_file.suffix)
                b64 = base64.b64encode(img_bytes).decode()
                content_parts.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:{mime};base64,{b64}"}
                })
                valid_files.append(img_file)
            except Exception:
                continue

        if not valid_files:
            continue

        try:
            resp = await client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": content_parts},
                ],
                temperature=0.1,
                max_completion_tokens=4096,
                response_format={"type": "json_object"},
            )
            if tracker:
                tracker.track(resp.usage)
            raw = resp.choices[0].message.content
            result = json.loads(raw)
        except Exception as e:
            print(f"[visual_eval] {tid}: batch {batch_start // BATCH_SIZE + 1} failed: {e}")
            for img_file in valid_files:
                all_entries.append({
                    "candidate_id": img_file.stem.split("_")[0],
                    "materialization_status": "failed",
                    "failure_reason": f"OpenAI call failed: {e}",
                    "relevance": 0,
                    "quality": 0,
                    "type": "unknown",
                    "reason": "",
                })
                rejected_count += 1
            continue

        evaluations = _parse_evaluations(result)

        for i, img_file in enumerate(valid_files):
            cid = img_file.stem.split("_")[0]

            if i < len(evaluations):
                ev = evaluations[i]
            else:
                ev = {}

            relevance = ev.get("relevance", 0)
            if isinstance(relevance, (int, float)):
                relevance = max(0, min(10, int(relevance)))
            else:
                relevance = 0
            quality = ev.get("quality", 0)
            if isinstance(quality, (int, float)):
                quality = max(0, min(10, int(quality)))
            else:
                quality = 0

            img_type = ev.get("type", "unknown")
            reason = ev.get("reason", "")

            if relevance >= RELEVANCE_THRESHOLD:
                dest = assets_dir / img_file.name
                shutil.copy2(img_file, dest)
                all_entries.append({
                    "candidate_id": cid,
                    "materialization_status": "downloaded",
                    "local_asset_path": str(dest),
                    "failure_reason": None,
                    "relevance": relevance,
                    "quality": quality,
                    "type": img_type,
                    "reason": reason,
                })

                # Write reference_ready sidecar for approved assets
                _write_reference_ready_sidecar(
                    dest, ev, tid, label, target_type,
                )
                approved_count += 1
            else:
                all_entries.append({
                    "candidate_id": cid,
                    "materialization_status": "skipped",
                    "local_asset_path": None,
                    "failure_reason": f"relevance={relevance} (below threshold {RELEVANCE_THRESHOLD})",
                    "relevance": relevance,
                    "quality": quality,
                    "type": img_type,
                    "reason": reason,
                })
                rejected_count += 1

        batch_num = batch_start // BATCH_SIZE + 1
        total_batches = (len(image_files) + BATCH_SIZE - 1) // BATCH_SIZE
        print(f"[visual_eval] {tid}: batch {batch_num}/{total_batches} done")

    # Clean up candidates/
    for f in candidates_dir.iterdir():
        try:
            f.unlink()
        except Exception:
            pass
    try:
        if candidates_dir.exists() and not any(candidates_dir.iterdir()):
            candidates_dir.rmdir()
    except Exception:
        pass

    report = {
        "contract_version": "s4.asset_materialization_report.v1",
        "target_id": tid,
        "job_id": "",
        "materialized_at": utc_now(),
        "entries": all_entries,
        "summary": {
            "total_candidates": len(image_files),
            "downloaded": approved_count,
            "skipped": rejected_count,
            "failed": 0,
        },
    }

    print(f"[visual_eval] {tid} ({label}): {approved_count} approved, {rejected_count} rejected out of {len(image_files)}")
    return report


def _parse_evaluations(result) -> list[dict]:
    """Parse OpenAI response into list of evaluation dicts."""
    if isinstance(result, list):
        return result
    if isinstance(result, dict):
        for key in ("evaluations", "images", "results"):
            if key in result and isinstance(result[key], list):
                return result[key]
    return []


def _empty_report(tid: str, label: str) -> dict:
    return {
        "contract_version": "s4.asset_materialization_report.v1",
        "target_id": tid,
        "job_id": "",
        "materialized_at": utc_now(),
        "entries": [],
        "summary": {
            "total_candidates": 0,
            "downloaded": 0,
            "skipped": 0,
            "failed": 0,
        },
    }


async def evaluate_all_targets(
    intake_path: Path,
    sector_root: Path,
    client: AsyncOpenAI,
    job_id: str,
    video_context: dict = None,
    tracker=None,
) -> None:
    """Evaluate images for all targets with Semaphore(10)."""
    sr = sector_root.resolve()
    intake = read_json(intake_path)
    all_targets = intake["research_targets"]
    targets = [t for t in all_targets if t.get("handling_mode") != "skip_visual_retrieval"]

    prompt_path = PROMPTS_DIR / "s4_visual_evaluator_batch_system.txt"
    system_prompt = prompt_path.read_text(encoding="utf-8")

    if video_context is None:
        video_context = {}

    semaphore = asyncio.Semaphore(EVAL_SEMAPHORE_LIMIT)
    total_approved = 0
    total_rejected = 0

    async def _eval_with_semaphore(target):
        async with semaphore:
            return await evaluate_target(target, sr, client, system_prompt, video_context, tracker)

    tasks = [_eval_with_semaphore(t) for t in targets]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    for target, result in zip(targets, results):
        tid = target["target_id"]
        stid = sanitize_target_id(tid)

        if isinstance(result, Exception):
            print(f"[visual_eval] {tid}: FAILED: {result}")
            result = _empty_report(tid, target["canonical_label"])

        result["job_id"] = job_id

        report_path = asset_report_path(sr, tid)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        write_json(report_path, result)

        s = result["summary"]
        total_approved += s["downloaded"]
        total_rejected += s["skipped"]

    print(f"[visual_eval] DONE: {total_approved} approved, {total_rejected} rejected across {len(targets)} targets")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise SystemExit("usage: s4_visual_evaluator.py <intake_path> <sector_root> <job_id>")
    client = AsyncOpenAI()
    asyncio.run(evaluate_all_targets(Path(sys.argv[1]), Path(sys.argv[2]), client, sys.argv[3]))
