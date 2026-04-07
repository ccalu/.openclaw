import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(r"C:\Users\User-OEM\.openclaw\workspace\content_factory_block2")


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
        raise SystemExit("usage: real_run_s3_supervisor_one_operator_cli.py <run_root>")

    run_root = Path(sys.argv[1])
    b2_root = run_root / "b2"
    if run_root.exists():
        shutil.rmtree(run_root)
    run_root.mkdir(parents=True, exist_ok=True)

    screenplay = {
        "video_context": {"title": "Supervisor CLI Narrow Run"},
        "script_overview": {"summary": "Narrow run for real supervisor->operator CLI path"},
        "scenes": [{"scene_id": "scene_001", "title": "Opening", "summary": "A palace scene with a king and a crown."}]
    }

    b2_bootstrap = {
        "kind": "b2_start",
        "contract_version": "b2.bootstrap.v1",
        "job_id": "real_supervisor_cli_001",
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
    write_json(b2_root / "checkpoints" / "b2_bootstrap_ready.json", {
        "event": "b2_bootstrap_ready",
        "job_id": b2_bootstrap["job_id"],
        "created_at": utc_now()
    })

    run_py(BASE / "helpers" / "build_s3_bootstrap_from_b2.py", str(run_root / "b2_bootstrap.json"), str(run_root))
    bootstrap_path = run_root / "s3_supervisor_bootstrap.json"

    bootstrap = json.loads(bootstrap_path.read_text(encoding="utf-8"))
    sector_root = Path(bootstrap["sector_root"])
    checkpoints_dir = Path(bootstrap["checkpoints_dir"])

    write_json(checkpoints_dir / "s3_supervisor_started.json", {
        "event": "s3_supervisor_started",
        "job_id": bootstrap["job_id"],
        "started_at": utc_now(),
        "bootstrap_path": str(bootstrap_path)
    })

    run_py(BASE / "S3" / "helpers" / "build_operator_dispatches.py", str(bootstrap_path), "human_subject_extractor")

    dispatch_path = Path(bootstrap["dispatch_dir"]) / "human_subject_extractor_job.json"
    invoke = run_py(BASE / "S3" / "helpers" / "invoke_operator_via_cli.py", "human_subject_extractor", str(dispatch_path), check=False)
    write_json(checkpoints_dir / "operator_cli_invoke_result.json", {
        "returncode": invoke.returncode,
        "stdout": invoke.stdout,
        "stderr": invoke.stderr,
        "captured_at": utc_now()
    })
    if invoke.returncode != 0:
        write_json(checkpoints_dir / "s3_final_checkpoint.json", {
            "status": "failed",
            "reason": "operator_cli_invoke_failed",
            "captured_at": utc_now()
        })
        raise RuntimeError(f"operator invocation failed\nstdout={invoke.stdout}\nstderr={invoke.stderr}")

    output_path = sector_root / "operators" / "human_subject_extractor" / "output.json"
    run_py(BASE / "S3" / "helpers" / "validate_operator_output.py", "human_subject_extractor", str(output_path), str(BASE / "S3" / "schemas" / "human_subject_output.schema.json"))

    compiled_path = sector_root / "compiled" / "compiled_entities.json"
    report_path = sector_root / "compiled" / "s3_sector_report.md"
    run_py(BASE / "S3" / "helpers" / "compile_s3_entities.py", str(sector_root), str(sector_root / "inputs" / "s3_source_package.json"), str(compiled_path))
    run_py(BASE / "S3" / "helpers" / "generate_s3_sector_report.py", str(compiled_path), str(report_path))

    compiled = json.loads(compiled_path.read_text(encoding="utf-8"))
    status = compiled.get("status")
    write_json(checkpoints_dir / "s3_final_checkpoint.json", {
        "status": status,
        "compiled_entities_path": str(compiled_path),
        "sector_report_path": str(report_path),
        "captured_at": utc_now(),
        "primitive": "exec + openclaw agent --agent ... --json"
    })

    print(json.dumps({
        "ok": True,
        "run_root": str(run_root),
        "status": status,
        "compiled_entities": str(compiled_path),
        "report": str(report_path)
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
