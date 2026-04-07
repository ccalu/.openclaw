# S4 — Agent Materialization Plan

_Status: implementation planning draft_
_Last updated: 2026-04-04_
_Owner: Tobias_
_Sector: S4 — Asset Research_

---

## 1. Purpose

This document freezes the next transition layer of S4:
from a sector-local functional pipeline into progressively materialized real OpenClaw actors.

It exists to prevent drift during agent materialization.

The goal is **not** to re-architect S4.
The goal is to define:
- materialization order
- bridge rules
- what remains deterministic Python substrate
- what becomes agent responsibility
- proof gates before progressing

---

## 2. Current state before this phase

Before this phase starts, the following are already considered materially proven:
- S4 architecture layer
- contracts/schemas layer
- foundation layer
- single-target prototype (Phase 2A)
- Brave-first discovery integration (3A)

This means S4 already exists as a functioning sector-local pipeline.
What is missing is the progressive conversion of that pipeline into real OpenClaw actor materialization.

---

## 3. Core principle

Agent materialization must be incremental.

Do **not** attempt to materialize all S4 actors at once.
Do **not** move deterministic substrate into prompt/agent logic by accident.
Do **not** turn helper-backed runtime mechanics into vague conversational behavior.

The correct pattern is:
- freeze the substrate
- materialize one actor layer at a time
- prove that actor in runtime
- move to the next actor only after the gate is satisfied

---

## 4. Two-stage materialization model

## 4.1 M1 — supervisor materialization

First materialize:
- `sm_s4_asset_research`

Goal:
- make the sector supervisor a real OpenClaw actor
- replace the temporary supervisor shell launch path with real supervisor agent invocation
- prove boot + first dispatch under real actor runtime

This is the anchor of the whole phase.

## 4.2 M2 — operator materialization

After supervisor materialization is proven, materialize operators progressively in this order:
1. `op_s4_target_builder`
2. `op_s4_web_investigator`
3. `op_s4_target_research_worker`
4. `op_s4_candidate_evaluator`
5. `op_s4_coverage_analyst`
6. `op_s4_pack_compiler`

Do not materialize operators in parallel by default.
Materialize one, prove one, then continue.

---

## 5. Recommended materialization order and rationale

## 5.1 `sm_s4_asset_research`
First because it is the sector dispatch hub.
Without it, no other actor can be proven in real sector context.

## 5.2 `op_s4_target_builder`
First operator and lowest-risk semantic transition.
It converts S3 upstream output into S4 intake.

## 5.3 `op_s4_web_investigator`
Second operator, produces target research briefs.
It remains bounded and easier to validate than the worker.

## 5.4 `op_s4_target_research_worker`
More operationally complex because it touches Brave/Firecrawl and candidate assembly.
Should only be materialized after the first two operators are stable.

## 5.5 `op_s4_candidate_evaluator`
Semantic core of candidate judgment.
Should be materialized only after candidate discovery is already stable.

## 5.6 `op_s4_coverage_analyst`
Can initially wrap deterministic coverage substrate, but must still be proven as a distinct actor.

## 5.7 `op_s4_pack_compiler`
Last because it depends on all previous outputs and should remain tightly constrained.

---

## 6. What remains helper/substrate Python

The following should remain deterministic Python substrate unless a later explicit decision changes that:

- `paths.py`
- `dirs.py`
- `artifact_io.py`
- `schema_validator.py`
- `checkpoint_writer.py`
- Brave Search API adapter(s)
- Firecrawl adapter(s)
- deterministic coverage heuristic implementation
- deterministic path/manifest/bootstrap mechanics

### Why
These are infrastructure and runtime mechanics.
They should remain auditable, deterministic, and not drift into agent prompt behavior.

---

## 7. What becomes agent responsibility

## 7.1 `sm_s4_asset_research`
Agent owns:
- sector-level orchestration
- dispatch sequencing
- artifact gate checks
- closure decisions

Helper/substrate continues to own:
- checkpoint writing
- schema validation
- path and IO mechanics

## 7.2 `op_s4_target_builder`
Agent owns:
- target mapping judgment
- target framing
- type normalization decisions that require semantic reading

