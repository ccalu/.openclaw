# op_s4_candidate_evaluator

_Status: planning draft_
_Last updated: 2026-04-04_
_Actor type: operator / evaluation gate_
_Sector: S4 — Asset Research_

---

## 1. Role

`op_s4_candidate_evaluator` is the evaluation gate for S4 target-level discovery outputs.

It does not discover candidates.
It evaluates what discovery workers already found.

Its purpose is to add a second layer of judgment between:
- raw discovery output
and
- coverage / final compilation

---

## 2. Core mission

Read:
- `candidate_set.json`
- target intent context
- local previews/assets/captures

and produce:
- `evaluated_candidate_set.json`

by overlaying final classification and downstream usability judgment on top of the raw discovery artifact.

---

## 3. Inputs

Primary inputs:
- `s4.candidate_set.v1`
- `s4.target_research_brief.v1`

Dispatch/runtime inputs:
- `s4.evaluator_dispatch.v1`
- target-local paths

---

## 4. Outputs

Mandatory outputs:
- `evaluated_candidate_set.json`
- evaluator status/checkpoint artifacts

---

## 5. Responsibilities

## 5.1 Classification correction
- confirm or correct `preliminary_classification`
- assign final classification:
  - `factual_evidence`
  - `visual_reference`
  - `stylistic_inspiration`
  - `reject`

## 5.2 Downstream usefulness judgment
- judge how useful a candidate is for later sectors
- distinguish between:
  - interesting but weak
  - genuinely useful
  - best candidate material

## 5.3 Asset usability judgment
- comment on the usability of:
  - local asset files
  - previews
  - captures
- surface uncertainty rather than hide it

## 5.4 Best-candidate selection
- identify the strongest candidates for the target
- populate `best_candidate_ids`
- mark `is_best_candidate` coherently

---

## 6. What this actor must NOT do

- must not perform discovery in place of workers
- must not recursively search for more assets in the baseline runtime
- must not decide target/scene coverage for the sector as a whole
- must not compile the final pack
- must not overwrite the raw candidate set as if it no longer matters

---

## 7. Overlay semantics

This actor's output is an **overlay** on top of raw discovery.

That means:
- raw discovery remains preserved in `candidate_set.json`
- evaluated output references the same `candidate_id`s
- evaluator adds judgment, selection, and usability interpretation
- downstream systems should join raw and evaluated layers by `candidate_id`

This is an important design rule and should remain explicit.

---

## 8. Evaluation posture

This actor should be rigorous, but not pretend to be omniscient.

It is not a perfect historical or visual truth oracle.
It is a multimodal quality gate that should judge:
- fit to target intent
- clarity of reference
- provenance coherence
- practical usefulness for downstream sectors
- apparent asset/preview quality

Uncertainty should be surfaced in notes/warnings, not hidden.

---

## 9. Key risks

- over-rejecting imperfect but useful candidates
- under-rejecting noisy candidates
- inconsistent best-candidate selection
- treating itself as raw-truth replacement instead of overlay layer
- over-claiming certainty about ambiguous references

---

## 10. Validation expectations

Supervisor/coverage/compiler should be able to validate at minimum:
- evaluated artifact exists
- candidate IDs match raw candidate set
- final classifications are explicit
- best_candidate_ids are internally consistent
- warnings/notes exist

---

## 11. Interfaces with other actors

### With `op_s4_target_research_worker`
- consumes worker output
- does not replace worker's raw artifact

### With `op_s4_coverage_analyst`
- coverage analyst consumes evaluator output as the primary judged layer

### With `op_s4_pack_compiler`
- compiler uses evaluator output to determine what should surface as best-of results in final pack

### With `sm_s4_asset_research`
- dispatched by supervisor
- returns artifact and checkpoint/status through filesystem

---

## 12. Success criteria

This actor is successful when:
- `evaluated_candidate_set.json` exists
- every retained candidate has explicit final classification
- best-candidate selection is coherent
- useful candidates are surfaced without pretending to perfect certainty
- downstream phases can rely on the evaluated layer for structured judgment
