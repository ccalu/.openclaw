"""S4 Coverage Analyst -- determines target and scene coverage using heuristics.

Reads asset_materialization_report.json (new format) as the source of truth.
Falls back to evaluated_candidate_set.json (legacy) if the new report is absent.
"""
import sys
from pathlib import Path

from artifact_io import read_json, write_json, utc_now
from paths import (
    asset_report_path,
    evaluated_set_path,
    coverage_report_path,
    sanitize_target_id,
)
from schema_validator import validate_artifact_strict

# Coverage state priority (worst to best) for aggregation
COVERAGE_PRIORITY = {
    "unresolved": 0,
    "inspiration_only": 1,
    "partially_covered": 2,
    "covered": 3,
}


def _assess_target_coverage_new(report: dict, target_dir: Path) -> tuple:
    """Assess coverage from asset_materialization_report.json.

    Returns:
        (coverage_state, supporting_ids, notes)
    """
    entries = report.get("entries", [])
    summary = report.get("summary", {})
    downloaded = summary.get("downloaded", 0)

    # Also count actual files in assets/ as ground truth
    assets_dir = target_dir / "assets"
    actual_assets = 0
    if assets_dir.exists():
        actual_assets = len([
            f for f in assets_dir.iterdir()
            if f.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp", ".gif")
        ])

    asset_count = max(downloaded, actual_assets)

    if asset_count == 0:
        return "unresolved", [], f"0 assets (report: {downloaded} downloaded, disk: {actual_assets} files)"

    supporting = [
        e["candidate_id"] for e in entries
        if e.get("materialization_status") == "downloaded"
    ]

    if asset_count >= 3:
        state = "covered"
        note = f"{asset_count} assets approved"
    elif asset_count >= 1:
        state = "partially_covered"
        note = f"only {asset_count} asset(s) approved"
    else:
        state = "unresolved"
        note = "no assets"

    return state, supporting, note


def _assess_target_coverage_legacy(evaluated_set: dict) -> tuple:
    """Assess coverage from evaluated_candidate_set.json (legacy format).

    Returns:
        (coverage_state, supporting_candidate_ids, notes)
    """
    evaluated = evaluated_set.get("evaluated_candidates", [])

    if not evaluated:
        return "unresolved", [], "no candidates evaluated"

    classifications = set()
    supporting = []

    for ev in evaluated:
        if ev["final_classification"] == "reject":
            continue
        supporting.append(ev["candidate_id"])
        if ev["is_best_candidate"]:
            classifications.add(ev["final_classification"])

    if not classifications:
        for ev in evaluated:
            if ev["final_classification"] != "reject":
                classifications.add(ev["final_classification"])

    if not classifications:
        return "unresolved", [], "all candidates rejected"

    has_factual = "factual_evidence" in classifications
    has_visual = "visual_reference" in classifications
    has_stylistic = "stylistic_inspiration" in classifications

    if has_factual and has_visual:
        state = "covered"
        note = "factual_evidence + visual_reference found"
    elif has_factual or has_visual:
        state = "partially_covered"
        parts = [c for c in ["factual_evidence", "visual_reference"] if c in classifications]
        note = f"only {' + '.join(parts)} found"
    elif has_stylistic:
        state = "inspiration_only"
        note = "only stylistic_inspiration found"
    else:
        state = "partially_covered"
        note = f"classifications: {', '.join(sorted(classifications))}"

    return state, supporting, note


def _worst_coverage(states: list) -> str:
    """Return the worst coverage state from a list."""
    if not states:
        return "unresolved"
    return min(states, key=lambda s: COVERAGE_PRIORITY.get(s, 0))


