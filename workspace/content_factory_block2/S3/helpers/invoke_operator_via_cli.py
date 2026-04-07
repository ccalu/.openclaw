import json
import shutil
import subprocess
import sys
from pathlib import Path

REGISTRY = {
    "human_subject_extractor": "op_s3_human_subject_extractor",
    "environment_location_extractor": "op_s3_environment_location_extractor",
    "object_artifact_extractor": "op_s3_object_artifact_extractor",
    "symbolic_event_extractor": "op_s3_symbolic_event_extractor",
}


def main():
    if len(sys.argv) != 3:
        raise SystemExit("usage: invoke_operator_via_cli.py <operator_name> <dispatch_path>")

    operator_name = sys.argv[1]
    dispatch_path = Path(sys.argv[2])
    if operator_name not in REGISTRY:
        raise SystemExit(f"unknown operator_name: {operator_name}")
    if not dispatch_path.exists():
        raise SystemExit(f"dispatch file not found: {dispatch_path}")

    agent_id = REGISTRY[operator_name]
    message = (
        f"Execute o job descrito em '{dispatch_path}'. "
        "Leia o payload do disco, use source_package.path como base do vídeo, "
        "escreva o output final em output.output_path, actualize runtime.checkpoint_path e runtime.status_path, "
        "e termine apenas quando o ficheiro final estiver persistido ou a falha explícita tiver sido registada."
    )

    openclaw_bin = shutil.which("openclaw") or shutil.which("openclaw.cmd") or shutil.which("openclaw.exe")
    if not openclaw_bin:
        raise SystemExit("openclaw executable not found in PATH")

    command = [
        openclaw_bin,
        "agent",
        "--agent",
        agent_id,
        "--message",
        message,
        "--json",
    ]

    result = subprocess.run(command, capture_output=True, text=True)
    payload = {
        "ok": result.returncode == 0,
        "operator_name": operator_name,
        "agent_id": agent_id,
        "dispatch_path": str(dispatch_path),
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
