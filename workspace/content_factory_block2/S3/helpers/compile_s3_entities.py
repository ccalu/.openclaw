import json
import sys
from datetime import datetime, timezone
from pathlib import Path

OPERATORS = {
    "human_subject_extractor": "human_subjects",
    "environment_location_extractor": "environment_locations",
    "object_artifact_extractor": "object_artifacts",
    "symbolic_event_extractor": "symbolic_events",
}


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def main():
    if len(sys.argv) != 4:
        raise SystemExit("usage: compile_s3_entities.py <sector_root> <source_package_path> <output_path>")

    sector_root = Path(sys.argv[1])
    source_package_path = Path(sys.argv[2])
    output_path = Path(sys.argv[3])

    source_package = json.loads(source_package_path.read_text(encoding="utf-8"))
    compiled = {
        "sector": "s3_visual_planning",
        "contract_version": "s3.compiled_entities.v1",
        "job_id": source_package.get("job_id", "unknown_job"),
        "video_id": source_package.get("video_id", "unknown_video"),
        "account_id": source_package.get("account_id", "unknown_account"),
        "language": source_package.get("language", "unknown_language"),
        "status": "completed",
        "entity_focus": source_package.get("entity_focus", {}),
        "sources": {
            "source_package_path": str(source_package_path)
        },
        "operators": {},
        "compiled_entities": {
            "human_subjects": [],
            "environment_locations": [],
            "object_artifacts": [],
            "symbolic_events": []
        },
        "compile_notes": [],
        "warnings": [],
        "generated_at": utc_now()
    }

    for operator_name, bucket in OPERATORS.items():
        operator_output = sector_root / "operators" / operator_name / "output.json"
        if operator_output.exists():
            data = json.loads(operator_output.read_text(encoding="utf-8"))
            compiled["operators"][operator_name] = {
                "status": data.get("status", "completed"),
                "output_path": str(operator_output)
            }
            compiled["compiled_entities"][bucket] = data.get("entities", [])
        else:
            compiled["operators"][operator_name] = {
                "status": "missing",
                "output_path": str(operator_output)
            }
            compiled["warnings"].append(f"missing output for {operator_name}")

    if compiled["warnings"]:
        compiled["status"] = "degraded_completed"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(compiled, ensure_ascii=False, indent=2), encoding="utf-8")
    print(str(output_path))


if __name__ == "__main__":
    main()
