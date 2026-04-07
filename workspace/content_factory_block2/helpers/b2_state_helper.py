import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def bootstrap_state(b2_root: Path, mode: str):
    state = {
        "block": "b2",
        "mode": mode,
        "status": "running",
        "current_stage": "s3",
        "completed_stages": [],
        "failed_stages": [],
        "next_stage": None,
        "last_event": "bootstrap_ready",
        "last_updated_at": utc_now(),
    }
    write_json(b2_root / "state" / "b2_state.json", state)
    return state


def update_state(b2_root: Path, *, status=None, current_stage=None, last_event=None, completed_stage=None, failed_stage=None):
    path = b2_root / "state" / "b2_state.json"
    state = json.loads(path.read_text(encoding="utf-8"))

    if status is not None:
        state["status"] = status
    if current_stage is not None:
        state["current_stage"] = current_stage
    if last_event is not None:
        state["last_event"] = last_event
    if completed_stage and completed_stage not in state["completed_stages"]:
        state["completed_stages"].append(completed_stage)
    if failed_stage and failed_stage not in state["failed_stages"]:
        state["failed_stages"].append(failed_stage)

    state["last_updated_at"] = utc_now()
    write_json(path, state)
    return state


def main():
    if len(sys.argv) < 3:
        raise SystemExit("usage: b2_state_helper.py <bootstrap|update> <b2_root> [args...]")

    command = sys.argv[1]
    b2_root = Path(sys.argv[2])
    ensure_dir(b2_root / "state")
    ensure_dir(b2_root / "checkpoints")
    ensure_dir(b2_root / "logs")
    ensure_dir(b2_root / "sectors")

    if command == "bootstrap":
        mode = sys.argv[3] if len(sys.argv) > 3 else "s3_only"
        state = bootstrap_state(b2_root, mode)
        print(json.dumps(state, ensure_ascii=False))
        return

    if command == "update":
        kwargs = {}
        for raw in sys.argv[3:]:
            key, value = raw.split("=", 1)
            kwargs[key] = value
        state = update_state(
            b2_root,
            status=kwargs.get("status"),
            current_stage=kwargs.get("current_stage"),
            last_event=kwargs.get("last_event"),
            completed_stage=kwargs.get("completed_stage"),
            failed_stage=kwargs.get("failed_stage"),
        )
        print(json.dumps(state, ensure_ascii=False))
        return

    raise SystemExit(f"unknown command: {command}")


if __name__ == "__main__":
    main()
