from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

BASE = Path(r"C:\Users\User-OEM\.openclaw\workspace\task_watchdog")
CONFIG_PATH = BASE / "config.json"
ACTIVE_PATH = BASE / "active_tasks.json"
HISTORY_PATH = BASE / "task_history.jsonl"


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat()


def load_json(path: Path, default: Any):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def save_json_atomic(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def append_history(entry: Dict[str, Any]) -> None:
    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with HISTORY_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def format_human_dt(iso_str: Optional[str]) -> Optional[str]:
    if not iso_str:
        return None
    try:
        dt = datetime.fromisoformat(iso_str)
        return dt.strftime("%d/%m %H:%M")
    except Exception:
        return iso_str


def minutes_since(iso_str: Optional[str]) -> Optional[int]:
    if not iso_str:
        return None
    try:
        dt = datetime.fromisoformat(iso_str)
        delta = datetime.now(dt.tzinfo or timezone.utc) - dt
        return max(0, int(delta.total_seconds() // 60))
    except Exception:
        return None


def build_running_message(task: Dict[str, Any]) -> str:
    started = format_human_dt(task.get("startedAt"))
    elapsed = minutes_since(task.get("startedAt"))
    checked = format_human_dt(task.get("lastCheckedAt"))
    step = task.get("lastKnownStep") or "sem passo detalhado"
    model = task.get("model") or "modelo não registado"
    who = task.get("launcher") or "Tobias"
    return (
        f"Tarefa em andamento: {task.get('taskName', 'sem nome')}\n"
        f"Tipo: {task.get('type', 'desconhecido')}\n"
        f"Modelo: {model}\n"
        f"Lançada por: {who}\n"
        f"Iniciada: {started or 'desconhecido'}\n"
        f"Rodando há: {str(elapsed) + ' min' if elapsed is not None else 'desconhecido'}\n"
        f"Último passo conhecido: {step}\n"
        f"Última checagem: {checked or 'desconhecido'}"
    )


def build_finished_message(task: Dict[str, Any]) -> str:
    started = format_human_dt(task.get("startedAt"))
    ended = format_human_dt(task.get("endedAt"))
    elapsed = minutes_since(task.get("startedAt"))
    model = task.get("model") or "modelo não registado"
    result = task.get("resultSummary") or "sem resumo adicional"
    return (
        f"Tarefa finalizada: {task.get('taskName', 'sem nome')}\n"
        f"Modelo: {model}\n"
        f"Iniciada: {started or 'desconhecido'}\n"
        f"Encerrada: {ended or 'desconhecido'}\n"
        f"Duração observada: {str(elapsed) + ' min' if elapsed is not None else 'desconhecida'}\n"
        f"Resumo: {result}"
    )


def build_failed_message(task: Dict[str, Any]) -> str:
    started = format_human_dt(task.get("startedAt"))
    failed = format_human_dt(task.get("endedAt"))
    elapsed = minutes_since(task.get("startedAt"))
    model = task.get("model") or "modelo não registado"
    err = task.get("error") or "sem erro detalhado"
    step = task.get("lastKnownStep") or "passo desconhecido"
    return (
        f"Tarefa falhou: {task.get('taskName', 'sem nome')}\n"
        f"Modelo: {model}\n"
        f"Iniciada: {started or 'desconhecido'}\n"
        f"Falha detectada: {failed or 'desconhecido'}\n"
        f"Rodou por: {str(elapsed) + ' min' if elapsed is not None else 'desconhecido'}\n"
        f"Último passo conhecido: {step}\n"
        f"Erro: {err}"
    )


def evaluate_tasks(tasks: List[Dict[str, Any]], config: Dict[str, Any]) -> Dict[str, Any]:
    now = now_iso()
    notify_every = int(config.get("notifyEveryMinutes", 10))
    outputs: List[Dict[str, Any]] = []
    remaining: List[Dict[str, Any]] = []

    for task in tasks:
        task["lastCheckedAt"] = now
        status = task.get("status", "running")
        last_notified = task.get("lastNotifiedAt")
        mins = minutes_since(last_notified)

        if status in ("running", "spawned"):
            if last_notified is None or (mins is not None and mins >= notify_every):
                outputs.append({
                    "taskId": task.get("taskId"),
                    "kind": status,
                    "message": build_running_message(task),
                    "originChat": task.get("originChat"),
                })
                task["lastNotifiedAt"] = now
            remaining.append(task)
            continue

        if status == "stalled":
            if last_notified is None or (mins is not None and mins >= notify_every):
                elapsed = minutes_since(task.get("startedAt"))
                outputs.append({
                    "taskId": task.get("taskId"),
                    "kind": "stalled",
                    "message": (
                        f"⚠️ Tarefa possivelmente travada: {task.get('taskName', 'sem nome')}\n"
                        f"Rodando há: {str(elapsed) + ' min' if elapsed is not None else 'desconhecido'}\n"
                        f"Sem registo de runtime encontrado. Pode ter terminado silenciosamente."
                    ),
                    "originChat": task.get("originChat"),
                })
                task["lastNotifiedAt"] = now
            remaining.append(task)
            continue

        if status == "orphaned":
            # Already terminal: notify once then archive
            terminal_notified = task.get("terminalNotifiedStatus")
            if terminal_notified != "orphaned":
                task.setdefault("endedAt", now)
                outputs.append({
                    "taskId": task.get("taskId"),
                    "kind": "orphaned",
                    "message": (
                        f"🔴 Tarefa órfã (sem runtime): {task.get('taskName', 'sem nome')}\n"
                        f"Erro: {task.get('error', 'sessão não encontrada no runtime')}"
                    ),
                    "originChat": task.get("originChat"),
                })
                task["terminalNotifiedStatus"] = "orphaned"
                task["lastNotifiedAt"] = now
                append_history(task)
            continue

        if status == "completed":
            task.setdefault("endedAt", now)
            outputs.append({
                "taskId": task.get("taskId"),
                "kind": "completed",
                "message": build_finished_message(task),
                "originChat": task.get("originChat"),
            })
            append_history(task)
            continue

        if status == "failed":
            task.setdefault("endedAt", now)
            outputs.append({
                "taskId": task.get("taskId"),
                "kind": "failed",
                "message": build_failed_message(task),
                "originChat": task.get("originChat"),
            })
            append_history(task)
            continue

        remaining.append(task)

    return {"checkedAt": now, "notifications": outputs, "remaining": remaining}


def main() -> None:
    config = load_json(CONFIG_PATH, {})
    if not config.get("enabled", True):
        print(json.dumps({"enabled": False}, ensure_ascii=False))
        return

    tasks = load_json(ACTIVE_PATH, [])

    # --- Reconciliation pass (MVP) ---
    # Attempt to reconcile task status against runtime before evaluating.
    try:
        import sys as _sys
        _sys.path.insert(0, str(BASE.parent))
        from task_watchdog.reconciler import reconcile_all  # noqa: E402
        rec = reconcile_all(tasks, config)
        tasks = rec["remaining"]
        # Archive terminal tasks that were reconciled and already notified
        for entry in rec.get("archived", []):
            append_history(entry)
        # Emit reconciler notifications (these go directly to output)
        rec_notifications = rec.get("notifications", [])
    except Exception as _exc:
        rec_notifications = []
        # Reconciler failure is non-fatal — continue with raw registry
        import traceback as _tb
        _tb.print_exc()

    # --- Standard evaluate pass ---
    result = evaluate_tasks(tasks, config)

    # Merge reconciler notifications (prepend so they appear before periodic pings)
    all_notifications = rec_notifications + [
        n for n in result["notifications"]
        if n["taskId"] not in {r["taskId"] for r in rec_notifications}
    ]
    result["notifications"] = all_notifications
    result["reconcilerRan"] = True

    save_json_atomic(ACTIVE_PATH, result["remaining"])
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
