import json
import sys
from datetime import datetime, timezone
from pathlib import Path

OPERATORS = {
    "human_subject_extractor": {
        "schema": "s3.human_subject.output.v1",
        "families": ["characters", "human_figures", "groups", "factions", "crowds"],
        "payload": {
            "target_families": ["characters", "human_figures", "groups", "factions", "crowds"],
            "identity_resolution": "high",
            "include_aliases": True,
            "group_detection": True,
            "specificity_bias": "account_driven"
        }
    },
    "environment_location_extractor": {
        "schema": "s3.environment_location.output.v1",
        "families": ["locations", "places", "environments", "settings"],
        "payload": {
            "target_families": ["locations", "places", "environments", "settings"],
            "specific_location_bias": "account_driven",
            "include_architectural_context": True,
            "merge_nearby_variants": True,
            "specificity_bias": "account_driven"
        }
    },
    "object_artifact_extractor": {
        "schema": "s3.object_artifact.output.v1",
        "families": ["objects", "props", "artifacts", "vehicles", "machines", "animals", "documents", "maps", "interfaces"],
        "payload": {
            "target_families": ["objects", "props", "artifacts", "vehicles", "machines", "animals", "documents", "maps", "interfaces"],
            "historical_specificity_bias": "account_driven",
            "include_functional_objects": True,
            "merge_duplicate_mentions": True,
            "specificity_bias": "account_driven"
        }
    },
    "symbolic_event_extractor": {
        "schema": "s3.symbolic_event.output.v1",
        "families": ["symbols", "motifs", "abstract_visual_concepts", "natural_phenomena", "weather", "disasters", "event_visual_entities"],
        "payload": {
            "target_families": ["symbols", "motifs", "abstract_visual_concepts", "natural_phenomena", "weather", "disasters", "event_visual_entities"],
            "allow_non_literal_translation": True,
            "event_detection": True,
            "atmospheric_relevance_bias": "account_driven",
            "specificity_bias": "account_driven"
        }
    }
}


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def write_json(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    if len(sys.argv) not in {2, 3}:
        raise SystemExit("usage: build_operator_dispatches.py <s3_supervisor_bootstrap_path> [operator_name|all]")

    bootstrap_path = Path(sys.argv[1])
    selected = sys.argv[2] if len(sys.argv) == 3 else "all"
    bootstrap = json.loads(bootstrap_path.read_text(encoding="utf-8"))
    source_package = json.loads(Path(bootstrap["source_package_path"]).read_text(encoding="utf-8"))
    dispatch_dir = Path(bootstrap["dispatch_dir"])
    operators_dir = Path(bootstrap["operators_dir"])

    active_operator_names = list(OPERATORS.keys()) if selected == "all" else [selected]
    invalid = [name for name in active_operator_names if name not in OPERATORS]
    if invalid:
        raise SystemExit(f"unknown operator(s): {invalid}")

    activation_plan = {
        "contract_version": "s3.operator_activation_plan.v1",
        "job_id": bootstrap["job_id"],
        "active_operators": active_operator_names,
        "inactive_operators": [name for name in OPERATORS.keys() if name not in active_operator_names],
        "generated_at": utc_now(),
        "strategy": "all_4_active_for_v1" if selected == "all" else f"single_operator:{selected}"
    }
    write_json(Path(bootstrap["sector_root"]) / "checkpoints" / "operator_activation_plan.json", activation_plan)

    for idx, operator_name in enumerate(active_operator_names, start=1):
        config = OPERATORS[operator_name]
        payload = {
            "contract_version": "s3.operator_dispatch.v1",
            "workflow_run_id": bootstrap["job_id"],
            "sector_run_id": f"{bootstrap['job_id']}_s3",
            "supervisor_run_id": f"{bootstrap['job_id']}_s3_supervisor",
            "operator_run_id": f"{bootstrap['job_id']}_{operator_name}_{idx}",
            "operator_name": operator_name,
            "job_id": bootstrap["job_id"],
            "video_id": bootstrap["video_id"],
            "account_id": bootstrap["account_id"],
            "channel_id": bootstrap["account_id"],
            "project_id": "content_factory_block2",
            "language": bootstrap["language"],
            "entity_focus": {
                "families": config["families"],
                "priority_mode": source_package.get("entity_focus", {}).get("priority_mode", "strict_precision"),
                "coverage_mode": source_package.get("entity_focus", {}).get("coverage_mode", "balanced")
            },
            "source_package": {
                "path": bootstrap["source_package_path"],
                "format": "s3_source_package.v1"
            },
            "analysis_scope": {
                "scene_ids": [],
                "full_video": True
            },
            "account_rules": {
                "precision_profile": "strict_specificity",
                "priority_entities": [],
                "salience_threshold": "high",
                "notes": "v1 narrow run"
            },
            "output": {
                "output_path": str(operators_dir / operator_name / "output.json"),
                "expected_schema": config["schema"],
                "write_mode": "replace"
            },
            "runtime": {
                "checkpoint_path": str(operators_dir / operator_name / "checkpoint.json"),
                "status_path": str(operators_dir / operator_name / "status.json"),
                "log_path": str(operators_dir / operator_name / "log.md")
            },
            "execution_policy": {
                "max_attempt": 1,
                "timeout_seconds": 900,
                "failure_mode": "explicit",
                "partial_output_allowed": False
            },
            "operator_payload": config["payload"]
        }
        write_json(dispatch_dir / f"{operator_name}_job.json", payload)

    print(str(dispatch_dir))


if __name__ == "__main__":
    main()
