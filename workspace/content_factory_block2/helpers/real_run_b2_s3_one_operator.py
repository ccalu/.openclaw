import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

OPENCLAW_BIN = shutil.which("openclaw") or shutil.which("openclaw.cmd") or "openclaw.cmd"

BASE = Path(r"C:\Users\User-OEM\.openclaw\workspace\content_factory_block2")

OPERATOR_TO_AGENT = {
    "human_subject_extractor": "op_s3_human_subject_extractor",
    "environment_location_extractor": "op_s3_environment_location_extractor",
    "object_artifact_extractor": "op_s3_object_artifact_extractor",
    "symbolic_event_extractor": "op_s3_symbolic_event_extractor",
}

SCHEMA_MAP = {
    "human_subject_extractor": "human_subject_output.schema.json",
    "environment_location_extractor": "environment_location_output.schema.json",
    "object_artifact_extractor": "object_artifact_output.schema.json",
    "symbolic_event_extractor": "symbolic_event_output.schema.json",
}


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def write_json(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def run_py(script: Path, *args: str):
    cmd = [sys.executable, str(script), *args]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return result.stdout.strip()


def run_cmd(*args: str):
    result = subprocess.run(list(args), capture_output=True, text=True, check=True)
    return result.stdout.strip()


def invoke_operator(agent_id: str, dispatch_path: Path):
    message = (
        f"Execute o job descrito em {dispatch_path.as_posix()}. "
        "Leia esse dispatch do disco, confirme que o operator alvo és tu, use o source package referenciado, "
        "produza o output canónico em output.output_path, escreva também runtime.status_path e runtime.checkpoint_path, "
        "e termina apenas quando os ficheiros finais estiverem no disco. "
        "Não respondas com sucesso textual sem escrever os ficheiros."
    )
    return run_cmd(
        OPENCLAW_BIN, "agent",
        "--agent", agent_id,
        "--message", message,
        "--json",
    )


def main():
    if len(sys.argv) != 3:
        raise SystemExit("usage: real_run_b2_s3_one_operator.py <run_root> <operator_name>")

    run_root = Path(sys.argv[1])
    operator_name = sys.argv[2]
    if operator_name not in OPERATOR_TO_AGENT:
        raise SystemExit(f"unknown operator: {operator_name}")

    b2_root = run_root / "b2"
    if run_root.exists():
        shutil.rmtree(run_root)
    run_root.mkdir(parents=True, exist_ok=True)

    screenplay_analysis = {
        "language": "pt-BR",
        "total_scenes": 3,
        "video_context": {
            "title": "A Queda do Rei Sol",
            "description": "Resumo histórico sobre o fim do reinado de Luís XIV e a decadência da corte."
        },
        "scenes": [
            {
                "scene_id": "scene_001",
                "scene_number": 1,
                "text": "Luís XIV caminha pelos corredores de Versalhes enquanto cortesãos observam em silêncio."
            },
            {
                "scene_id": "scene_002",
                "scene_number": 2,
                "text": "Madame de Maintenon acompanha o rei durante uma cerimônia privada, enquanto membros da corte aguardam ao fundo."
            },
            {
                "scene_id": "scene_003",
                "scene_number": 3,
                "text": "Após a morte do rei, um grupo de nobres debate o futuro da França diante do vazio político."
            }
        ]
    }
    script_fetched = {
        "video_name": "a_queda_do_rei_sol",
        "data": {
            "title": "A Queda do Rei Sol",
            "description": "Resumo histórico sobre o fim do reinado de Luís XIV e a decadência da corte.",
            "words": 320,
            "row_number": 61
        }
    }

    write_json(run_root / "upstream" / "screenplay_analysis.json", screenplay_analysis)
    write_json(run_root / "upstream" / "01_script_fetched.json", script_fetched)

    b2_bootstrap = {
        "kind": "b2_start",
        "contract_version": "b2.bootstrap.v1",
        "job_id": f"realrun_{operator_name}_001",
        "video_id": "realcheck_video_001",
        "run_root": str(run_root),
        "b2_root": str(b2_root),
        "account_id": "006",
        "language": "pt-BR",
        "inputs": {
            "screenplay_analysis_path": str(run_root / "upstream" / "screenplay_analysis.json"),
            "script_fetched_checkpoint_path": str(run_root / "upstream" / "01_script_fetched.json")
        },
        "mode": "s3_only"
    }
    write_json(run_root / "b2_bootstrap.json", b2_bootstrap)

    run_py(BASE / "helpers" / "b2_state_helper.py", "bootstrap", str(b2_root), "s3_only")
    write_json(b2_root / "checkpoints" / "b2_bootstrap_ready.json", {
        "event": "b2_bootstrap_ready",
        "job_id": b2_bootstrap["job_id"],
        "created_at": utc_now()
    })
    write_json(b2_root / "checkpoints" / "s3_requested.json", {
        "event": "s3_requested",
        "job_id": b2_bootstrap["job_id"],
        "sector": "s3_visual_planning",
        "requested_at": utc_now(),
        "supervisor_agent_id": "sm_s3_visual_planning",
        "mode": "s3_only"
    })

    bootstrap_path = run_py(BASE / "helpers" / "build_s3_bootstrap_from_b2.py", str(run_root / "b2_bootstrap.json"), str(run_root))
    run_py(BASE / "S3" / "helpers" / "build_operator_dispatches.py", bootstrap_path, operator_name)

    dispatch_path = b2_root / "sectors" / "s3_visual_planning" / "dispatch" / f"{operator_name}_job.json"
    invoke_result = invoke_operator(OPERATOR_TO_AGENT[operator_name], dispatch_path)

    output_path = b2_root / "sectors" / "s3_visual_planning" / "operators" / operator_name / "output.json"
    run_py(
        BASE / "S3" / "helpers" / "validate_operator_output.py",
        operator_name,
        str(output_path),
        str(BASE / "S3" / "schemas" / SCHEMA_MAP[operator_name]),
    )

    sector_root = b2_root / "sectors" / "s3_visual_planning"
    compiled_path = sector_root / "compiled" / "compiled_entities.json"
    report_path = sector_root / "compiled" / "s3_sector_report.md"
    run_py(BASE / "S3" / "helpers" / "compile_s3_entities.py", str(sector_root), str(sector_root / "inputs" / "s3_source_package.json"), str(compiled_path))
    run_py(BASE / "S3" / "helpers" / "generate_s3_sector_report.py", str(compiled_path), str(report_path))

    compiled = json.loads(compiled_path.read_text(encoding="utf-8"))
    compiled_status = compiled.get("status")
    if compiled_status == "completed":
        checkpoint_path = run_py(BASE / "S3" / "helpers" / "emit_s3_b2_checkpoint.py", "completed", str(b2_root), b2_bootstrap["job_id"], str(sector_root))
        run_py(BASE / "helpers" / "b2_state_helper.py", "update", str(b2_root), "status=completed", "current_stage=s3", "last_event=s3_completed", "completed_stage=s3")
        write_json(b2_root / "checkpoints" / "b2_completed.json", {
            "event": "b2_completed",
            "job_id": b2_bootstrap["job_id"],
            "mode": "s3_only",
            "completed_at": utc_now(),
            "compiled_entities_path": str(compiled_path),
            "sector_report_path": str(report_path)
        })
    else:
        checkpoint_path = run_py(
            BASE / "S3" / "helpers" / "emit_s3_b2_checkpoint.py",
            "failed",
            str(b2_root),
            b2_bootstrap["job_id"],
            str(sector_root),
            f"compiled_status={compiled_status}",
        )
        run_py(BASE / "helpers" / "b2_state_helper.py", "update", str(b2_root), "status=failed", "current_stage=s3", f"last_event=s3_{compiled_status}", "failed_stage=s3")

    summary = {
        "ok": compiled_status == "completed",
        "run_root": str(run_root),
        "operator_name": operator_name,
        "agent_id": OPERATOR_TO_AGENT[operator_name],
        "dispatch_path": str(dispatch_path),
        "output_path": str(output_path),
        "compiled_entities_path": str(compiled_path),
        "sector_report_path": str(report_path),
        "compiled_status": compiled_status,
        "s3_checkpoint_path": checkpoint_path,
        "invoke_result": invoke_result,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
