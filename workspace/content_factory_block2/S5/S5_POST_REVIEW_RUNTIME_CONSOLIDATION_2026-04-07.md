# S5 Post-Review Runtime Consolidation — 2026-04-07

_Status: runtime consolidation checkpoint_
_Last updated: 2026-04-07_
_Owner: Tobias_

---

## 1. Purpose of this document

This document consolidates the S5 decisions that emerged **after** the main conceptual boundary work.

It exists to capture the post-review runtime direction that was clarified through:
- deeper Tobias/Lucca discussion
- correction of the initial “supervisor too monolithic” runtime intuition
- review and challenge with Claude Code
- comparison against the real S4 implementation style

This is **not yet** the final implementation plan.
It is the checkpoint that freezes the current runtime direction before further discussion on:
- S5 -> S6 outputs
- real OpenClaw agent materialization
- `b2_director` integration
- phased implementation planning

---

## 2. What remains unchanged from the earlier S5 work

The post-review discussion did **not** change the conceptual identity of S5.

The following remain strong and valid:
- S5 is a **scene kit design** sector
- S5 sits between S4 grounding/reference discovery and S6 materialization
- the main boundary objects remain `video_direction_frame` and `scene_kit_spec`
- `asset_families[]` remain the correct primitive
- `family_type + family_intent` remains the correct production-facing language
- `scene_summary` and `narrative_function` remain semantically derived fields
- `motion_allowed` remains a deterministic system-injected field

So the post-review work should be understood as a **runtime-layer consolidation**, not a conceptual redesign.

---

## 3. Main runtime correction

A key runtime correction emerged during discussion.

### Earlier runtime intuition that proved too weak
A first operational intuition leaned toward:
- one supervisor
- almost everything else in substrate/helpers

This is now considered too weak for the real cognitive and operational load of S5.

### Stronger current runtime direction
The preferred provisional runtime shape is now:

- **1 supervisor OpenClaw**
- **1 real operator OpenClaw**
- **helper-direct Python layers for the more deterministic phases**
- **Python substrate/helpers used strongly underneath the sector**

This is now considered the best balance between:
- avoiding swarm over-materialization
- avoiding a supervisor monolith
- not materializing OpenClaw actors for phases that are mostly deterministic + one LLM call
- preserving one real semantic operator where scene-level creative judgment is materially valuable
- keeping deterministic/runtime control where it belongs

---

## 4. Current preferred actor/runtime map

### 4.1 Supervisor
`sm_s5_scene_kit_design`

Role:
- owns sector flow
- runs preflight
- dispatches helper-direct phases and the scene-kit operator
- manages checkpoints/status
- compiles final sector outputs
- decides completion/failure
- prepares downstream handoff

This supervisor should **not** absorb all semantic work directly.
It should remain the operational owner of the sector, not a semantic monolith.

---

### 4.2 Helper-direct phase 1
`input_assembly.py`

Role:
- transforms distributed upstream artifacts into normalized per-scene S5 input packages

Expected responsibilities:
- load scene/source layer
- gather S3 grounding
- resolve S4 scene -> target -> reference-ready asset linkage
- semantically derive `scene_summary` and `narrative_function`
- deterministically derive `motion_allowed` and other policy-driven scene fields
- emit normalized `scene_direction_input_package` outputs

This phase is now preferred as helper-direct because it is mostly deterministic orchestration plus a narrow semantic derivation step.

---

### 4.3 Helper-direct phase 2
`direction_frame_builder.py`

Role:
- produces the global `video_direction_frame`

Expected responsibilities:
- load/normalize global video context
- establish grounding baseline
- establish style posture
- establish allowed generation modes
- establish motion policy / complexity ceiling / other video-level constraints
- write `video_direction_frame.json`

This phase is now preferred as helper-direct because it is mainly context gathering plus one LLM call.

---

### 4.4 OpenClaw operator
`op_s5_scene_kit_designer`

Role:
- produces `scene_kit_spec` artifacts from scene packages + global frame

Expected responsibilities:
- load a normalized scene package
- load the global frame
- design the scene kit
- populate scene direction / kit strategy / `asset_families[]` / delivery expectations
- validate or retry when output is structurally inadequate
- write per-scene `scene_kit_spec` outputs

This remains the semantic core of the sector and the strongest candidate for a real OpenClaw operator.

---

## 5. What the post-review explicitly rejects

The post-review discussion also clarified several things that should **not** be done.

### 5.1 No swarm of micro-agents
The sector should not be decomposed into many narrowly-scoped OpenClaw actors.

### 5.2 No supervisor monolith
The supervisor should not own every semantic responsibility directly.

### 5.3 No helper over-fragmentation
The helper layer should not explode into many small files that mirror every tiny conceptual sub-step.

### 5.4 No pseudo-intelligent mega-helper
There should not be a `mega_s5_brain.py`-style substrate that invisibly absorbs all sector intelligence.

### 5.5 No per-field micro-helper sprawl
Helpers should not be split into one file per tiny field or one file per tiny semantic sub-decision.

### 5.6 No premature semantic reconciler
A heavy cross-scene semantic reconciler should not be created early unless real runtime evidence later shows it is necessary.

---

## 6. Runtime layering model

The current preferred runtime layering is:

