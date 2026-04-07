# op_s4_web_investigator

_Status: planning draft_
_Last updated: 2026-04-04_
_Actor type: operator / discovery coordinator_
_Sector: S4 — Asset Research_

---

## 1. Role

`op_s4_web_investigator` is the logical coordinator of the S4 discovery phase.

Its job is not to be the one giant researcher that personally executes the whole search workload.

Its job is to transform:
- intake-level research targets
- batch planning constraints

into:
- bounded target-level research briefs
- optional batch discovery summaries

This actor preserves the discovery-planning layer of the architecture without forcing nested runtime spawning in the critical path.

---

## 2. Core mission

Read:
- `s4_research_intake.json`
- `research_batch_manifest.json`

and produce:
- `target_research_brief.json` files for the selected targets
- optional `batch_discovery_summary.json`

so that target workers can execute focused discovery with minimal ambiguity.

---

## 3. Inputs

Primary inputs:
- `s4_research_intake.json`
- `research_batch_manifest.json`

Dispatch/runtime inputs:
- `s4.web_investigator_dispatch.v1`
- target brief output directory
- optional batch summary output directory

---

## 4. Outputs

Mandatory outputs:
- one `target_research_brief.json` per target or per bounded target batch

Optional outputs:
- `batch_discovery_summary.json`

Also expected:
- operator status/checkpoint artifact(s)

---

## 5. Responsibilities

## 5.1 Discovery decomposition
- read the active discovery batch
- determine what each target worker needs to investigate
- decompose abstract target intent into concrete search goals

## 5.2 Brief generation
- create bounded, concrete target briefs
- sharpen `research_needs` into actionable `search_goals`
- preserve target semantics without overcomplicating worker scope

## 5.3 Batch-level coherence
- ensure target briefs are consistent with the batch manifest
- preserve priorities and ordering constraints
- avoid conflicting search instructions across targets in the same batch

## 5.4 Optional batch summary generation
- write optional summary of the active batch planning/output expectations
- make it easier for supervisor/humans to inspect the discovery phase

---

## 6. What this actor must NOT do

- must not be assumed to directly spawn runtime worker processes in S4 v1
- must not absorb the actual target-level search workload in place of workers
- must not evaluate final candidate quality
- must not decide sector coverage
- must not compile the final pack

---

## 7. Important runtime clarification

This actor is a **logical discovery coordinator**, not a required runtime spawner.

That means:
- it defines the work
- it structures the briefs
- it supports the discovery hierarchy semantically

But in S4 v1:
- `sm_s4_asset_research` remains the operational dispatcher of target workers
- the runtime does not depend on investigator->worker spawn trees

This distinction is central and must not be lost.

---

## 8. Required output quality

A good `op_s4_web_investigator` output should make the worker's task:
- bounded
- concrete
- target-specific
- usable without improvising missing scope

A brief should not merely restate the target name.
It should translate the target into discoverable search intent.

---

## 9. Key risks

- writing briefs that are too vague
- writing briefs that are too broad and overload workers
- collapsing multiple search intents into confusing instructions
- accidentally behaving like a runtime spawner layer instead of a planning layer
- producing batch summaries that are treated as truth instead of support artifacts

---

## 10. Validation expectations

Supervisor should validate at minimum:
- expected brief files exist
- each brief has required fields
- target IDs match the batch manifest/intake
- output contract points to `s4.candidate_set.v1`

If optional batch summaries exist, they should be treated as support artifacts only.

---

## 11. Interfaces with other actors

### With `sm_s4_asset_research`
- receives dispatch from supervisor
- writes briefs that supervisor will later use to dispatch workers

### With `op_s4_target_research_worker`
- does not call worker directly in the baseline runtime
- prepares the brief contract that worker consumes

### With `op_s4_candidate_evaluator`
- evaluator may later read the brief to understand target intent during qualification

---

## 12. Success criteria

This actor is successful when:
- all expected target briefs are written
- each brief is concrete enough to drive bounded discovery
- workers can execute without inventing missing mission scope
- the discovery layer remains semantically rich without becoming a runtime nesting risk
