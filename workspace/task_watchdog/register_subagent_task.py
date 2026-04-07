from __future__ import annotations

import json
import sys
from datetime import datetime, timezone

sys.path.append(r"C:\Users\User-OEM\.openclaw\workspace")
from task_watchdog.registry_helpers import register_task  # noqa: E402


def now_stamp() -> str:
    return datetime.now(timezone.utc).astimezone().strftime("%Y%m%d_%H%M%S")


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: register_subagent_task.py <json_payload>")

    payload = json.loads(sys.argv[1])
    task_id = payload.get("taskId") or f"task_{now_stamp()}"

    if not payload.get("childSessionKey"):
        raise SystemExit("register_subagent_task.py requires childSessionKey for subagent tasks")

    task = {
        "taskId": task_id,
        "taskName": payload["taskName"],
        "type": payload.get("type", "subagent"),
        "model": payload.get("model"),
        "originChat": payload.get("originChat"),
        "originSession": payload.get("originSession"),
        "replyTarget": payload.get("replyTarget", "current_chat"),
        "notifyEveryMinutes": payload.get("notifyEveryMinutes", 10),
        "status": payload.get("status", "running"),
        "childSessionKey": payload.get("childSessionKey"),
        "summaryHint": payload.get("summaryHint"),
        "lastKnownStep": payload.get("lastKnownStep", "spawned"),
        "launcher": payload.get("launcher", "Tobias")
    }

    out = register_task(task)
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
