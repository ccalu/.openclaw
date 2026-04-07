import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(r"C:\Users\User-OEM\.openclaw\workspace\content_factory_block2")


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def run_py(script: Path, *args: str):
    cmd = [sys.executable, str(script), *args]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return result.stdout.strip()


def write_json(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: dry_run_b2_s3_only.py <run_root>")

    run_root = Path(sys.argv[1])
    b2_root = run_root / "b2"
    if run_root.exists():
        shutil.rmtree(run_root)
    run_root.mkdir(parents=True, exist_ok=True)

    b2_bootstrap = {
        "kind": "b2_start",
        "contract_version": "b2.bootstrap.v1",
        "job_id": "dryrun_job_001",
        "run_root": str(run_root),
        "b2_root": str(b2_root),
        "account_id": "006",
        "language": "pt-BR",
        "inputs": {
            "screenplay_analysis_path": str(run_root / "upstream" / "screenplay_analysis.json")
        },
        "mode": "s3_only"
    }

    write_json(run_root / "b2_bootstrap.json", b2_bootstrap)
    write_json(run_root / "upstream" / "screenplay_analysis.json", {
        "video_context": {"title": "Dry Run Video"},
        "script_overview": {"summary": "Dry run summary"},
        "scenes": [{"scene_id": "scene_001", "summary": "A test scene"}]
    })

    run_py(BASE / "helpers" / "b2_state_helper.py", "bootstrap", str(b2_root), "s3_only")

    write_json(b2_root / "checkpoints" / "b2_bootstrap_ready.json", {
        "event": "b2_bootstrap_ready",
        "job_id": "dryrun_job_001",
        "created_at": utc_now()
    })
    write_json(b2_root / "checkpoints" / "s3_requested.json", {
        "event": "s3_requested",
        "job_id": "dryrun_job_001",
        "sector": "s3_visual_planning",
        "requested_at": utc_now(),
        "supervisor_agent_id": "sm_s3_visual_planning",
        "mode": "s3_only"
    })

    run_py(BASE / "helpers" / "build_s3_bootstrap_from_b2.py", str(run_root / "b2_bootstrap.json"), str(run_root))

    sector_root = b2_root / "sectors" / "s3_visual_planning"
    fake_outputs = {
        "human_subject_extractor": [{"entity_id": "h1", "entity_type": "person", "canonical_label": "Luís XIV", "scene_ids": ["scene_001"], "visual_relevance_note": "main figure"}],
        "environment_location_extractor": [{"entity_id": "e1", "entity_type": "specific_place", "canonical_label": "Palácio", "scene_ids": ["scene_001"], "visual_relevance_note": "main location"}],
        "object_artifact_extractor": [{"entity_id": "o1", "entity_type": "artifact", "canonical_label": "Coroa", "scene_ids": ["scene_001"], "visual_relevance_note": "symbol of power"}],
        "symbolic_event_extractor": [{"entity_id": "s1", "entity_type": "symbol", "canonical_label": "Decadência", "scene_ids": ["scene_001"], "visual_relevance_note": "atmospheric motif"}]
    }

    schema_map = {
        "human_subject_extractor": "human_subject_output.schema.json",
        "environment_location_extractor": "environment_location_output.schema.json",
        "object_artifact_extractor": "object_artifact_output.schema.json",
        "symbolic_event_extractor": "symbolic_event_output.schema.json"
    }
    version_map = {
        "human_subject_extractor": "s3.human_subject.output.v1",
        "environment_location_extractor": "s3.environment_location.output.v1",
        "object_artifact_extractor": "s3.object_artifact.output.v1",
        "symbolic_event_extractor": "s3.symbolic_event.output.v1"
    }

    for operator_name, entities in fake_outputs.items():
        op_dir = sector_root / "operators" / operator_name
        output_path = op_dir / "output.json"
        write_json(output_path, {
            "contract_version": version_map[operator_name],
            "operator_name": operator_name,
            "job_id": "dryrun_job_001",
            "video_id": "dryrun_job_001",
            "account_id": "006",
            "language": "pt-BR",
            "status": "completed",
            "entities": entities,
            "generated_at": utc_now()
        })
        write_json(op_dir / "status.json", {"status": "completed", "updated_at": utc_now()})
        write_json(op_dir / "checkpoint.json", {"event": "operator_completed", "operator_name": operator_name, "updated_at": utc_now()})
        run_py(BASE / "S3" / "helpers" / "validate_operator_output.py", operator_name, str(output_path), str(BASE / "S3" / "schemas" / schema_map[operator_name]))

    compiled_path = sector_root / "compiled" / "compiled_entities.json"
    report_path = sector_root / "compiled" / "s3_sector_report.md"

    run_py(BASE / "S3" / "helpers" / "compile_s3_entities.py", str(sector_root), str(sector_root / "inputs" / "s3_source_package.json"), str(compiled_path))
    run_py(BASE / "S3" / "helpers" / "generate_s3_sector_report.py", str(compiled_path), str(report_path))

    write_json(b2_root / "checkpoints" / "s3_completed.json", {
        "event": "s3_completed",
        "job_id": "dryrun_job_001",
        "sector": "s3_visual_planning",
        "compiled_entities_path": str(compiled_path),
        "sector_report_path": str(report_path),
        "completed_at": utc_now(),
        "status": "completed"
    })

    run_py(BASE / "helpers" / "b2_state_helper.py", "update", str(b2_root), "status=completed", "current_stage=s3", "last_event=s3_completed", "completed_stage=s3")

    write_json(b2_root / "checkpoints" / "b2_completed.json", {
        "event": "b2_completed",
        "job_id": "dryrun_job_001",
        "mode": "s3_only",
        "completed_at": utc_now(),
        "compiled_entities_path": str(compiled_path),
        "sector_report_path": str(report_path)
    })

    print(json.dumps({
        "ok": True,
        "run_root": str(run_root),
        "b2_completed": str(b2_root / "checkpoints" / "b2_completed.json"),
        "compiled_entities": str(compiled_path),
        "sector_report": str(report_path)
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
