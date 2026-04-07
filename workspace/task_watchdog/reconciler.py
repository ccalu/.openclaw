"""
reconciler.py — MVP reconciler for task_watchdog.

Checks each active task against the real runtime state (subagents/runs.json)
and transitions tasks to accurate statuses:

  spawned   → task registered but not yet started (startedAt not set)
  running   → runtime confirms session is active (no endedAt in runs)
  stalled   → running but no runtime record found + over stall threshold
  completed → runtime confirmed ok/complete
  failed    → runtime confirmed error/timeout
  orphaned  → childSessionKey present but no matching run in runtime at all,
               AND task has been "running" long enough to be suspicious

Prevents duplicate notifications by checking lastNotifiedAt + deduplication.
Does NOT invent external infra. Reads only local files.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

BASE = Path(r"C:\Users\User-OEM\.openclaw\workspace\task_watchdog")
RUNS_PATH = Path(r"C:\Users\User-OEM\.openclaw\subagents\runs.json")

DEFAULT_STALL_MINUTES = 30
DEFAULT_ORPHAN_MINUTES = 60


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat()


def minutes_since(iso_str: Optional[str]) -> Optional[int]:
    if not iso_str:
        return None
    try:
        dt = datetime.fromisoformat(iso_str)
        delta = datetime.now(dt.tzinfo or timezone.utc) - dt
        return max(0, int(delta.total_seconds() // 60))
    except Exception:
        return None


def load_runs() -> Dict[str, Any]:
    """Load runs.json from the runtime. Returns the runs dict or {} on failure."""
    if not RUNS_PATH.exists():
        return {}
    try:
        data = json.loads(RUNS_PATH.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            # Format: {"version": 1, "runs": {...}}
            if "runs" in data and isinstance(data["runs"], dict):
                return data["runs"]
            # Flat dict of runs keyed by runId
            return data
        return {}
    except Exception:
        return {}


def find_run_for_session(session_key: str, runs: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Find the run entry matching a childSessionKey."""
    if not session_key:
        return None
    for run in runs.values():
        if isinstance(run, dict) and run.get("childSessionKey") == session_key:
            return run
    return None


def classify_run(run: Dict[str, Any]) -> str:
    """
    Given a run entry, return the canonical outcome status.
    Returns: 'completed', 'failed', 'running', 'unknown'
    """
    if run.get("endedAt"):
        outcome = run.get("outcome", {})
        status = outcome.get("status", "") if isinstance(outcome, dict) else str(outcome)
        ended_reason = run.get("endedReason", "")
        if status == "ok" or ended_reason == "subagent-complete":
            return "completed"
        # timeout, error, killed, etc.
        return "failed"
    # No endedAt → still running (or never started)
    if run.get("startedAt"):
        return "running"
    return "unknown"


def reconcile_task(task: Dict[str, Any], runs: Dict[str, Any], now: str, stall_minutes: int, orphan_minutes: int) -> Tuple[Dict[str, Any], Optional[str]]:
    """
    Reconcile a single task against runtime state.

    Returns:
        (updated_task, terminal_status_or_None)
        terminal_status is 'completed', 'failed', 'orphaned', or None (task stays active)
    """
    session_key = task.get("childSessionKey")
    current_status = task.get("status", "running")

    # Already terminal — skip (shouldn't reach here normally)
    if current_status in ("completed", "failed", "orphaned"):
        return task, current_status

    run = find_run_for_session(session_key, runs) if session_key else None

    if run is not None:
        # We have runtime evidence
        runtime_status = classify_run(run)

        if runtime_status == "completed":
            task["status"] = "completed"
            task["statusReason"] = "runtime-confirmed-completed"
            task.setdefault("endedAt", now)
            if not task.get("resultSummary"):
                frozen = run.get("frozenResultText", "")
                task["resultSummary"] = frozen[:300] + "..." if len(frozen) > 300 else frozen or "Concluída com sucesso (reconciliado pelo reconciler)"
            task["reconciled"] = True
            return task, "completed"

        if runtime_status == "failed":
            task["status"] = "failed"
            task["statusReason"] = "runtime-confirmed-failed"
            task.setdefault("endedAt", now)
            outcome = run.get("outcome", {})
            if not task.get("error"):
                task["error"] = str(outcome) if outcome else run.get("endedReason", "Falhou (reconciliado pelo reconciler)")
            task["reconciled"] = True
            return task, "failed"

        # runtime says still running — update lastKnownStep if available
        if runtime_status == "running":
            task["status"] = "running"
            task["statusReason"] = "runtime-confirmed-active"
            task["reconciled"] = True
            return task, None

    else:
        # No runtime record for this session
        elapsed = minutes_since(task.get("startedAt"))

        if elapsed is None or elapsed < stall_minutes:
            # Too early to panic — keep as spawned/running
            if current_status == "running" and not task.get("startedAt"):
                task["status"] = "spawned"
                task["statusReason"] = "registered-without-startedAt"
            else:
                task["statusReason"] = "awaiting-runtime-evidence"
            return task, None

        if elapsed >= orphan_minutes:
            # Long enough with no runtime record → orphaned
            task["status"] = "orphaned"
            task["statusReason"] = f"no-runtime-record-after-{elapsed}-min"
            task.setdefault("endedAt", now)
            task["error"] = (
                f"Nenhum registo de runtime encontrado para childSessionKey={session_key!r} "
                f"após {elapsed} min. Task marcada como orphaned."
            )
            task["reconciled"] = True
            return task, "orphaned"

        # Between STALL and ORPHAN threshold
        task["status"] = "stalled"
        task["statusReason"] = f"no-runtime-record-after-{elapsed}-min"
        task["stalledSince"] = task.get("stalledSince") or now
        task["reconciled"] = True
        return task, None

    return task, None


