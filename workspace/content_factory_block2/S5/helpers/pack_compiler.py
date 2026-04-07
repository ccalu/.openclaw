"""S5 Pack Compiler — compile scene kit specs into s5_scene_kit_pack.json.

Deterministic. No LLM calls. Reads all scene_kit_specs and the direction frame,
builds the compiled pack and sector report.

Usage:
    python pack_compiler.py <sector_root> <job_id> <video_id> <account_id> <language>
"""
import sys
from pathlib import Path

from artifact_io import read_json, write_json, write_markdown, utc_now
from paths import (
    direction_frame_path,
    scene_kit_pack_path,
    sector_report_path,
)
from schema_validator import validate_artifact_strict


def compile_pack(sector_root: str, job_id: str, video_id: str, account_id: str, language: str) -> None:
    sr = Path(sector_root).resolve()

    # Load direction frame
    frame_path = direction_frame_path(sr)
    if not frame_path.exists():
        raise FileNotFoundError(f"Direction frame not found: {frame_path}")
    frame = read_json(frame_path)

    # List all scene kit specs
    specs_dir = sr / "scene_kit_specs"
    spec_files = sorted(specs_dir.glob("*.json"))
    print(f"[pack_compiler] found {len(spec_files)} scene kit specs")

    # Count input packages for total scene count
    pkg_dir = sr / "scene_direction_input_packages"
    pkg_files = sorted(pkg_dir.glob("*.json"))
    scene_count_total = len(pkg_files)

    # Build scenes list
    scenes = []
    warnings = []
    incomplete = []
    family_type_dist: dict[str, int] = {}

    for spec_file in spec_files:
        try:
            spec = read_json(spec_file)
            sid = spec.get("scene_id", spec_file.stem)
            core = spec.get("scene_core", {})
            families = spec.get("asset_families", [])

            for fam in families:
                ft = fam.get("family_type", "unknown")
                family_type_dist[ft] = family_type_dist.get(ft, 0) + 1

            scenes.append({
                "scene_id": sid,
                "sequence_position": core.get("sequence_position", 0),
                "scene_summary": core.get("scene_summary", ""),
                "narrative_function": core.get("narrative_function", ""),
                "family_count": len(families),
                "scene_kit_spec_ref": f"scene_kit_specs/{spec_file.name}",
                "status": "ready",
            })
        except Exception as e:
            sid = spec_file.stem
            warnings.append(f"Failed to read spec {sid}: {e}")
            scenes.append({
                "scene_id": sid,
                "sequence_position": 0,
                "status": "invalid",
                "notes": str(e)[:200],
            })
            incomplete.append(sid)

    # Sort by sequence_position
    scenes.sort(key=lambda s: s.get("sequence_position", 0))

    ready_count = sum(1 for s in scenes if s["status"] == "ready")
    ready_for_s6 = ready_count == scene_count_total and scene_count_total > 0

    # Check for missing scenes (in packages but not in specs)
    spec_scene_ids = {s["scene_id"] for s in scenes}
    for pkg_file in pkg_files:
        pkg = read_json(pkg_file)
        sid = pkg.get("scene_id", pkg_file.stem)
        if sid not in spec_scene_ids:
            warnings.append(f"Scene {sid} has input package but no spec")
            scenes.append({
                "scene_id": sid,
                "sequence_position": 0,
                "status": "missing",
            })
            incomplete.append(sid)

    # Build pack
    pack = {
        "pack_version": "v1",
        "sector": "s5_scene_kit_design",
        "video_id": video_id,
        "run_id": job_id,
        "generated_at": utc_now(),
        "status": "completed" if ready_for_s6 else "partial",
        "scene_count_total": scene_count_total,
        "scene_count_included": ready_count,
        "ready_for_s6": ready_for_s6,
        "video_direction_frame": frame,
        "video_direction_frame_ref": "compiled/video_direction_frame.json",
        "scenes": scenes,
        "warnings": warnings,
        "incomplete_scenes": incomplete,
        "handoff_notes": [],
    }

    # Validate and write pack
    validate_artifact_strict(pack, "s5_scene_kit_pack")
    out_path = scene_kit_pack_path(sr)
    write_json(out_path, pack)
    print(f"[pack_compiler] pack written: {ready_count}/{scene_count_total} ready, "
          f"ready_for_s6={ready_for_s6}")

    # Write sector report
    total_families = sum(s.get("family_count", 0) for s in scenes if s["status"] == "ready")
    avg_families = total_families / ready_count if ready_count else 0

    report = f"""# S5 Scene Kit Design — Sector Report

**Video**: {video_id}
**Account**: {account_id} | **Language**: {language}
**Job**: {job_id}
**Generated**: {utc_now()}

## Summary

| Metric | Value |
|--------|-------|
| Total scenes | {scene_count_total} |
| Specs generated | {ready_count} |
| Ready for S6 | {'Yes' if ready_for_s6 else 'No'} |
| Total families | {total_families} |
| Avg families/scene | {avg_families:.1f} |

## Family Type Distribution

| Type | Count |
|------|-------|
"""
    for ft, count in sorted(family_type_dist.items(), key=lambda x: -x[1]):
        report += f"| {ft} | {count} |\n"

    if warnings:
        report += "\n## Warnings\n\n"
        for w in warnings:
            report += f"- {w}\n"

    if incomplete:
        report += f"\n## Incomplete Scenes ({len(incomplete)})\n\n"
        for sid in incomplete:
            report += f"- {sid}\n"

    report_path = sector_report_path(sr)
    write_markdown(report_path, report)
    print(f"[pack_compiler] report written: {report_path}")


def main():
    if len(sys.argv) != 6:
        raise SystemExit("usage: pack_compiler.py <sector_root> <job_id> <video_id> <account_id> <language>")
    compile_pack(*sys.argv[1:])


if __name__ == "__main__":
    main()
