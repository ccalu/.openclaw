from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

BASE = Path(r"C:\Users\User-OEM\.openclaw\workspace\task_watchdog")
ACTIVE_PATH = BASE / "active_tasks.json"
HISTORY_PATH = BASE / "task_history.jsonl"


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat()


def load_active() -> List[Dict[str, Any]]:
    if not ACTIVE_PATH.exists():
        return []
    try:
        return json.loads(ACTIVE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return []


def save_active(tasks: List[Dict[str, Any]]) -> None:
    ACTIVE_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = ACTIVE_PATH.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(tasks, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(ACTIVE_PATH)


def append_history(entry: Dict[str, Any]) -> None:
    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with HISTORY_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def register_task(task: Dict[str, Any]) -> Dict[str, Any]:
    task_type = task.get("type", "subagent")
    if task_type == "subagent" and not task.get("childSessionKey"):
        raise ValueError("Subagent tasks require childSessionKey for reliable reconciliation.")

    tasks = load_active()
    task.setdefault("startedAt", now_iso())
    task.setdefault("lastCheckedAt", None)
    task.setdefault("lastNotifiedAt", None)
    task.setdefault("notifyEveryMinutes", 10)
    task.setdefault("status", "running")
    task.setdefault("launcher", "Tobias")
    tasks.append(task)
    save_active(tasks)
    return task


def update_task(task_id: str, **fields: Any) -> Optional[Dict[str, Any]]:
    tasks = load_active()
    updated = None
    for task in tasks:
        if task.get("taskId") == task_id:
            task.update(fields)
            updated = task
            break
    save_active(tasks)
    return updated


def finish_task(task_id: str, status: str = "completed", result_summary: Optional[str] = None, error: Optional[str] = None) -> Optional[Dict[str, Any]]:
    tasks = load_active()
    remaining = []
    finished = None
    for task in tasks:
        if task.get("taskId") == task_id:
            task["status"] = status
            task["endedAt"] = now_iso()
            if result_summary is not None:
                task["resultSummary"] = result_summary
            if error is not None:
                task["error"] = error
            finished = task
            append_history(task)
        else:
            remaining.append(task)
    save_active(remaining)
    return finished
