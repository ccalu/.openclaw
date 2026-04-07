# S4 — Single-Target Prototype Plan

_Status: implementation planning draft_
_Last updated: 2026-04-04_
_Owner: Tobias_
_Sector: S4 — Asset Research_

---

## 1. Purpose

This document defines the first end-to-end correctness proof for S4.

The goal is not to prove scale.
The goal is not to prove production maturity.
The goal is to prove that the S4 sector can complete a real disk-truth pipeline for exactly one target under supervisor control.

This is the first meaningful runtime proof that the documentation can survive contact with implementation.

---

## 2. Why single-target first

The single-target prototype is the safest way to validate whether S4's architecture actually works in runtime.

It isolates the right question:

> Can S4 take one bounded research target from intake to final pack through the real artifact chain?

Without this proof, jumping to multiple targets would blur together:
- artifact design mistakes
- supervisor sequencing mistakes
- aggregation mistakes
- concurrency mistakes
- quality-of-output mistakes

Single-target removes most of that noise.

---

## 3. Prototype objective

The prototype is successful when one real S4 run can:
- start from valid upstream S3 inputs
- build intake for one target
- build one brief
- produce one candidate set
- produce one evaluated candidate set
- produce one coverage report
- produce one final research pack
- produce one sector report
- close successfully through supervisor validation

And all of that must be validated from disk artifacts, not from conversational summaries.

---

## 4. Prototype scope

Included in scope:
- one supervisor-managed S4 run
- one real target flowing through the full sector chain
- schema validation for every major output artifact
- checkpoint/status visibility during progression
- final completion through real S4 closure path

Explicitly not in scope:
- multiple targets
- parallel worker fan-out
- second discovery round
- production-grade retry logic
- deep optimization of prompts or search strategy
- degraded completion as a core scenario

---

## 5. Recommended target selection posture

The prototype target should be chosen for clarity, not difficulty.

Ideal properties:
- target is easy to identify in S3 compiled entities
- target is likely to produce discoverable references
- target is linked to a real scene
- target is not the most ambiguous or adversarial case in the video

Do not choose the hardest target first just to feel robust.
The goal is to prove runtime correctness, not frontier difficulty.

---

## 6. Minimal prototype pipeline

Recommended sequence:

1. Boundary launches `sm_s4_asset_research`
2. Supervisor validates bootstrap and initializes runtime
3. `op_s4_target_builder` writes `s4_research_intake.json`
4. Supervisor creates `research_batch_manifest.json`
5. `op_s4_web_investigator` writes one `target_research_brief.json`
6. One `op_s4_target_research_worker` writes one `candidate_set.json`
7. `op_s4_candidate_evaluator` writes one `evaluated_candidate_set.json`
8. `op_s4_coverage_analyst` writes `compiled/coverage_report.json`
9. `op_s4_pack_compiler` writes:
   - `compiled/s4_research_pack.json`
   - `compiled/s4_sector_report.md`
10. Supervisor validates final artifacts
11. Supervisor writes `s4_completed.json`
12. Boundary/B2 can resume from the final checkpoint

---

## 7. Prototype proof points by actor

## 7.1 `sm_s4_asset_research`
Must prove:
- real boot works
- phase progression works
- per-step validation works
- final completion uses artifact truth

## 7.2 `op_s4_target_builder`
Must prove:
- can read S3 upstream artifacts
- can normalize a one-target intake correctly
- output validates against `s4.research_intake.v1`

## 7.3 `op_s4_web_investigator`
Must prove:
- can consume intake + batch manifest
- can produce one usable target brief
- output validates against `s4.target_research_brief.v1`

## 7.4 `op_s4_target_research_worker`
Must prove:
- can consume one brief
- can produce one raw candidate set
- output validates against `s4.candidate_set.v1`

## 7.5 `op_s4_candidate_evaluator`
Must prove:
- can consume the one-target raw set correctly
- can produce overlay evaluation output
- output validates against `s4.evaluated_candidate_set.v1`

## 7.6 `op_s4_coverage_analyst`
Must prove:
- can map one target plus linked scene(s) into coverage semantics
- output validates against `s4.coverage_report.v1`

