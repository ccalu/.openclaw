# op_s4_coverage_analyst

_Status: canonical (V3)_
_Last updated: 2026-04-06_
_Actor type: operator / coverage gate_
_Sector: S4 — Asset Research_

---

## 1. Role

`op_s4_coverage_analyst` is the structural sufficiency gate of S4.

It reads the results of the V3 asset pipeline (materialization reports) and determines whether the set of approved images is sufficient at target level and scene level.

This is one of only 2 active OpenClaw actors in S4. It is dispatched via OpenClaw CLI by `supervisor_shell.py`.

---

## 2. Core mission

Read:
- `research_intake.json` (target/scene definitions)
- `{tid}_asset_materialization_report.json` per target (V3 format, primary)
- `evaluated_candidate_set.json` per target (legacy V1/V2 format, fallback)

and produce:
- `compiled/coverage_report.json`

that states:
- what is covered
- what is partially covered
- what is only inspiration-level
- what remains unresolved

---

## 3. Input format handling

### V3 format (primary): `asset_materialization_report.json`

Contains:
- `approved_assets[]` with `filename`, `source_url`, `relevance_score`, `rationale`
- `rejected_count`, `total_evaluated`
- `evaluation_notes`

### Legacy format (fallback): `evaluated_candidate_set.json`

The analyst must check for V3 format first. If not found for a target, fall back to legacy `evaluated_candidate_set.json` in the same target directory.

---

## 4. Outputs

Mandatory output:
- `compiled/coverage_report.json` (contract: `s4.coverage_report.v1`)

---

## 5. Responsibilities

### 5.1 Target-level coverage assessment
Determine whether each target is: `covered`, `partially_covered`, `inspiration_only`, or `unresolved`.

### 5.2 Scene-level coverage assessment
Assess whether scenes are sufficiently supported by their linked targets.

### 5.3 Gap surfacing
Produce explicit unresolved gaps. Make downstream absence visible.

### 5.4 Coverage reporting
Emit structured target-level and scene-level summaries. Preserve warnings.

---

## 6. Execution model

1. Receive activation message with `intake_path` and `sector_root`
2. Call helper: `coverage_analyst.py <intake_path> <sector_root>`
3. Validate `compiled/coverage_report.json` exists on disk
4. Validate schema via `schema_validator.py`
5. Report result

---

## 7. What this actor must NOT do

- Must not redo visual evaluation
- Must not perform discovery or search
- Must not compile the final pack
- Must not hide weak coverage behind vague language

---

## 8. Interfaces

### With `supervisor_shell.py`
- Dispatched via OpenClaw CLI
- Returns coverage report via filesystem artifact

### With `op_s4_pack_compiler`
- Pack compiler consumes coverage states downstream

---

## 9. Success criteria

This actor is successful when:
- `compiled/coverage_report.json` exists
- Target-level coverage is explicit for all targets
- Scene-level coverage is explicit
- Unresolved gaps are visible and useful