def analyze_coverage(intake_path_arg: Path, sector_root: Path) -> Path:
    """Analyze coverage across all targets and scenes.

    Prefers asset_materialization_report.json (new pipeline).
    Falls back to evaluated_candidate_set.json (legacy pipeline).
    """
    intake = read_json(intake_path_arg)
    targets = intake["research_targets"]
    scene_index = intake["scene_index"]
    job_id = intake["metadata"]["job_id"]
    video_id = intake["metadata"]["video_id"]

    print(f"[coverage_analyst] analyzing coverage for {len(targets)} targets, {len(scene_index)} scenes")

    # Evaluate each target
    target_coverage = []
    target_state_map = {}

    for target in targets:
        tid = target["target_id"]
        stid = sanitize_target_id(tid)
        target_dir = sector_root / "targets" / stid

        # Try new format first
        new_report_path = asset_report_path(sector_root, tid)
        if new_report_path.exists():
            report = read_json(new_report_path)
            state, supporting, note = _assess_target_coverage_new(report, target_dir)
        else:
            # Fall back to legacy format
            eval_path = evaluated_set_path(sector_root, tid)
            try:
                evaluated_set = read_json(eval_path)
                state, supporting, note = _assess_target_coverage_legacy(evaluated_set)
            except FileNotFoundError:
                state = "unresolved"
                supporting = []
                note = "no materialization report or evaluated set found"

        target_state_map[tid] = state
        target_coverage.append({
            "target_id": tid,
            "coverage_state": state,
            "supporting_candidate_ids": supporting,
            "notes": note,
        })

    # Derive scene coverage from linked targets
    scene_coverage = []
    for scene in scene_index:
        sid = scene["scene_id"]
        linked = scene["linked_target_ids"]

        if not linked:
            scene_coverage.append({
                "scene_id": sid,
                "coverage_state": "unresolved",
                "linked_target_ids": linked,
                "notes": "no linked targets",
            })
            continue

        linked_states = [target_state_map.get(tid, "unresolved") for tid in linked]
        scene_state = _worst_coverage(linked_states)

        scene_coverage.append({
            "scene_id": sid,
            "coverage_state": scene_state,
            "linked_target_ids": linked,
            "notes": f"derived from {len(linked)} target(s): {', '.join(linked_states)}",
        })

    # Collect unresolved gaps
    unresolved_gaps = []
    for tc in target_coverage:
        if tc["coverage_state"] in ("unresolved", "inspiration_only"):
            unresolved_gaps.append(
                f"target {tc['target_id']}: {tc['coverage_state']} - {tc['notes']}"
            )
    for sc in scene_coverage:
        if sc["coverage_state"] == "unresolved":
            unresolved_gaps.append(
                f"scene {sc['scene_id']}: unresolved - {sc['notes']}"
            )

    warnings = []
    covered_count = sum(1 for tc in target_coverage if tc["coverage_state"] == "covered")
    partially = sum(1 for tc in target_coverage if tc["coverage_state"] == "partially_covered")
    unresolved = sum(1 for tc in target_coverage if tc["coverage_state"] == "unresolved")

    if covered_count == 0:
        warnings.append("no targets fully covered")

    report = {
        "contract_version": "s4.coverage_report.v1",
        "metadata": {
            "job_id": job_id,
            "video_id": video_id,
            "sector": "s4_asset_research",
            "generated_at": utc_now(),
        },
        "target_coverage": target_coverage,
        "scene_coverage": scene_coverage,
        "unresolved_gaps": unresolved_gaps,
        "warnings": warnings,
    }

    validate_artifact_strict(report, "coverage_report")

    out = coverage_report_path(sector_root)
    write_json(out, report)
    print(f"[coverage_analyst] wrote coverage report: {out}")
    print(f"[coverage_analyst] targets: {covered_count} covered, {partially} partially, {unresolved} unresolved")
    return out


def main():
    if len(sys.argv) != 3:
        raise SystemExit("usage: coverage_analyst.py <intake_path> <sector_root>")
    analyze_coverage(Path(sys.argv[1]), Path(sys.argv[2]))


if __name__ == "__main__":
    main()
