# S4 — Next Documentation Steps

_Status: working note_
_Last updated: 2026-04-04_

---

## Goal

Track the documentation pieces still needed before S4 implementation can begin safely.

---

## Already created

- `S4_asset_research_architecture.md`
- `S4_runtime_control_flow.md`
- `S4_invocation_spec.md`
- `S4_contracts_registry.md`

---

## Highest-priority next docs

### 1. Schema / contract detail docs

Needed next:

- `S4_schema_research_intake.md`
- `S4_schema_target_research_brief.md`
- `S4_schema_candidate_set.md`
- `S4_schema_evaluated_candidate_set.md`
- `S4_schema_coverage_report.md`
- `S4_schema_research_pack.md`

These should freeze:
- required fields
- optional fields
- enums
- ownership of each field
- producer/consumer notes

### 2. Agent-specific docs

Needed after schemas are stable:

- `sm_s4_asset_research.md`
- `op_s4_target_builder.md`
- `op_s4_web_investigator.md`
- `op_s4_target_research_worker.md`
- `op_s4_candidate_evaluator.md`
- `op_s4_coverage_analyst.md`
- `op_s4_pack_compiler.md`

### 3. Runtime validation / preflight docs

Potentially useful:

- `S4_preflight_checklist.md`
- `S4_narrow_validation_plan.md`

---

## Current planning stance

S4 is now documented strongly enough at the architecture/runtime/invocation layer to support another review pass.

The next review should focus on:

- whether the flattened runtime dispatch model is correct
- whether the contracts registry is complete enough
- whether separate evaluator + coverage analyst should remain in v1
- what exact schema shapes to freeze next
