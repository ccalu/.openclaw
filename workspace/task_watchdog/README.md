# Task Watchdog

Global task registry + watchdog for Tobias long-running tasks.

## Goal
- track tasks launched by Tobias
- check every 5 minutes
- notify Lucca every 10 minutes while running
- send final notification on completion/failure
- stay silent when no tasks are active

## Files
- `config.json` — watchdog settings
- `active_tasks.json` — active monitored tasks
- `task_history.jsonl` — completed/failed task history
- `watchdog.py` — deterministic status checker

## Scope (MVP)
- monitors Tobias-launched subagents first
- stores global registry so it can work across chats/surfaces
- internal timestamps are ISO; user-facing messages must be human formatted

## Operational protocol (mandatory)
For every long-running subagent launched by Tobias:
1. spawn the subagent
2. capture the returned `childSessionKey`
3. immediately register it in `active_tasks.json` with that `childSessionKey`
4. if registration fails, treat the launch as incomplete and do not claim monitoring
5. only after successful registration, confirm to Lucca that the task was launched
6. let the watchdog/reconciler own truth about ongoing/terminal state

Rule:
- spawn without register = incomplete launch
- do not claim a task is being monitored unless it is already in the registry
- subagent tasks must include `childSessionKey`; without it, registration must fail

## Quick validation
Expected behavior:
- valid subagent registration with `childSessionKey` -> succeeds and is written to `active_tasks.json`
- invalid subagent registration without `childSessionKey` -> fails immediately with a clear error

## Configurable thresholds
Defined in `config.json`:
- `stallMinutes` — minutes without runtime evidence before a task becomes `stalled`
- `orphanMinutes` — minutes without runtime evidence before a task becomes `orphaned`

## Manual audit check
Run:
`python .\\task_watchdog\\check_watchdog.py`

Returns a compact JSON summary with:
- total active tasks
- counts by status
- flagged tasks (`stalled`, `orphaned`, `failed`)
- current threshold config

## Safety layers
The watchdog design uses three layers together:
1. **Launch wrapper discipline** — spawn -> register -> confirm
2. **No-confirmation-without-registry** — Tobias must not claim monitoring without persisted registration
3. **Launch audit** — `watchdog_launch_audit.py` scans for recent unregistered subagent sessions and auto-registers them as a fallback safety net
