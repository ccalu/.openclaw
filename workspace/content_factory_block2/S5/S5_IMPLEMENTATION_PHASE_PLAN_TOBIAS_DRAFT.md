# S5 Implementation Phase Plan — Tobias Draft

_Status: draft for review before freeze_
_Last updated: 2026-04-07_
_Owner: Tobias_

---

## 1. Purpose of this document

This document proposes the phased implementation plan for S5.

It is intentionally written as a **Tobias draft**, not yet the final frozen implementation plan.
Its role is to:
- convert the now-mature S5 documentation into an execution sequence
- reduce architectural rediscovery during implementation
- define proof gates before the sector is treated as operationally real
- provide a reviewable plan for Claude Code before implementation freeze

This document should be reviewed for:
- practical execution efficiency
- hidden dependencies
- over-validation risk
- unnecessary phase fragmentation
- missing proof steps

---

## 2. Implementation objective

The objective of the implementation phase is not just to “code S5”.
The real objective is:

> implement S5 in a way that is operationally robust, checkpoint-valid, B2-compatible, semantically strong, and materially easier to execute than the S4 implementation cycle.

This means the plan should optimize for:
- clarity of sequencing
- proof-by-gates
- low architectural drift during execution
- low risk of false progress
- reuse of the validated S4/B2 runtime pattern where appropriate

---

## 3. Frozen assumptions this plan depends on

This phase plan assumes the following are already strong enough to act as implementation base:

### 3.1 Sector identity
- S5 = scene kit design
- not single-image planning
- not direct materialization
- not final editorial resolution

### 3.2 Runtime actor map
- `sm_s5_scene_kit_design` = OpenClaw supervisor
- `input_assembly.py` = helper-direct phase
- `direction_frame_builder.py` = helper-direct phase
- `op_s5_scene_kit_designer` = OpenClaw operator
- compile + validators = helper-direct

### 3.3 Model routing
- OpenClaw actors use `GPT-5.4-mini`
- Python+LLM calls use MiniMax M2.7 via token plan as provisional default
- `llm_client.py` should use `Semaphore(10)` + retry/backoff
- GPT-5.4-nano remains fallback if MiniMax quality is not sufficient

### 3.4 Output contract
Canonical truth layer:
- `video_direction_frame.json`
- `scene_kit_specs/<scene_id>.json`

Derived downstream handoff:
- `s5_scene_kit_pack.json`

### 3.5 B2 integration
- `b2_director` writes `s5_requested.json`
- boundary launches `sm_s5_scene_kit_design`
- S5 writes `s5_completed.json` / `s5_failed.json`
- `b2_director` validates declared handoff paths and readiness before opening S6

---

## 4. Phase design principle

Each phase in this plan should prove one concrete thing.

A phase should define:
- what is being made real
- what artifact or runtime behaviour proves it
- what failure means
- what should explicitly not be solved yet

This plan should avoid:
- vague phases
- implementation by intuition
- over-validation of everything at once
- mixing proof-of-runtime with proof-of-quality without distinction

---

## 5. Phase 0 — implementation freeze checkpoint

### Objective
Start implementation only after confirming that the current docs are strong enough to serve as execution substrate.

### This phase confirms
- actor map is stable enough
- helper layout is stable enough
- output posture is stable enough
- B2 ↔ S5 contract is stable enough
- agent materialization expectations are stable enough
- key operational requirements from review are documented

### Gate
Proceed only if there is no remaining major architectural ambiguity on:
- actor map
- output truth hierarchy
- B2 handoff contract
- helper-direct vs OpenClaw split

### Main risk
Starting implementation while still redesigning the sector structure.

### Explicitly not solved here
- no code implementation yet
- no performance tuning yet

---

## 6. Phase 1 — shared substrate foundation

### Objective
Create the shared substrate and filesystem layout that the whole sector will rely on.

### Scope
Implement the shared layer:
- `paths.py`
- `artifact_io.py`
- `checkpoint_writer.py`
- `schema_validator.py`
- `llm_client.py`
- `bootstrap_loader.py` (or integrated equivalent if chosen explicitly)

Establish canonical folders such as:
- `compiled/`
- `scene_kit_specs/`
- `scene_direction_input_packages/`
- `runtime/`
- `checkpoints/`

### Must prove
- canonical paths are centralized
- read/write behavior is stable
- checkpoint writing works
- shared validation hooks exist
- MiniMax client wrapper exists with semaphore + retry/backoff

### Gate
Phase passes when:
- the substrate can initialize a sector run root cleanly
- paths do not depend on ad hoc reconstruction
- runtime/control files can be written and read deterministically

### Main risk
Letting path and IO drift start early and contaminate later phases.

### Explicitly not solved here
- no scene understanding yet
- no scene-kit generation yet
- no B2 full resume proof yet

---

## 7. Phase 2 — real materialization of S5 OpenClaw agents

### Objective
Materialize the two real S5 OpenClaw actors as actual runtime agents.

### Scope
Create and validate:
- `sm_s5_scene_kit_design`
- `op_s5_scene_kit_designer`