def should_notify(task: Dict[str, Any], notify_every: int, now_ts: Optional[float] = None) -> bool:
    """
    Returns True if we should send a notification for this task now.
    Prevents spam by checking lastNotifiedAt vs notify_every minutes.
    For terminal statuses, notify once (lastNotifiedAt not set yet for this status).
    """
    status = task.get("status", "running")
    last_notified = task.get("lastNotifiedAt")

    # Terminal: notify if we haven't notified for this terminal status yet
    if status in ("completed", "failed", "orphaned"):
        terminal_notified = task.get("terminalNotifiedStatus")
        return terminal_notified != status

    # Running/stalled/spawned: throttle by notify_every
    if last_notified is None:
        return True
    mins = minutes_since(last_notified)
    return mins is not None and mins >= notify_every


def reconcile_all(tasks: List[Dict[str, Any]], config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main reconciliation pass. Returns dict with notifications and remaining tasks.
    """
    runs = load_runs()
    now = now_iso()
    notify_every = int(config.get("notifyEveryMinutes", 10))
    stall_minutes = int(config.get("stallMinutes", DEFAULT_STALL_MINUTES))
    orphan_minutes = int(config.get("orphanMinutes", DEFAULT_ORPHAN_MINUTES))

    notifications = []
    remaining = []
    history_entries = []

    for task in tasks:
        task, terminal = reconcile_task(task, runs, now, stall_minutes, orphan_minutes)
        task["lastCheckedAt"] = now

        status = task.get("status", "running")

        if should_notify(task, notify_every):
            notif = {
                "taskId": task.get("taskId"),
                "status": status,
                "statusReason": task.get("statusReason"),
                "taskName": task.get("taskName"),
                "originChat": task.get("originChat"),
                "reconciled": task.get("reconciled", False),
            }
            if status == "completed":
                notif["resultSummary"] = task.get("resultSummary")
                task["terminalNotifiedStatus"] = "completed"
            elif status == "failed":
                notif["error"] = task.get("error")
                task["terminalNotifiedStatus"] = "failed"
            elif status == "orphaned":
                notif["error"] = task.get("error")
                task["terminalNotifiedStatus"] = "orphaned"
            elif status == "stalled":
                notif["stalledSince"] = task.get("stalledSince")
                notif["minutesElapsed"] = minutes_since(task.get("startedAt"))
            else:
                notif["minutesElapsed"] = minutes_since(task.get("startedAt"))
                notif["lastKnownStep"] = task.get("lastKnownStep")

            task["lastNotifiedAt"] = now
            notifications.append(notif)

        # Keep active unless terminal AND already notified
        if terminal and task.get("terminalNotifiedStatus") == terminal:
            history_entries.append(task)
        else:
            remaining.append(task)

    return {
        "reconciledAt": now,
        "runsLoaded": len(runs),
        "notifications": notifications,
        "remaining": remaining,
        "archived": history_entries,
    }
