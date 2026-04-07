# S4 — Implementation Plan

_Status: implementation planning draft_
_Last updated: 2026-04-04_
_Owner: Tobias_
_Sector: S4 — Asset Research_

---

## 1. Purpose

This document defines the recommended implementation sequence for S4.

Its job is not to redesign the sector.
The architecture, contracts, schemas, runtime flow, and actor boundaries are already sufficiently frozen for implementation planning.

The purpose of this plan is to answer:
- what should be built first
- what should be validated first
- what should not be attempted too early
- how to move from documentation to real runtime safely

---

## 2. Planning posture

S4 should not be implemented as a big-bang multi-agent build.

The correct posture is:
- foundation first
- narrow validation before breadth
- single-target proof before multi-target scaling
- disk truth before conversational confidence
- supervisor-controlled orchestration before any complexity expansion

This follows the proven Block 2 / S3 lesson:
**runtime correctness must be proven incrementally on disk.**

---

## 3. Preconditions

Before implementation starts, the following should already be considered frozen enough:
- `S4_asset_research_architecture.md`
- `S4_runtime_control_flow.md`
- `S4_invocation_spec.md`
- `S4_contracts_registry.md`
- all S4 schema docs
- all S4 actor docs

Minor documentation hygiene may continue, but implementation should not wait for cosmetic perfection.

---

## 4. Global implementation principles

## 4.1 Filesystem truth first
All progress, validation, and closure decisions must be based on disk artifacts, not chat summaries.

## 4.2 Python boundary controls dispatch
Do not push orchestration logic into conversational turns if the boundary/runtime layer can own it more safely.

## 4.3 No premature parallel complexity
Do not begin with multi-target concurrency or retry sophistication.
First prove the happy-path structure with one target.

## 4.4 Schema validation early
Artifacts should be validated against frozen schemas as early as possible.
Do not let output shapes drift during implementation.

## 4.5 Actor richness preserved, runtime flattened where needed
Keep the architectural richness of S4.
But the implementation substrate should remain close to the proven S3/B2 dispatch pattern.

---

## 5. Recommended implementation phases

## 5.1 Phase 0 — pre-flight fix pass

### Goal
Remove small remaining ambiguities before code work begins.

### Scope
- apply the final non-blocking doc fixes from Round 4 review
- ensure paths and input ownership are aligned
- ensure batch manifest schema exists
- decide the canonical schema validation approach
- align foundation order so the real boundary launch is proved early

### Exit criteria
- no remaining unclear ownership around pack compiler inputs
- no remaining path ambiguity around `coverage_report.json`
- `s4.research_batch_manifest.v1` documented
- schema validation approach explicitly chosen
- foundation sequence reflects early proof of real sector launch

### Status
This phase is effectively complete if the latest R4/R5 alignment pass has been applied.

---

## 5.2 Phase 1 — foundation layer

### Goal
Materialize the runtime substrate for S4 before implementing rich behavior.

### Deliverables
- S4 directory structure creation logic
- schema file materialization strategy
- shared Python helpers for:
  - path building
  - artifact loading/writing
  - schema validation
  - checkpoint writing
  - status mirroring
- sector bootstrap loading/validation
- boundary hook for launching `sm_s4_asset_research`

### What this phase is proving
- S4 can exist as a runtime sector on disk
- paths can be built deterministically
- artifacts can be validated consistently
- supervisor launch path is real

### What not to do in this phase
- no multi-target orchestration yet
- no evaluator/coverage intelligence depth yet
- no concurrency tuning yet

### Exit criteria
- boundary can detect/launch S4 reliably
- S4 directory skeleton is created deterministically
- at least one artifact can be written and schema-validated through shared helpers

---

## 5.3 Phase 2 — single-target prototype

### Goal
Prove one complete S4 pipeline for one target end to end.

### Minimal pipeline scope
1. target builder writes intake
2. supervisor creates batch manifest
3. web investigator writes one target brief
4. one research worker writes one candidate set
5. evaluator writes one evaluated candidate set
6. coverage analyst writes one coverage report
7. pack compiler writes final pack + sector report
8. supervisor validates and closes

### Why this is the critical phase
This phase proves:
- actor boundaries are real
- schemas are usable in runtime
- handoffs are sufficient
- final closure can be decided from artifacts

It is the most important phase in the whole implementation.

### What not to do in this phase
- no parallel worker fan-out as a requirement
- no second discovery round
- no broad optimization effort
- no assumption that scale correctness follows automatically

### Exit criteria
- one real target runs end-to-end
- every artifact required by the contracts exists
- every produced artifact passes schema validation
- supervisor reaches deterministic completion from disk truth

---

## 5.4 Phase 3 — supervisor orchestration hardening

### Goal
Move from single-path prototype to real supervisor-controlled sector flow.

### Scope
- full dispatch sequencing from supervisor
- explicit phase-gate validation between operators
- checkpoint progression and resume logic
- failure handling aligned to v1 decision table

