from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

BASE = Path(r"C:\Users\User-OEM\.openclaw\workspace\task_watchdog")
ACTIVE_PATH = BASE / "active_tasks.json"
CONFIG_PATH = BASE / "config.json"


def load_json(path: Path, default: Any):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def summarize(tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
    by_status: Dict[str, int] = {}
    flagged = []
    for task in tasks:
        status = task.get("status", "unknown")
        by_status[status] = by_status.get(status, 0) + 1
        if status in {"stalled", "orphaned", "failed"}:
            flagged.append({
                "taskId": task.get("taskId"),
                "taskName": task.get("taskName"),
                "status": status,
                "statusReason": task.get("statusReason"),
                "lastKnownStep": task.get("lastKnownStep"),
            })
    return {
        "totalActive": len(tasks),
        "byStatus": by_status,
        "flagged": flagged,
    }


def main() -> None:
    config = load_json(CONFIG_PATH, {})
    tasks = load_json(ACTIVE_PATH, [])
    summary = summarize(tasks)
    summary["enabled"] = config.get("enabled", True)
    summary["notifyEveryMinutes"] = config.get("notifyEveryMinutes", 10)
    summary["stallMinutes"] = config.get("stallMinutes", 30)
    summary["orphanMinutes"] = config.get("orphanMinutes", 60)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