Helper/substrate owns:
- output writing
- path derivation
- schema validation

## 7.3 `op_s4_web_investigator`
Agent owns:
- search intent planning
- research framing
- query direction / discovery planning

Helper/substrate owns:
- artifact writing
- path handling

## 7.4 `op_s4_target_research_worker`
Agent owns:
- retrieval strategy
- search decision logic
- interpretation of search results into candidate assembly

Helper/substrate owns:
- Brave API execution
- Firecrawl execution
- artifact writing
- path handling

### Important guardrail
The worker may perform preliminary triage, but the canonical semantic classification of candidates must remain separate and belong to the evaluator.

## 7.5 `op_s4_candidate_evaluator`
Agent owns:
- semantic candidate classification
- factual vs visual vs stylistic vs reject judgment
- best-candidate judgments

Helper/substrate owns:
- artifact IO
- schema validation

## 7.6 `op_s4_coverage_analyst`
Agent owns:
- coverage interpretation layer
- target/scene-level sufficiency review

Helper/substrate may continue to own:
- deterministic coverage heuristic implementation
- artifact writing/validation

The initial materialization may wrap the heuristic layer, but the actor identity and contract boundary must remain explicit.

## 7.7 `op_s4_pack_compiler`
Agent owns:
- constrained final compilation
- report writing under bounded rules

Helper/substrate owns:
- deterministic aggregation helpers
- IO/validation

### Important guardrail
The compiler must not become a loose summarizer that hides gaps or rewrites operational truth.

---

## 8. Bridge policy

## 8.1 Allowed bridge
After `sm_s4_asset_research` is materialized, it is acceptable for a short transition period that the supervisor dispatches some downstream steps through existing helper-backed execution paths while the corresponding operators are not yet materialized as real actors.

## 8.2 Bridge is temporary
This bridge is acceptable only as a narrow transition strategy.
It must not become the comfortable default state of the sector.

## 8.3 Bridge usage rule
If an operator is still bridge-backed:
- it must still respect the frozen contract
- it must still write canonical artifacts to disk
- the supervisor must remain explicit about what is bridge execution vs real actor execution

---

## 9. Proof gates by stage

## 9.1 Gate M1 — supervisor materialized
Must prove:
- boundary launches `sm_s4_asset_research` as real OpenClaw actor
- supervisor boots under real actor runtime
- supervisor can perform at least the first valid dispatch step
- supervisor writes expected status/checkpoints under real runtime

## 9.2 Gate M2.1 — target builder materialized
Must prove:
- real actor invocation
- valid intake artifact written
- schema passes

## 9.3 Gate M2.2 — web investigator materialized
Must prove:
- real actor invocation
- valid brief artifact written
- schema passes

## 9.4 Gate M2.3 — research worker materialized
Must prove:
- real actor invocation
- candidate set with real candidates written
- schema passes
- Brave/Firecrawl-backed retrieval still works through the new actor boundary

## 9.5 Gate M2.4 — evaluator materialized
Must prove:
- real actor invocation
- evaluated set written
- semantic classification occurs at evaluator boundary, not smeared elsewhere
- schema passes

## 9.6 Gate M2.5 — coverage analyst materialized
Must prove:
- real actor invocation
- valid coverage report written
- contract boundary remains explicit even if heuristic substrate is still used underneath

## 9.7 Gate M2.6 — pack compiler materialized
Must prove:
- real actor invocation
- final pack + sector report written
- closure artifacts remain trustworthy
- compiler does not hide unresolved gaps

---

## 10. What must NOT happen during materialization

- do not materialize all actors at once
- do not move deterministic infra into prompts by accident
- do not let the research worker absorb evaluator responsibilities
- do not let the compiler become an unconstrained summarizer
- do not treat bridge execution as acceptable permanent architecture
- do not open multi-target expansion before core actors are materially stable

---

## 11. Immediate next step

The immediate next step after this document is:

### Materialize `sm_s4_asset_research` first

That includes:
- creating the real OpenClaw actor boundary/docs/config for the supervisor
- swapping the temporary launch path to real supervisor actor launch
- proving boot + first dispatch gate under real actor runtime

Only after that should operator materialization begin.