Each must have:
- `IDENTITY.md`
- `MISSION.md`
- `CONTEXT.md`
- `CONTRACT.md`
- `OPERATIONS.md`

### Must prove
- folders exist
- runtime recognizes them as real agents
- each agent executes at least one real narrow turn coherently

### Gate
An agent only passes when:
- local workspace exists
- runtime recognition exists
- a real turn runs successfully

### Main risk
Mistaking nice local docs for real runtime materialization.

### Explicitly not solved here
- no semantic quality proof yet
- no end-to-end sector proof yet

---

## 8. Phase 3 — supervisor bootstrap and macro sector contract

### Objective
Make the supervisor real as the external face of the sector.

### Scope
Implement in the supervisor path:
- bootstrap ingestion
- upstream path validation
- status/checkpoint initialization
- `s5_completed.json` writing path
- `s5_failed.json` writing path
- B2 checkpoint mirror path
- session cleanup requirement before each run

### Must prove
- supervisor can ingest real S5 bootstrap payload
- required upstream paths are validated explicitly
- completion/failure checkpoints can be emitted in the agreed macro shape

### Gate
Phase passes when:
- supervisor starts from real bootstrap
- refuses invalid upstream cleanly
- writes correct sector-level completion/failure shape

### Main risk
Building internal runtime before the supervisor is actually B2-compatible.

### Explicitly not solved here
- no full scene-kit production yet
- no quality evaluation yet

---

## 9. Phase 4 — input assembly proof

### Objective
Prove the helper-direct `input_assembly.py` phase on real upstream data.

### Scope
Implement and prove:
- source package load
- S3 grounding load
- S4 reference linkage
- semantic derivation of `scene_summary`
- semantic derivation of `narrative_function`
- deterministic derivation of `motion_allowed`
- normalized package write to `scene_direction_input_packages/`

### Test slice
Use a deliberately mixed subset of scenes:
- factual person-centered
- location/architecture
- symbolic
- transition-oriented
- at least one low-reference or zero-reference scene

### Must prove
- packages are structurally valid
- scene linkage is correct
- semantic fields are useful
- low-reference regime does not collapse

### Gate
Phase passes when:
- packages are usable for downstream scene-kit design
- deterministic fields are correct
- reference linkage does not drift from canonical S4 truth

### Main risk
Producing structurally neat packages that are semantically weak or operationally misleading.

### Explicitly not solved here
- no full video run yet
- no sector compile yet

---

## 10. Phase 5 — video direction frame proof

### Objective
Prove the helper-direct `direction_frame_builder.py` phase.

### Scope
Implement and prove:
- global context load
- global constraint normalization
- generation of `video_direction_frame.json`
- structural validation of the frame

### Must prove
- the frame is usable, not generic
- the frame enforces coherent video-level posture
- `allowed_generation_modes[]` and `motion_policy` are represented correctly

### Gate
Phase passes when:
- `video_direction_frame.json` is valid and operationally useful
- it constrains the sector rather than merely describing mood

### Main risk
Generating a frame that sounds good but is too vague to constrain scene-kit design.

### Explicitly not solved here
- no full scene-kit output yet
- no optimization of wording beyond operational sufficiency

---

## 11. Phase 6 — MiniMax quality gate

### Objective
Decide whether MiniMax M2.7 is genuinely strong enough for the semantically important Python-controlled steps.

### Scope
Test real outputs for:
- `scene_summary`
- `narrative_function`
- `video_direction_frame`
- 3 to 5 real `scene_kit_spec` generations

### Must prove
- Portuguese semantic quality is sufficient
- family design is not generic
- grounding sensitivity is good enough
- low-reference behavior remains coherent

### Gate
MiniMax passes if outputs are:
- semantically solid
- structurally usable
- not clearly weaker than acceptable downstream standards

If MiniMax fails:
- define fallback before committing to full sector implementation on it

### Main risk
Locking the implementation to a low-cost model path before proving semantic adequacy.

### Explicitly not solved here
- no throughput optimization yet
- no provider benchmark theater beyond what is operationally needed

---

## 12. Phase 7 — scene kit designer proof

### Objective
Prove the OpenClaw `op_s5_scene_kit_designer` on real scene packages.

### Scope
Implement and prove:
- package + frame ingestion
- `scene_kit_spec` generation
- schema/structure validation
- retry/refinement if needed
- write to `scene_kit_specs/<scene_id>.json`

### Test slice
Use the same scene classes used earlier, including:
- factual person-centered
- location/architecture
- symbolic
- transition-oriented
- low-reference / zero-reference

### Must prove
- `family_type + family_intent` is strong
- scene kits remain open enough for S6/S7
- factual grounding is preserved where needed
- weak-reference scenes still get viable minimum families

### Gate
Phase passes when:
- specs are structurally valid
- semantically useful
- operationally credible as S6 inputs

### Main risk
Mistaking schema-valid output for truly usable scene-kit direction.

### Explicitly not solved here
- no whole-video batching decision yet
- no final sector compile yet

---

## 13. Phase 8 — batching strategy proof

### Objective
Freeze the practical scene batching strategy for the `op_s5_scene_kit_designer`.

