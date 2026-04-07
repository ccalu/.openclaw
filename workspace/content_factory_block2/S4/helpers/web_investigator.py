"""S4 Web Investigator -- creates target research briefs from intake."""
import sys
from pathlib import Path

from artifact_io import read_json, write_json
from dirs import create_target_directories
from paths import (
    target_root,
    target_brief_path,
    candidate_set_path,
)
from schema_validator import validate_artifact_strict

# Search goal templates by target_type
GOAL_TEMPLATES = {
    "architectural_anchor": [
        "Find historical photographs of '{label}'",
        "Find architectural plans and construction details for '{label}'",
        "Find Wikipedia or encyclopedia articles about '{label}'",
        "Find exterior and interior visual references of '{label}'",
    ],
    "person_historical": [
        "Find historical portraits or photographs of '{label}'",
        "Find biographical details and primary sources about '{label}'",
        "Find artistic depictions of '{label}'",
    ],
    "location_historical": [
        "Find historical and modern photographs of '{label}'",
        "Find maps and geographic context for '{label}'",
        "Find encyclopedia entries about '{label}'",
    ],
    "environment_reference": [
        "Find visual mood references for '{label}' environments",
        "Find atmosphere and lighting references for '{label}'",
    ],
    "interior_space": [
        "Find interior photographs and design references for '{label}'",
        "Find architectural details of '{label}' interiors",
    ],
    "object_artifact": [
        "Find reference images of '{label}'",
        "Find historical context and provenance of '{label}'",
    ],
    "symbolic_sequence": [
        "Find visual metaphors and symbolic imagery for '{label}'",
        "Find artistic interpretations of '{label}'",
    ],
    "event_reference": [
        "Find documentation and photographs of '{label}'",
        "Find historical accounts of '{label}'",
    ],
}


def build_brief(target: dict, intake: dict, manifest: dict, sector_root: Path) -> dict:
    """Build a target research brief for one target."""
    tid = target["target_id"]
    label = target["canonical_label"]
    ttype = target["target_type"]
    job_id = intake["metadata"]["job_id"]

    # Find batch_id
    batch_id = "batch_001"
    for batch in manifest.get("batches", []):
        if tid in batch.get("target_ids", []):
            batch_id = batch["batch_id"]
            break

    # Generate search goals
    templates = GOAL_TEMPLATES.get(ttype, GOAL_TEMPLATES["object_artifact"])
    search_goals = [t.format(label=label) for t in templates]

    # Create target directories
    tr = target_root(sector_root, tid)
    create_target_directories(tr)

    brief = {
        "contract_version": "s4.target_research_brief.v1",
        "job_id": job_id,
        "batch_id": batch_id,
        "target_id": tid,
        "canonical_label": label,
        "target_type": ttype,
        "scene_ids": target["scene_ids"],
        "research_modes": target["research_modes"],
        "priority": target["priority"],
        "search_goals": search_goals,
        "research_needs": target["research_needs"],
        "source_entity_ids": target["source_entity_ids"],
        "storage_paths": {
            "target_root": str(tr),
            "candidate_set_path": str(candidate_set_path(sector_root, tid)),
            "assets_dir": str(tr / "assets"),
            "previews_dir": str(tr / "previews"),
            "captures_dir": str(tr / "captures"),
        },
        "output_contract": "s4.candidate_set.v1",
        "notes": [],
        "warnings": [],
    }

    validate_artifact_strict(brief, "target_research_brief")

    out = target_brief_path(sector_root, tid)
    write_json(out, brief)
    print(f"[web_investigator] wrote brief: {out}")
    return brief


def build_all_briefs(intake_path_arg: Path, manifest_path: Path, sector_root: Path) -> list:
    """Build briefs for all targets in intake."""
    intake = read_json(intake_path_arg)
    manifest = read_json(manifest_path)
    briefs = []
    for target in intake["research_targets"]:
        brief = build_brief(target, intake, manifest, sector_root)
        briefs.append(brief)
    print(f"[web_investigator] built {len(briefs)} briefs")
    return briefs


def main():
    if len(sys.argv) != 4:
        raise SystemExit("usage: web_investigator.py <intake_path> <manifest_path> <sector_root>")
    build_all_briefs(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]))


if __name__ == "__main__":
    main()
