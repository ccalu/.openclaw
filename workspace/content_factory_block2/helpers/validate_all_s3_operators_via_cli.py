import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(r"C:\Users\User-OEM\.openclaw\workspace\content_factory_block2")
OPERATORS = [
    ("human_subject_extractor", "human_subject_output.schema.json"),
    ("environment_location_extractor", "environment_location_output.schema.json"),
    ("object_artifact_extractor", "object_artifact_output.schema.json"),
    ("symbolic_event_extractor", "symbolic_event_output.schema.json"),
]


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def run_py(script: Path, *args: str, check=True):
    cmd = [sys.executable, str(script), *args]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if check and result.returncode != 0:
        raise RuntimeError(f"script failed: {script}\nstdout={result.stdout}\nstderr={result.stderr}")
    return result


def write_json(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: validate_all_s3_operators_via_cli.py <run_root>")

    run_root = Path(sys.argv[1])
    b2_root = run_root / "b2"
    if run_root.exists():
        shutil.rmtree(run_root)
    run_root.mkdir(parents=True, exist_ok=True)

    screenplay = {
        "video_context": {"title": "All Operators Real Validation"},
        "script_overview": {"summary": "Validate one real run for each S3 operator via CLI primitive."},
        "scenes": [
            {"scene_id": "scene_001", "title": "Opening", "summary": "A king enters the palace wearing a crown."},
            {"scene_id": "scene_002", "title": "Storm", "summary": "Thunder over the city as banners wave."}
        ]
    }

    b2_bootstrap = {
        "kind": "b2_start",
        "contract_version": "b2.bootstrap.v1",
        "job_id": "all_ops_cli_001",
        "run_root": str(run_root),
        "b2_root": str(b2_root),
        "account_id": "006",
        "language": "pt-BR",
        "inputs": {
            "screenplay_analysis_path": str(run_root / "upstream" / "screenplay_analysis.json")
        },
        "mode": "s3_only"
    }

    write_json(run_root / "upstream" / "screenplay_analysis.json", screenplay)
    write_json(run_root / "b2_bootstrap.json", b2_bootstrap)

    run_py(BASE / "helpers" / "b2_state_helper.py", "bootstrap", str(b2_root), "s3_only")
    run_py(BASE / "helpers" / "build_s3_bootstrap_from_b2.py", str(run_root / "b2_bootstrap.json"), str(run_root))
    bootstrap_path = run_root / "s3_supervisor_bootstrap.json"
    bootstrap = json.loads(bootstrap_path.read_text(encoding="utf-8"))
    sector_root = Path(bootstrap["sector_root"])

    results = []
    for operator_name, schema_file in OPERATORS:
        run_py(BASE / "S3" / "helpers" / "build_operator_dispatches.py", str(bootstrap_path), operator_name)
        dispatch_path = Path(bootstrap["dispatch_dir"]) / f"{operator_name}_job.json"
        invoke = run_py(BASE / "S3" / "helpers" / "invoke_operator_via_cli.py", operator_name, str(dispatch_path), check=False)
        result_blob = {
            "operator_name": operator_name,
            "invoke_returncode": invoke.returncode,
            "invoke_stdout": invoke.stdout,
            "invoke_stderr": invoke.stderr,
            "validated": False,
            "output_exists": False,
            "validated_at": utc_now(),
        }
        output_path = sector_root / "operators" / operator_name / "output.json"
        if invoke.returncode == 0 and output_path.exists():
            result_blob["output_exists"] = True
            run_py(BASE / "S3" / "helpers" / "validate_operator_output.py", operator_name, str(output_path), str(BASE / "S3" / "schemas" / schema_file))
            result_blob["validated"] = True
        results.append(result_blob)

    summary = {
        "ok": all(r["validated"] for r in results),
        "run_root": str(run_root),
        "results": results,
    }
    write_json(run_root / "all_operator_validation_summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
