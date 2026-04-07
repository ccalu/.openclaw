"""S5 Scene Kit Designer — produce per-scene kit specs via MiniMax.

Reads all scene_direction_input_packages and the video_direction_frame,
then generates a scene_kit_spec for each scene using MiniMax M2.7-HS.

Production-safe: runs up to MAX_WAVES retry waves for failed scenes.
Each wave only processes scenes that don't have a valid spec on disk yet.

Usage:
    python scene_kit_designer.py <sector_root> <job_id>
"""
import asyncio
import json
import sys
from pathlib import Path

from artifact_io import read_json, write_json, utc_now
from llm_client import create_client, call_llm, UsageTracker
from paths import direction_frame_path, scene_kit_spec_path, usage_path
from schema_validator import validate_artifact

MAX_WAVES = 3  # total attempts (1 main + 2 retries)


def _auto_fix_spec(spec: dict, pkg: dict) -> dict:
    """Fix common LLM output issues before schema validation."""
    # Inject sequence_position if missing
    core = spec.get("scene_core", {})
    if "sequence_position" not in core:
        core["sequence_position"] = pkg.get("scene_core", {}).get("sequence_position", 0)
        spec["scene_core"] = core

    # Fix invalid family fields
    for fam in spec.get("asset_families", []):
        ft = fam.get("family_type", "")
        if ft not in ("hero", "support", "detail", "atmospheric", "transition", "fallback"):
            fam["family_type"] = "atmospheric"

        # Filter null/invalid reference_inputs
        refs = fam.get("reference_inputs", [])
        fam["reference_inputs"] = [
            r for r in refs
            if isinstance(r, dict) and r.get("asset_id") and r.get("source_target_id")
        ]

        # Ensure array fields exist
        for arr_key in ("preserve_requirements", "avoid_literal_copy_notes", "preferred_generation_modes"):
            val = fam.get(arr_key)
            if val is None:
                fam[arr_key] = []
            elif isinstance(val, str):
                fam[arr_key] = [val]

    # Fix delivery_expectations items that are strings instead of arrays
    de = spec.get("delivery_expectations", {})
    for key in ("minimum_viable_delivery", "preferred_enrichment"):
        val = de.get(key)
        if isinstance(val, str):
            de[key] = [val]
        elif val is None:
            de[key] = []

    # Ensure min 1 family
    if len(spec.get("asset_families", [])) < 1:
        spec["asset_families"] = [{
            "family_id": "f_fallback",
            "family_type": "fallback",
            "family_intent": "Minimum viable atmospheric asset for scene continuity",
            "priority": "required",
            "target_asset_count": {"minimum": 1, "ideal": 1, "maximum": 1},
            "grounding_strength": "low",
            "creative_freedom_level": "open",
            "preferred_generation_modes": ["from_scratch_generation"],
            "reference_inputs": [],
            "preserve_requirements": [],
            "avoid_literal_copy_notes": [],
            "editorial_notes": "Auto-injected fallback",
        }]

    return spec


async def design_all_kits(sector_root: str, job_id: str) -> None:
    sr = Path(sector_root).resolve()

    # Load direction frame
    frame_path = direction_frame_path(sr)
    if not frame_path.exists():
        raise FileNotFoundError(f"Direction frame not found: {frame_path}")
    frame = read_json(frame_path)

    # List all input packages
    pkg_dir = sr / "scene_direction_input_packages"
    pkg_files = sorted(pkg_dir.glob("*.json"))
    if not pkg_files:
        raise FileNotFoundError(f"No input packages found in {pkg_dir}")
    print(f"[scene_kit_designer] {len(pkg_files)} input packages to process")

    # Load system prompt
    prompt_path = Path(__file__).parent.parent / "prompts" / "scene_kit_designer.txt"
    system_prompt = prompt_path.read_text(encoding="utf-8")

    # Create client
    client = create_client()
    tracker = UsageTracker()
    all_errors = []

    semaphore = asyncio.Semaphore(10)

    async def _process_scene(pkg_file: Path) -> tuple[str, bool, str]:
        """Process one scene. Returns (scene_id, success, error_msg)."""
        pkg = read_json(pkg_file)
        sid = pkg["scene_id"]

        user_payload = {
            "video_direction_frame": frame,
            "scene_input_package": pkg,
        }
        user_content = json.dumps(user_payload, ensure_ascii=False)

        async with semaphore:
            try:
                spec = await call_llm(client, system_prompt, user_content, tracker=tracker)

                spec["spec_version"] = "v1"
                spec["scene_id"] = sid
                spec = _auto_fix_spec(spec, pkg)

                valid, errs = validate_artifact(spec, "scene_kit_spec")
                if not valid:
                    return (sid, False, f"schema: {errs[0][:200]}")

                out_path = scene_kit_spec_path(sr, sid)
                write_json(out_path, spec)
                return (sid, True, "")

            except Exception as e:
                return (sid, False, str(e)[:200])

    # --- Retry waves ---
    for wave in range(1, MAX_WAVES + 1):
        # Check which specs still missing
        existing = {f.stem for f in (sr / "scene_kit_specs").glob("*.json")} if (sr / "scene_kit_specs").exists() else set()
        pending = [f for f in pkg_files if f.stem not in existing]

        if not pending:
            print(f"[scene_kit_designer] wave {wave}: all {len(pkg_files)} specs complete")
            break

        print(f"[scene_kit_designer] wave {wave}/{MAX_WAVES}: {len(pending)} scenes to process "
              f"({len(existing)} already done)")

        results = await asyncio.gather(*[_process_scene(pf) for pf in pending])

        wave_ok = sum(1 for _, ok, _ in results if ok)
        wave_fail = sum(1 for _, ok, _ in results if not ok)
        wave_errors = [(sid, err) for sid, ok, err in results if not ok]

        print(f"[scene_kit_designer] wave {wave}: {wave_ok} succeeded, {wave_fail} failed")
        for sid, err in wave_errors:
            print(f"[scene_kit_designer]   {sid}: {err[:120]}")
            all_errors.append({"scene_id": sid, "error": err, "wave": wave})

        if wave_fail == 0:
            break

    # Final count
    final_specs = list((sr / "scene_kit_specs").glob("*.json"))
    total_succeeded = len(final_specs)
    total_failed = len(pkg_files) - total_succeeded

    # Update usage
    existing_usage = {}
    up = usage_path(sr)
    if up.exists():
        existing_usage = read_json(up)
    existing_usage["scene_kit_designer"] = {
        "usage": tracker.summary(),
        "succeeded": total_succeeded,
        "failed": total_failed,
        "waves_used": wave,
        "timestamp": utc_now(),
    }
    if all_errors:
        existing_usage["scene_kit_designer"]["errors"] = all_errors[-20:]
    write_json(up, existing_usage)

    print(f"[scene_kit_designer] DONE: {total_succeeded}/{len(pkg_files)} specs, "
          f"{total_failed} failed after {wave} waves, "
          f"{tracker.summary()['calls']} LLM calls")

    if total_failed > 0:
        print(f"[scene_kit_designer] WARNING: {total_failed} scenes remain without specs")


def main():
    if len(sys.argv) != 3:
        raise SystemExit("usage: scene_kit_designer.py <sector_root> <job_id>")
    asyncio.run(design_all_kits(*sys.argv[1:]))


if __name__ == "__main__":
    main()
