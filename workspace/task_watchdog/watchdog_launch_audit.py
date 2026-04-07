from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Set

BASE = Path(r"C:\Users\User-OEM\.openclaw\workspace\task_watchdog")
ACTIVE_PATH = BASE / "active_tasks.json"
SCAN_MINUTES = 20


def now_local() -> datetime:
    return datetime.now(timezone.utc).astimezone()


def iso_now() -> str:
    return now_local().isoformat()


def load_active() -> List[Dict[str, Any]]:
    if not ACTIVE_PATH.exists():
        return []
    try:
        return json.loads(ACTIVE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return []


def save_active(tasks: List[Dict[str, Any]]) -> None:
    ACTIVE_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = ACTIVE_PATH.with_suffix('.json.tmp')
    tmp.write_text(json.dumps(tasks, ensure_ascii=False, indent=2), encoding='utf-8')
    tmp.replace(ACTIVE_PATH)


def format_human(dt: datetime) -> str:
    return dt.strftime('%d/%m %H:%M')


def scan_subagent_sessions() -> List[Dict[str, Any]]:
    sessions_path = Path(r"C:\Users\User-OEM\.openclaw\sessions.json")
    if not sessions_path.exists():
        return []
    try:
        data = json.loads(sessions_path.read_text(encoding='utf-8'))
    except Exception:
        return []

    now = now_local()
    cutoff = now - timedelta(minutes=SCAN_MINUTES)
    found = []

    if isinstance(data, list):
        items = data
    elif isinstance(data, dict):
        items = data.get('sessions', []) or data.get('items', []) or []
    else:
        items = []

    for item in items:
        key = item.get('key') or item.get('sessionKey') or ''
        if 'subagent' not in key:
            continue
        updated_raw = item.get('updatedAt') or item.get('lastMessageAt') or item.get('createdAt')
        if not updated_raw:
            continue
        try:
            updated = datetime.fromisoformat(updated_raw.replace('Z', '+00:00')).astimezone()
        except Exception:
            continue
        if updated < cutoff:
            continue
        found.append({
            'sessionKey': key,
            'updatedAt': updated.isoformat(),
            'label': item.get('label') or item.get('name') or 'subagent sem label'
        })
    return found


def main() -> None:
    active = load_active()
    tracked_keys: Set[str] = {t.get('childSessionKey') for t in active if t.get('childSessionKey')}
    scanned = scan_subagent_sessions()
    added = []
    now = iso_now()

    for sess in scanned:
        key = sess['sessionKey']
        if key in tracked_keys:
            continue
        task = {
            'taskId': f"auto_{abs(hash(key))}",
            'taskName': sess.get('label') or 'Subagente detectado automaticamente',
            'type': 'subagent',
            'model': 'desconhecido (auto-detected)',
            'originChat': 'telegram:1962323981',
            'originSession': 'auto-detected',
            'replyTarget': 'current_chat',
            'startedAt': sess.get('updatedAt') or now,
            'lastCheckedAt': now,
            'lastNotifiedAt': None,
            'notifyEveryMinutes': 10,
            'status': 'running',
            'childSessionKey': key,
            'summaryHint': 'detectado automaticamente pelo auditor de launches',
            'lastKnownStep': 'detected_unregistered_launch',
            'launcher': 'Tobias (auto-audit)'
        }
        active.append(task)
        added.append(task)

    save_active(active)
    print(json.dumps({
        'checkedAt': now,
        'detected': len(scanned),
        'added': len(added),
        'items': added,
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
