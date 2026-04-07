# op_s4_pack_compiler

_Status: canonical (V3)_
_Last updated: 2026-04-06_
_Actor type: operator / final compiler_
_Sector: S4 — Asset Research_

---

## 1. Role

`op_s4_pack_compiler` is the final compiler of S4.

It transforms the sector's distributed artifacts into the canonical final outputs. This is one of only 2 active OpenClaw actors in S4, dispatched via OpenClaw CLI by `supervisor_shell.py`.

---

## 2. Core mission

Read:
- `research_intake.json`
- `{tid}_asset_materialization_report.json` per target (V3 format, primary)
- `evaluated_candidate_set.json` per target (legacy fallback)
- `coverage_report.json`

and produce:
- `compiled/research_pack.json`
- `compiled/s4_sector_report.md`

---

## 3. Input format handling

### V3 format (primary): `asset_materialization_report.json`

Contains approved assets with relevance scores, source URLs, and evaluation rationale.

### Legacy format (fallback): `evaluated_candidate_set.json`

The compiler checks for V3 format first. If not found for a target, falls back to legacy format.

---

## 4. Outputs

Mandatory outputs:
- `compiled/research_pack.json` (contract: `s4.research_pack.v1`)
- `compiled/s4_sector_report.md`
- `compiled/s4_reference_ready_asset_pool.json` (contract: `s4.reference_ready_asset_pool.v1`)

---

## 5. Responsibilities

### 5.1 Target-level compilation
- Surface approved asset references per target
- Carry through coverage state from coverage report
- Preserve unresolved notes

### 5.2 Scene-level compilation
- Compile scene-level recommendations from target-level results
- Reflect scene coverage state

### 5.3 Asset manifest
- Surface asset manifest with local paths for downstream consumption

### 5.4 Warning/gap preservation
- Preserve unresolved gaps from coverage report
- Preserve warnings — do not present the pack as cleaner than reality

### 5.5 Reference-ready asset pooling
- Collect `.reference_ready.json` sidecars from all approved assets across targets
- Compile into `s4_reference_ready_asset_pool.json` with grouped views (`by_target`, `by_reference_value`, `by_depiction_type`)
- Include `scene_relevance` per asset for downstream prioritization

### 5.6 Sector report
- Write `s4_sector_report.md` summarizing outcome, strengths, gaps, and caveats

---

## 6. Execution model

1. Receive activation message with `intake_path`, `sector_root`, `job_id`, `video_id`, `account_id`, `language`
2. Call helper: `pack_compiler.py <intake_path> <sector_root> <job_id> <video_id> <account_id> <language>`
3. Validate `compiled/research_pack.json` exists on disk
4. Validate `compiled/s4_reference_ready_asset_pool.json` exists on disk
5. Validate `compiled/s4_sector_report.md` exists on disk
6. Validate schema via `schema_validator.py`
7. Report result

---

## 7. What this actor must NOT do

- Must not redo visual evaluation
- Must not redo coverage analysis
- Must not hide unresolved gaps
- Must not close the sector (supervisor's job)
- Must not perform discovery

---

## 8. Interfaces

### With `supervisor_shell.py`
- Dispatched via OpenClaw CLI
- Returns final pack and sector report via filesystem

### With `op_s4_coverage_analyst`
- Consumes coverage states from coverage report
- Reflects, does not reinterpret, structural sufficiency decisions

### With downstream sectors
- `research_pack.json` is the main S4 artifact that S5 and later sectors consume
- `s4_reference_ready_asset_pool.json` provides structured reference metadata for S5 visual spec assembly

---

## 9. Success criteria

This actor is successful when:
- `research_pack.json` exists
- `s4_reference_ready_asset_pool.json` exists
- `s4_sector_report.md` exists
- Target-level and scene-level outputs are coherent
- Warnings and unresolved gaps are preserved
- Supervisor can close the sector based on real artifacts