### What this phase is proving
- the sector behaves like a real state machine
- partial worker outcomes are handled intentionally
- closure/failure semantics are deterministic

### Exit criteria
- supervisor can run the full S4 sequence without manual operator babysitting
- checkpoint progression is visible and debuggable
- failure conditions produce correct sector-level outcomes

---

## 5.5 Phase 4 — multi-target scaling

### Goal
Expand from one target to bounded multi-target execution.

### Scope
- multiple target briefs
- multiple worker runs
- batch grouping
- bounded parallelism
- aggregation of target-local outputs into evaluator / coverage / compiler inputs

### Main risk in this phase
This is where orchestration complexity rises sharply.
The biggest risk is not model quality.
It is coordination drift:
- missing outputs
- broken joins
- unstable aggregation
- race conditions around readiness assumptions

### Guardrail
Do not start this phase until the single-target path is clean and boring.

### Exit criteria
- multiple targets can run in one sector pass
- batch manifest is actually used as control artifact
- coverage and final pack remain coherent across aggregated outputs

---

## 5.6 Phase 5 — hardening and operational maturity

### Goal
Improve resilience, observability, and production usability.

### Scope
- better runtime telemetry
- stronger debug artifacts
- timeout/failure tuning
- optional degraded-completion formalization if later needed
- quality-of-life improvements for reports and diagnostics

### Important note
This phase should not be mixed into earlier correctness work unless necessary.
Correctness first, elegance later.

---

## 6. Recommended build order by actor

Recommended order:

1. `sm_s4_asset_research` bootstrap + minimal dispatch skeleton
2. `op_s4_target_builder`
3. `op_s4_web_investigator`
4. `op_s4_target_research_worker`
5. `op_s4_candidate_evaluator`
6. `op_s4_coverage_analyst`
7. `op_s4_pack_compiler`
8. return to `sm_s4_asset_research` for full orchestration hardening

### Why this order
Because it follows artifact dependency order and supports narrow proof.

The supervisor should exist first as a shell, but not be fully hardened before the downstream artifact chain is proven.

---

## 7. Readiness gates

## 7.1 Gate A — Foundation readiness
Must be true before prototype work:
- directory creation works
- schema validation helper works
- bootstrap load works
- supervisor launch path works

## 7.2 Gate B — Single-target runtime readiness
Must be true before multi-target scaling:
- one target succeeds end to end
- all required artifacts validate
- final closure works from disk truth

## 7.3 Gate C — Orchestration readiness
Must be true before scaling:
- supervisor phase transitions are stable
- checkpoint writes are consistent
- failure table behavior is respected

## 7.4 Gate D — Multi-target readiness
Must be true before any production-like runs:
- batch grouping is stable
- aggregation is stable
- coverage/pack coherence survives multiple targets

---

## 8. Narrow validations to run early

## 8.1 Validation 1 — schema materialization sanity
Before building rich runtime logic:
- generate/encode real schema files or equivalent validators
- verify they can validate sample artifacts

## 8.2 Validation 2 — boundary launch sanity
Before implementing all operators:
- prove boundary can launch `sm_s4_asset_research` from `s4_requested.json`

## 8.3 Validation 3 — target builder round-trip
First operator proof should be:
- input upstream artifacts
- write `s4_research_intake.json`
- validate it against schema

## 8.4 Validation 4 — single target sector closure
Before scaling:
- prove the whole sector can close successfully with one target

## 8.5 Validation 5 — controlled partial worker failure
Before production-like scaling:
- simulate one worker failure
- verify supervisor continues where policy says continue
- verify coverage/final pack surface gaps honestly

---

## 9. Things that should NOT be attempted too early

- no automatic second research round
- no complex degraded completion semantics
- no deep retry matrix before baseline correctness exists
- no premature optimization around concurrency
- no reliance on conversational summaries as runtime truth
- no attempt to prove the whole sector with a large real-world batch before the one-target path is stable

---

## 10. Success definition for implementation planning

Implementation planning is successful when it becomes obvious:
- what should be built first
- how each phase proves the next one safe
- what the gates are
- where the main runtime risks live
- how to avoid repeating the old failure mode of over-ambitious implementation before substrate proof

---

## 11. Recommended next planning docs

After this document, the most useful next docs are:

1. `S4_FOUNDATION_PLAN.md`
2. `S4_SINGLE_TARGET_PROTOTYPE_PLAN.md`
3. optional: `S4_IMPLEMENTATION_CHECKLIST.md`

These should translate the phase logic in this document into concrete implementation work items.

---

## 12. Final recommendation

S4 should now transition from documentation planning into implementation planning and then into incremental runtime materialization.

The correct first implementation objective is **not** “build all of S4”.
The correct first implementation objective is:

**prove a disk-truth, schema-validated, single-target S4 pipeline under supervisor control.**

Everything else should build on top of that proof.
