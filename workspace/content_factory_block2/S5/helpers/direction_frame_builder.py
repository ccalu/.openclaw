"""S5 Direction Frame Builder — produce the global video direction frame.

Reads video_context, compiled_entities, and source_package to produce
a single video_direction_frame.json that constrains all scene-kit design.

Usage:
    python direction_frame_builder.py <video_context> <compiled_entities> <source_package> <sector_root> <job_id>
"""
import asyncio
import json
import sys
from pathlib import Path

from artifact_io import read_json, write_json, utc_now
from llm_client import create_client, call_llm, UsageTracker
from paths import direction_frame_path, usage_path
from schema_validator import validate_artifact_strict


async def build_direction_frame(
    video_context_path: str,
    compiled_entities_path: str,
    source_package_path: str,
    sector_root: str,
    job_id: str,
) -> None:
    sr = Path(sector_root).resolve()

    # Load upstream
    print("[direction_frame] loading upstream artifacts...")
    video_ctx = read_json(Path(video_context_path))
    compiled_ent = read_json(Path(compiled_entities_path))
    source_pkg = read_json(Path(source_package_path))

    # Build entity landscape summary
    categories = compiled_ent.get("compiled_entities", {})
    entity_summary = {}
    for cat_name, entities in categories.items():
        entity_summary[cat_name] = [
            e.get("canonical_label") or e.get("name", "unknown")
            for e in entities[:10]
        ]

    scenes = source_pkg.get("scenes", [])
    video_id = source_pkg.get("video_id") or source_pkg.get("job_id", job_id)

    # Build user content for LLM
    user_payload = {
        "video_id": video_id,
        "video_context": video_ctx,
        "entity_landscape": entity_summary,
        "total_scenes": len(scenes),
        "first_scene_text": scenes[0].get("text", "")[:500] if scenes else "",
        "last_scene_text": scenes[-1].get("text", "")[:500] if scenes else "",
    }

    # Load system prompt
    prompt_path = Path(__file__).parent.parent / "prompts" / "direction_frame_builder.txt"
    system_prompt = prompt_path.read_text(encoding="utf-8")

    # Call LLM
    client = create_client()
    tracker = UsageTracker()

    print("[direction_frame] calling MiniMax for direction frame...")
    frame = await call_llm(
        client,
        system_prompt,
        json.dumps(user_payload, ensure_ascii=False),
        tracker=tracker,
        max_tokens=2000,
    )

    # Inject fixed fields that should not be LLM-decided
    frame["frame_version"] = "v1"
    frame["video_id"] = video_id
    frame["motion_policy"] = "first_10_scenes_only"
    frame["allowed_generation_modes"] = [
        "reference_guided_generation",
        "regeneration_from_reference",
        "from_scratch_generation",
        "multi_reference_synthesis",
    ]
    frame["generated_at"] = utc_now()

    # Validate
    validate_artifact_strict(frame, "video_direction_frame")
    print(f"[direction_frame] frame valid: era={frame.get('dominant_visual_era')}, "
          f"style={frame.get('dominant_style_mode')}, grounding={frame.get('grounding_baseline')}")

    # Write
    out_path = direction_frame_path(sr)
    write_json(out_path, frame)

    # Update usage
    existing_usage = {}
    up = usage_path(sr)
    if up.exists():
        existing_usage = read_json(up)
    existing_usage["direction_frame"] = {
        "usage": tracker.summary(),
        "timestamp": utc_now(),
    }
    write_json(up, existing_usage)

    print(f"[direction_frame] DONE: frame written to {out_path}")


def main():
    if len(sys.argv) != 6:
        raise SystemExit(
            "usage: direction_frame_builder.py <video_context> <compiled_entities> "
            "<source_package> <sector_root> <job_id>"
        )
    asyncio.run(build_direction_frame(*sys.argv[1:]))


if __name__ == "__main__":
    main()
