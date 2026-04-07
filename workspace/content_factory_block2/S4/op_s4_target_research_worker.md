# op_s4_target_research_worker

_Status: planning draft_
_Last updated: 2026-04-04_
_Actor type: operator / target-level discovery worker_
_Sector: S4 — Asset Research_

---

## 1. Role

`op_s4_target_research_worker` is the target-level discovery worker of S4.

It is the actor that performs bounded discovery work for:
- one target
or
- one tightly bounded mini-batch of targets

In S4 v1, this actor should remain a **leaf node** in the critical path.

---

## 2. Core mission

Read one `target_research_brief.json` and produce:
- `candidate_set.json`
- local files under `assets/`, `previews/`, `captures/`
- worker status/checkpoint outputs

It is the first actor that turns planning into real discovered material.

---

## 3. Inputs

Primary input:
- `s4.target_research_brief.v1`

Dispatch/runtime inputs:
- `s4.target_research_worker_dispatch.v1`
- target-local storage paths
- output contract reference

---

## 4. Outputs

Mandatory outputs:
- `candidate_set.json`
- target-local file outputs when available/appropriate
- worker status/checkpoint artifacts

Possible local file outputs:
- `assets/*`
- `previews/*`
- `captures/*`

---

## 5. Responsibilities

## 5.1 Target-focused discovery
- execute discovery for the assigned target only
- follow the target brief's search goals and research needs
- remain bounded in scope

## 5.2 Candidate collection
- identify candidate references/assets/pages
- capture source metadata
- preserve the reason each candidate is being kept

## 5.3 Local acquisition/materialization
- materialize files when useful and possible
- distinguish between:
  - `reference_only`
  - `preview_asset`
  - `materialized_asset`
- avoid indiscriminate downloading

## 5.4 Candidate persistence
- write `candidate_set.json`
- include all required candidate fields
- include warnings rather than silently omitting edge cases

---

## 6. What this actor must NOT do

- must not recursively spawn more agents in the S4 v1 critical path
- must not act as the evaluator
- must not decide target/scene coverage
- must not compile the final sector pack
- must not hide failed downloads or zero-result outcomes by omitting the candidate set file

---

## 7. Discovery posture

This actor should be:
- focused
- opportunistic within the target scope
- willing to keep useful-but-imperfect candidates for later evaluation

It should not behave as if it must achieve perfect final judgment itself.
That is evaluator/coverage/compiler territory.

---

## 8. Asset acquisition posture

The worker is allowed to produce three levels of acquisition outcome:

### 8.1 `reference_only`
Useful source found, but no local preview/asset captured.

### 8.2 `preview_asset`
Useful preview/capture exists locally, even if the source asset was not fully materialized.

### 8.3 `materialized_asset`
Local file exists and is linked clearly in the candidate record.

The worker should preserve useful candidates even when materialization is incomplete.
Failed downloads are a warning condition, not an automatic reason to discard a candidate.

---

## 9. Key risks

- returning too many noisy candidates
- failing to preserve useful candidates after partial acquisition failure
- over-downloading junk
- weak traceability between candidate metadata and local files
- drifting beyond the brief into unbounded browsing

---

## 10. Validation expectations

Supervisor/evaluator should be able to validate at minimum:
- candidate set exists
- required fields exist
- confidence values are normalized
- acquisition modes are explicit
- local file paths are present where claimed
- warnings explain zero-candidate or failed-materialization cases

---

## 11. Interfaces with other actors

### With `op_s4_web_investigator`
- consumes the brief produced by investigator
- does not require direct runtime spawn by investigator in v1

### With `sm_s4_asset_research`
- is dispatched by supervisor
- returns results via target-local artifacts and worker checkpoint/status

### With `op_s4_candidate_evaluator`
- evaluator reads the produced `candidate_set.json`
- evaluator may reinterpret/reclassify the candidates

---

## 12. Success criteria

This actor is successful when:
- `candidate_set.json` exists
- candidates are target-relevant and traceable
- local acquisition state is explicit
- useful imperfect candidates are preserved for evaluation
- the output remains bounded, structured, and consumable by evaluator
