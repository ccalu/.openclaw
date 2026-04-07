# S4 — Invocation Specification

_Status: canonical (V3)_
_Last updated: 2026-04-06_
_Owner: Tobias_

---

## 1. Purpose

This document defines the **runtime invocation discipline** for S4 in its current V3 architecture.

---

## 2. Entry point

The S4 entry point is `supervisor_shell.py`:

```
python supervisor_shell.py <bootstrap_path>
```

The SM actor (`sm_s4_asset_research`) receives the bootstrap path in its activation message and delegates immediately to `supervisor_shell.py`. The SM performs no orchestration logic itself.

---

## 3. Invocation patterns

S4 V3 uses two distinct invocation patterns:

### 3.1 Helper-direct (Python subprocess)

Used for phases where LLM actors proved unreliable.

| Phase | Helper | Called by |
|-------|--------|-----------|
| 2 - Target building | `target_builder.py` | `supervisor_shell.py` direct |
| 3 - Batch manifest | `batch_manifest_builder.py` | `supervisor_shell.py` direct |
| 4 - Web investigation | `web_investigator.py` | `supervisor_shell.py` direct |
| 5 - Asset pipeline | `s4_asset_pipeline.py` | `supervisor_shell.py` direct |

These helpers use GPT-5.4-nano (OpenAI API) and Serper.dev (Google Images API) directly in Python. No OpenClaw actor is involved.

### 3.2 OpenClaw CLI dispatch

Used for the two remaining analysis/compilation phases.

```text
openclaw agent --agent <agent_id> --message <task_payload> --json --timeout <seconds> --session-id <unique_session_id>
```

| Phase | Actor | Timeout |
|-------|-------|---------|
| 6 - Coverage analysis | `op_s4_coverage_analyst` | 1800s |
| 7 - Pack compilation | `op_s4_pack_compiler` | 1800s |

These actors call their respective Python helpers (`coverage_analyst.py`, `pack_compiler.py`) internally, then validate output on disk.

---

## 4. Session cleanup

Before each S4 run, `supervisor_shell.py` cleans all OpenClaw agent sessions:

```
openclaw sessions cleanup --enforce --agent <agent_id>
```

Applied to all S4 agents (active and deprecated):
- `sm_s4_asset_research`
- `op_s4_coverage_analyst`
- `op_s4_pack_compiler`
- `op_s4_target_builder` (deprecated, cleaned for safety)
- `op_s4_web_investigator` (deprecated, cleaned for safety)
- `op_s4_target_research_worker` (deprecated, cleaned for safety)
- `op_s4_candidate_evaluator` (deprecated, cleaned for safety)

This prevents stale context accumulation and cross-video contamination.

---

## 5. Mandatory invocation rules

### Rule 1 — Unique session IDs

Every OpenClaw invocation uses a unique session ID:

```text
{job_id}__s4__{actor_id}__{timestamp}
```

### Rule 2 — `--json` required

All OpenClaw invocations use `--json` to avoid ANSI noise.

### Rule 3 — Explicit timeout required

No reliance on default timeouts. Current values: 1800s for both active actors.

### Rule 4 — Absolute paths only

Every bootstrap, dispatch, checkpoint, and output path is absolute. Relative path drift caused real failures in earlier versions.

### Rule 5 — Disk artifacts are completion truth

Process exit codes and conversational responses are not completion truth. The supervisor validates:
- Output file exists on disk
- JSON parses without error
- Schema validation passes

### Rule 6 — Checkpoint resume

`supervisor_shell.py` writes phase checkpoints to `runtime/phase_checkpoints.json`. On re-execution, it resumes from the last completed phase.

---

## 6. Who dispatches whom

### Boundary level

`w3_block2.py`:
- Detects `s4_requested.json`
- Launches `sm_s4_asset_research`
- Detects `s4_completed.json` / `s4_failed.json`

### Director level

`b2_director`:
- Writes S4 request checkpoint and bootstrap
- Resumes after `s4_completed` / `s4_failed`

### SM level

`sm_s4_asset_research`:
- Receives bootstrap path
- Calls `supervisor_shell.py <bootstrap_path>`
- Does NOT dispatch operators itself

### Supervisor shell level

`supervisor_shell.py`:
- Calls `target_builder.py` directly (helper-direct)
- Calls `batch_manifest_builder.py` directly (helper-direct)
- Calls `web_investigator.py` directly (helper-direct)
- Calls `s4_asset_pipeline.py` directly (helper-direct)
- Dispatches `op_s4_coverage_analyst` via OpenClaw CLI
- Dispatches `op_s4_pack_compiler` via OpenClaw CLI
- Writes completion/failure checkpoints

---

## 7. Deprecated actors (not dispatched)

These actors are no longer dispatched by `supervisor_shell.py`. Their work is performed by helper-direct Python calls:

| Deprecated Actor | Replaced by |
|-----------------|-------------|
| `op_s4_target_builder` | `target_builder.py` |
| `op_s4_web_investigator` | `web_investigator.py` |
| `op_s4_target_research_worker` | `s4_query_generator.py` + `s4_image_collector.py` |
| `op_s4_candidate_evaluator` | `s4_visual_evaluator.py` |

---

## 8. Required checkpoints and artifacts

### Boundary-facing
- `s4_requested.json` (written by `b2_director`)
- `s4_completed.json` / `s4_failed.json` (mirrored to `{b2_root}/checkpoints/`)

### Supervisor-owned
- `runtime/phase_checkpoints.json`
- `runtime/sector_status.json`
- `runtime/video_context.json`
- `runtime/openai_usage.json`

### Phase outputs
- `intake/research_intake.json`
- `intake/research_batch_manifest.json`
- `targets/{tid}/{tid}_brief.json`
- `targets/{tid}/{tid}_asset_materialization_report.json`
- `compiled/coverage_report.json`
- `compiled/research_pack.json`
- `compiled/s4_sector_report.md`