### A. OpenClaw agents
Used for:
- supervisor
- the scene-kit designer operator

These actors should use:
- `GPT-5.4-mini`
- via the already-working OpenClaw/Codex auth path
- not via new direct API key coupling for the agents themselves

### B. Python deterministic substrate
Used for:
- path resolution
- artifact IO
- checkpoint/status writing
- deterministic linkage
- policy application
- schema validation
- compile/final aggregation support
- session cleanup before each run
- bootstrap loading/parsing

### C. Python-controlled LLM calls
Used for:
- semantic derivation in input assembly
- `video_direction_frame` generation
- `scene_kit_spec` generation
- controlled retry/refinement when necessary

The current preferred plan is for these non-agent semantic calls to use:
- MiniMax M2.7 via the token plan
- through an OpenAI-compatible SDK wrapper

This is a strong provisional direction, but not yet an irrevocable final quality-approved standard.

---

## 7. Helper layer — consolidated direction

An earlier helper inventory draft mapped responsibilities well, but was too fragmented as a real file/module layout.

The current preferred direction is to keep the helper layer **consolidated and pragmatic**, more in line with the successful S4 pattern.

### Current preferred shape

#### Shared
- `paths.py`
- `artifact_io.py`
- `checkpoint_writer.py`
- `schema_validator.py`
- `llm_client.py`
- `bootstrap_loader.py` (or equivalent integrated bootstrap parser)

#### Input assembler
- `input_assembly.py`

#### Video direction frame builder
- `direction_frame_builder.py`

#### Scene kit designer
- `scene_kit_generator.py`

This should be treated as the current preferred runtime shape of the substrate/helpers.
It is still provisional, but materially stronger than the earlier over-fragmented helper map.

---

## 8. Dispatch and completion pattern

The S4 implementation style was explicitly checked before carrying assumptions into S5.

The relevant confirmation is:
- S4 does **not** use `dispatch_helpers.py`
- S4 does **not** use `completion_evaluator.py`
- operator dispatch is done inline in the supervisor
- completion is decided from artifact existence + schema validation + explicit completion writing

So the current preferred S5 direction is:
- do **not** create `dispatch_helpers.py`
- do **not** create `completion_evaluator.py`
- follow the simpler S4-style inline dispatch/completion pattern unless real complexity later proves otherwise

This matters because it reduces the risk of inventing unnecessary runtime abstractions.

---

## 9. Model routing direction

### 9.1 OpenClaw agents
Supervisor + scene-kit operator:
- `GPT-5.4-mini`
- via the already-configured OpenClaw/Codex auth route

### 9.2 Python+LLM calls
For semantic generation outside the agents themselves:
- MiniMax M2.7
- via Token Plan Plus High-Speed
- through an OpenAI-compatible client/wrapper

Likely target uses:
- `scene_summary`
- `narrative_function`
- `video_direction_frame`
- `scene_kit_spec`

### 9.3 Important caveat
MiniMax should currently be treated as:
- the preferred provisional semantic engine for the Python layer

but **not yet** as a permanently approved default for all noble S5 semantic tasks until quality is tested on real examples.

---

## 10. Scene kit generation granularity

A major runtime question surfaced during review:
- how should `op_s5_scene_kit_designer` iterate scenes?

The current strongest provisional direction is:
- **small batches** rather than one huge all-scenes call
- and also rather than forcing one giant actor turn that tries to design the whole video at once

This direction is currently preferred because it should better balance:
- semantic quality
- latency
- cost
- practical throughput

The exact batch size remains open and should be explicitly frozen later.

---

## 11. What is now strong enough to treat as the current base

The following can now be treated as the current best runtime basis for S5:
- S5 should use `1 supervisor + 1 OpenClaw operator + helper-direct phases`
- helper/substrate layout should be consolidated, not fragmented
- dispatch/completion should follow the simpler S4 style
- OpenClaw actors should use `GPT-5.4-mini`
- Python+LLM semantic calls should provisionally target MiniMax M2.7 via token plan
- `llm_client.py` should include Semaphore(10) + retry/backoff from day 1
- session cleanup should be treated as mandatory before each run
- scene kit generation should likely use small batches

These points are now stronger than loose brainstorm status.

---

## 12. What still remains open after this consolidation

This post-review runtime checkpoint does **not** close the following topics:

### 12.1 Exact final module layout and implementation topology
Still open:
- final helper file layout freeze
- final supervisor-shell/substrate implementation shape
- exact proof sequence for runtime materialization

### 12.2 Final implementation phase plan
Still open:
- the exact phased implementation plan and gates
- exact proof strategy
- exact quality gate for MiniMax

The following topics are no longer fully open at the same level they were before this checkpoint:
- S5 -> S6 output / handoff posture now has a preferred truth hierarchy
- B2 ↔ S5 macro integration now has a preferred contract shape
- S5 agent materialization now has a preferred standardization direction

---

## 13. Summary

S5 is no longer blocked mainly by conceptual ambiguity.

The new centre of gravity is:
- runtime architecture freeze
- downstream output/handoff clarification
- real OpenClaw materialization design
- B2 integration design

The key post-review correction is:

> S5 should not be a supervisor monolith, and it should not be a micro-agent swarm.
> The current best shape is a small real actor map with strong consolidated Python substrate underneath it.