## 7.7 `op_s4_pack_compiler`
Must prove:
- can compile final target/scene output coherently
- can build manifests from raw + evaluated layers
- can produce both final outputs
- pack validates against `s4.research_pack.v1`

---

## 8. Required artifact set for prototype success

The prototype should not count as proven unless at minimum these artifacts exist:

- supervisor bootstrap input
- `s4_research_intake.json`
- `research_batch_manifest.json`
- one `target_research_brief.json`
- one `candidate_set.json`
- one `evaluated_candidate_set.json`
- `compiled/coverage_report.json`
- `compiled/s4_research_pack.json`
- `compiled/s4_sector_report.md`
- `s4_completed.json`

Optional support artifacts may exist, but they do not replace this minimum set.

---

## 9. Validation plan

## 9.1 Validation A — intake correctness
Check:
- exactly one active target chosen for prototype path
- scene linkage exists
- schema passes

## 9.2 Validation B — brief correctness
Check:
- brief target matches intake target
- storage paths are coherent
- schema passes

## 9.3 Validation C — worker correctness
Check:
- candidate set exists
- target identity is preserved
- candidate entries have required fields
- schema passes

## 9.4 Validation D — evaluator correctness
Check:
- evaluated output joins by `candidate_id`
- overlay semantics are preserved
- best candidate selections are coherent
- schema passes

## 9.5 Validation E — coverage correctness
Check:
- target coverage exists
- scene coverage exists for linked scene(s)
- unresolved gaps/warnings fields exist
- schema passes

## 9.6 Validation F — pack correctness
Check:
- final pack exists
- sector report exists
- target and scene outputs are coherent
- manifests exist even if empty
- schema passes for final pack

## 9.7 Validation G — closure correctness
Check:
- supervisor closes only after all critical outputs exist
- completion checkpoint path is correct
- downstream resume path is deterministic

---

## 10. Suggested implementation order for the prototype

Recommended order:

1. implement minimal supervisor progression for prototype path
2. implement `op_s4_target_builder`
3. implement stub/simple `research_batch_manifest` generation in supervisor
4. implement `op_s4_web_investigator`
5. implement `op_s4_target_research_worker`
6. implement `op_s4_candidate_evaluator`
7. implement `op_s4_coverage_analyst`
8. implement `op_s4_pack_compiler`
9. wire final closure in supervisor
10. run end-to-end prototype validation

### Important note
At prototype stage, the supervisor may generate the simplest valid batch manifest possible, as long as it respects the frozen contract.

---

## 11. Recommended prototype constraints

To keep the proof clean:
- run only one target
- no worker parallelism requirement
- no batch complexity beyond a single batch with one target
- no automatic retries as a dependency for success
- no optional support artifacts required for proof

This should be a correctness-first prototype, not a feature-complete one.

---

## 12. What would count as failure of the prototype

The prototype should be considered not yet proven if any of the following happen:
- supervisor can only complete through manual intervention not captured in runtime design
- any major artifact is missing
- artifact shapes drift from schemas
- final pack exists but cannot be trusted because provenance/linkage is broken
- completion happens without valid final artifacts
- success depends mostly on conversational interpretation instead of disk-backed truth

---

## 13. Main risks during prototype

## 13.1 Overbuilding too early
Trying to make the prototype too sophisticated will hide whether the base chain actually works.

## 13.2 Weak artifact joins
The raw/evaluated/compiler relationship must remain traceable by `candidate_id` and `target_id`.

## 13.3 Supervisor overreach
If the supervisor starts doing semantic work to compensate for weak operators, the proof becomes misleading.

## 13.4 Good-looking final pack with weak provenance
A polished output is not enough.
It must still be traceable back to the correct raw/evaluated layers.

---

## 14. Exit gate for prototype

The single-target prototype is complete when:
- one target completes end to end
- all mandatory artifacts exist
- all major JSON artifacts validate
- final pack and sector report are coherent
- supervisor closure is deterministic
- the result is believable as a real sector proof, not a hand-held demo

Only after this gate should implementation move to:
**full supervisor orchestration hardening and multi-target scaling.**

---

## 15. Recommended next doc

After this document, the most useful next planning artifact is likely:
- `S4_IMPLEMENTATION_CHECKLIST.md`

That document should convert the implementation plan + foundation plan + prototype plan into a concrete execution checklist.
