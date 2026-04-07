# sm_s4_asset_research

_Status: canonical (V3)_
_Last updated: 2026-04-06_
_Actor type: sector supervisor_
_Sector: S4 — Asset Research_

---

## 1. Role

`sm_s4_asset_research` is the **sector supervisor** for S4.

In V3, the SM is a thin delegation layer. Its only job is to:
1. Receive the activation message containing the bootstrap path
2. Validate that the bootstrap path exists
3. Delegate entirely to `supervisor_shell.py`

All orchestration logic — phase progression, checkpoint management, operator dispatch, validation gates — lives in `supervisor_shell.py`.

---

## 2. Core mission

Take S4 from:
- Requested sector with valid S3 upstream artifacts

to:
- Completed / failed S4 sector with validated final outputs and checkpoints

by delegating to the deterministic Python orchestrator.

---

## 3. Execution model

```
SM receives activation message with bootstrap_path
  |
  v
SM validates bootstrap_path exists on disk
  |
  v
SM calls: python supervisor_shell.py <bootstrap_path>
  |
  v
SM confirms s4_completed.json or s4_failed.json exists
  |
  v
SM reports result
```

The SM does NOT:
- Parse S3 entities
- Dispatch operators directly
- Evaluate candidates
- Make coverage decisions
- Compile packs

---

## 4. Pipeline (delegated to supervisor_shell.py)

| Phase | Actor | Pattern |
|-------|-------|---------|
| 1 | Bootstrap | supervisor_shell.py |
| 2 | target_builder.py | HELPER-DIRECT |
| 3 | batch_manifest_builder.py | HELPER-DIRECT |
| 4 | web_investigator.py | HELPER-DIRECT |
| 5 | s4_asset_pipeline.py (4 sub-steps) | HELPER-DIRECT |
| 6 | op_s4_coverage_analyst | OPENCLAW CLI |
| 7 | op_s4_pack_compiler | OPENCLAW CLI |
| 8 | Completion | supervisor_shell.py |

GPT-5.4-nano via OpenAI API powers phases 2 and 5 (target consolidation, query generation, visual evaluation). Serper.dev provides Google Images search in phase 5.

---

## 5. Interfaces

### With `b2_director`
- Receives sector request indirectly through bootstrap + boundary launch
- Returns sector completion/failure via checkpoint files

### With `supervisor_shell.py`
- SM delegates entirely to it
- Shell handles all phase logic and operator dispatch

---

## 6. Failure handling

SM confirms outcome from disk:
- Exit 0 + `s4_completed.json` exists -> report success
- Exit != 0 or `s4_failed.json` exists -> report failure with reason

---

## 7. Success criteria

This actor is successful when:
- `supervisor_shell.py` is called with the correct bootstrap path
- The sector completes with `s4_completed.json` and both `research_pack.json` + `s4_sector_report.md` exist
- Or the sector fails cleanly with `s4_failed.json` containing an explicit failure reason