### Scope
Test and compare at least:
- one-scene calls
- small batches (3–5)
- larger small batches (5–10)

### Must prove
- quality remains strong
- context windows stay stable
- runtime remains predictable
- batching does not degrade grounding or family quality

### Gate
Choose one batch strategy only after it proves the best tradeoff on:
- quality
- predictability
- latency
- implementation simplicity

### Main risk
Choosing a batching strategy based on intuition rather than runtime evidence.

### Explicitly not solved here
- no production-scale concurrency tuning yet

---

## 14. Phase 9 — sector compile and output contract proof

### Objective
Make S5 finish as a clean sector with canonical truth artifacts and a valid downstream handoff surface.

### Scope
Implement and prove:
- compile of `video_direction_frame.json`
- compile/index of `scene_kit_specs/`
- build of `s5_scene_kit_pack.json`
- write of `s5_sector_report.md`
- readiness counts and readiness flag
- write of `s5_completed.json`

### Must prove
- canonical truth layer exists and is inspectable
- compiled pack exists and remains derived
- the S5 completion contract is real, not hypothetical

### Gate
Phase passes when:
- completion artifacts are correct
- truth hierarchy is preserved
- B2-facing macro handoff is structurally valid

### Main risk
Letting the compiled pack silently become competing truth.

### Explicitly not solved here
- no actual S6 consumption yet

---

## 15. Phase 10 — B2 resume and handoff proof

### Objective
Prove the real macro integration of S5 inside the B2 runtime pattern.

### Scope
Prove the full macro chain:
- `b2_director` resumes from `s4_completed.json`
- director writes `s5_requested.json`
- boundary launches `sm_s5_scene_kit_design`
- S5 runs and writes `s5_completed.json`
- boundary reactivates `b2_director`
- director validates S5 handoff paths and readiness
- director is able to open S6 next

### Must prove
- S5 uses the validated B2 pattern rather than special-case glue
- B2 does not need knowledge of internal S5 topology

### Gate
Phase passes when:
- B2 ↔ S5 macro integration works through checkpoints and declared paths only
- no hacky hidden dependency is needed

### Main risk
Creating a superficially integrated sector that actually depends on ad hoc coupling.

### Explicitly not solved here
- no full S6 implementation yet

---

## 16. Phase 11 — narrow E2E S3 -> S4 -> S5 proof

### Objective
Run the first narrow real chain that reaches `s5_completed` inside B2.

### Scope
Prove:
- upstream real artifacts from earlier sectors
- S5 runtime entry through B2
- real scene-kit artifacts on disk
- correct completion and reentry behavior

### Must prove
- S5 is no longer only locally valid
- it behaves correctly inside the real block progression

### Gate
Phase passes when:
- the chain reaches `s5_completed`
- artifacts are coherent
- director sees valid readiness for S6

### Main risk
Only discovering hidden inter-sector mismatch at the very end.

### Explicitly not solved here
- no final production-hardening yet

---

## 17. Phase 12 — hardening before S6 opening

### Objective
Consolidate S5 into a reusable, stable sector before opening S6 implementation.

### Scope
- document remaining runtime refinements
- tighten validators where needed
- confirm final model route
- confirm session hygiene discipline
- confirm run isolation discipline
- confirm no major contract ambiguity remains in S5 -> S6

### Must prove
- S5 can be treated as stable substrate for the next sector
- the next sector will not need to reopen S5 architecture casually

### Gate
S5 should only be treated as ready for S6 opening when:
- runtime behavior is predictable
- quality gate has passed
- B2 integration is stable
- output contract is inspectable and trustworthy

### Main risk
Opening S6 while S5 is still semantically or operationally unstable.

---

## 18. What this plan explicitly tries to avoid

### 18.1 Re-learning architecture during implementation
The main purpose of the doc set is to reduce this.

### 18.2 Over-validating everything at once
Each phase should prove one thing clearly.

### 18.3 Confusing “agent created” with “agent real”
Runtime recognition + real turn remain required.

### 18.4 Confusing schema validity with semantic quality
Semantic gates are explicitly separate from structural gates.

### 18.5 Opening S6 on top of an unstable S5
The plan intentionally keeps a hardening phase before the next sector opens.

---

## 19. Suggested review questions for Claude Code

This draft should be reviewed for the following:

1. Is the phase order practical for actual implementation?
2. Are any phases too fragmented or too merged?
3. Is there any hidden dependency missing from the sequence?
4. Is there any place where this draft still over-validates relative to the S4 lessons?
5. What is the minimal robust path from this draft to runtime proof?

---

## 20. Summary

This draft proposes an implementation sequence where S5 becomes real in the following order:
- substrate foundation
- real OpenClaw materialization of the supervisor and single semantic operator
- supervisor/B2 macro compatibility
- proof of helper-direct phases
- quality gate for MiniMax
- proof of scene-kit design
- batching proof
- sector compile proof
- B2 integration proof
- narrow end-to-end proof
- hardening before S6 opening

This is intentionally not yet the final frozen plan.
It is the Tobias draft that should now be reviewed against practical execution reality before freeze.
