# S5 Open Questions and Freeze Order

_Status: design governance note_  
_Last updated: 2026-04-07_  
_Owner: Tobias_

---

## 1. Purpose of this document

This document exists to prevent premature implementation and conceptual drift while S5 is still being defined.

Its role is to make explicit:
- what is already conceptually decided
- what remains open
- what is intentionally deferred to later versions
- what order of design freeze should be followed

This document is especially important because S5 sits at a strategic boundary:
- it is upstream of visual materialization
- it is downstream of factual grounding
- it directly shapes the future editorial freedom of the system

That means weak sequencing here would produce downstream confusion very quickly.

---

## 2. What is already decided

The following points should now be treated as conceptually established unless strong evidence forces revision.

### 2.1 Sector chain
The intended chain is:
- S4 = factual visual grounding / reference discovery
- S5 = scene kit design
- S6 = scene kit materialization
- S7 = editorial scene resolution / assembly

### 2.2 Central shift in S5
S5 should not be framed as:
- prompt writing
- image picking
- final scene resolution
- one-image-per-scene planning

S5 should be framed as:
- scene kit design
- asset-space specification per scene
- controlled balance of grounding and creative freedom

### 2.3 S4 output posture
S4 outputs are primarily:
- factual anchors
- reference inputs
- anti-hallucination support

They are not assumed to be preferred final video assets by default.

### 2.4 Global frame requirement
A global directional artifact is required before scene-level kit specs.

The conceptual object for this is:
- `video_direction_frame`

### 2.5 Scene-level boundary object
The main scene-level object should now be thought of as:
- `scene_kit_spec`

not as a narrowly framed “single-scene production plan.”

### 2.6 Asset families as primitive
The internal primitive of the scene kit should be:
- `asset_families[]`

rather than prematurely rigid one-asset slots.

### 2.7 S6 constraint awareness
The boundary must include practical production constraints such as:
- `allowed_generation_modes`
- `motion_policy`
- `motion_allowed` (deterministically injected rather than freely authored by the S5 LLM)
- `kit_complexity_ceiling`

### 2.8 V1 simplicity rule
V1 should remain simpler than the maximum richness theoretically available.

The boundary should optimize for:
- stability
- legibility
- inspectability
- downstream usefulness

not maximum semantic density.

---

## 3. Highest-priority open questions

The following questions still need disciplined treatment.

---

## 3.1 What is the minimum viable `scene_kit_spec`?

This is the most important unresolved design question.

The team still needs to freeze:
- which fields are essential in V1
- which should remain free-text
- which should be constrained enums
- which should be postponed

The danger is over-designing too early.

---

## 3.2 What is the minimum viable grammar of `asset_families[]`?

Open questions include:
- how many family roles exist in V1
- how family purpose should be expressed
- how asset counts should be modeled
- how grounding vs freedom should be represented
- how reference inputs should be attached

This must be strong enough to drive S6 but simple enough to remain consistent.

---

## 3.3 What exactly should `video_direction_frame` control in V1?

It is already decided that this artifact should exist.
What remains open is its exact scope.

V1 likely needs it to control:
- global style posture
- grounding baseline
- tonal coherence
- generation mode allowance
- budget posture
- deterministic motion policy

What remains open is whether anything more is needed at this stage.

---

## 3.4 How should grounding be expressed at family level?

Open questions:
- is `grounding_strength` enough?
- does the model also need a separate identity-integrity concept per family?
- should family-level preserve requirements be mandatory or optional?
- how much reference trace detail is useful at spec time vs delivery time?

---

## 3.5 What should S6 be allowed to decide autonomously?

This is a strategic boundary question.

The system still needs to clarify:
- how tightly S6 should follow family guidance
- how much latitude S6 has in producing variants
- whether S6 may exceed target asset counts when useful
- whether S6 may downgrade family ambition under constraints

This matters because S6 should be an executor, but not a blind serializer of impossible requests.

---

## 3.6 What exactly should S7 receive beyond files?

The conceptual package `scene_editorial_input` is useful, but still loose.

Questions remain around:
- what metadata is essential for editorial choice
- how much scene intent should remain visible downstream
- whether editorial affordances should be standardized in V1 or remain lightweight

---

## 3.7 How should examples be used to validate the boundary?

The concept needs stress-test examples.

Open questions include:
- how many examples are enough for V1
- which scene types should be mandatory
- whether examples should be embedded in concept docs or live in a separate examples doc

---

## 4. Questions intentionally deferred to V2+

The following topics should not block the V1 conceptual freeze.

### 4.1 Deep cross-scene continuity modeling
Examples:
- exact continuity graphs
- explicit scene-to-scene visual inheritance rules
- multi-scene anchor networks

### 4.2 Full editorial rhythm modeling
Examples:
- timing-use enums per asset family
- dense cut-pattern prediction
- highly structured pacing grammars
- scene-level motion strategy authored freely by the LLM beyond deterministic system policy

### 4.3 Final schema hardening
Examples:
- final JSON Schema files
- strict required/optional freeze
- full validator implementation

### 4.4 Runtime and materialization topology
Examples:
- which S5 functions become agents vs helpers
- execution substrate
- checkpointing model
- CLI invocation patterns
- exact OpenClaw agent materialization requirements (beyond creating workspaces/docs)
- runtime coupling between S5 and `b2_director`

### 4.5 Final S6 tool contracts
Examples:
- exact Freepik operator split
- exact Higgsfield integration contracts
- provider-specific retry logic

### 4.6 Final S7 editing contract
Examples:
- exact scene assembly object model
- exact edit-decision recording
- final timeline composition protocol

These are important, but premature at the current stage.

---

## 5. Freeze order

The order of freeze matters.
The recommended order is:

### Freeze 1 — conceptual boundary philosophy
Already in progress.
Freeze:
- S4/S5/S6/S7 chain
- scene kit framing
- grounding-first but not direct-use-by-default posture

### Freeze 2 — `video_direction_frame` V1
Freeze:
- what global posture fields exist
- what production constraints it carries
- how budget/allowed generation modes are expressed

### Freeze 3 — `scene_kit_spec` V1
Freeze:
- minimum scene-level object
- minimum family grammar
- minimum grounding/freedom expression
- minimum editorial guidance posture

### Freeze 4 — stress-test examples
Freeze by testing concept against:
- person-centered factual scene
- location/architecture scene
- symbolic/evocative scene
- transition-oriented scene

### Freeze 5 — `scene_kit_delivery` and `scene_editorial_input`
Freeze:
- what S6 must report back
- what S7 needs to consume
- what metadata is actually necessary downstream

### Freeze 6 — discuss internal S5 runtime architecture
Now that the conceptual boundary is substantially stronger, the next freeze layer is the internal S5 runtime architecture.
This discussion should focus on:
- actor map
- helpers / substrate layout
- orchestration boundaries
- runtime layout
- contracts and schemas
- OpenClaw agent materialization requirements
- integration with `b2_director`

This freeze should still happen before implementation, but it no longer needs to wait for every later downstream detail to be fully settled.

---

## 6. Anti-scope-creep rules

To keep the design process healthy, the following rules should be enforced.

### 6.1 Do not freeze runtime before boundary
No implementation topology should be treated as canonical before the boundary is strong.

### 6.2 Do not freeze schemas before object shape is stable
Formal schema work should lag conceptual agreement, not lead it.

### 6.3 Do not add enum richness without a real downstream consumer
A field should not become a detailed enum system unless it clearly improves materialization or editorial consumption.

### 6.4 Do not let V1 become a disguised V2
If a feature mainly serves future refinement rather than immediate clarity, it should likely wait.

### 6.5 Do not confuse creative openness with under-specification
The scene kit model should open editorial freedom, but still remain structured and inspectable.

---

## 7. Recommended immediate next steps

The immediate next steps are now:

1. consolidate the post-review S5 decisions into the docs
2. freeze the provisional runtime architecture of S5
3. clarify the exact S5 -> S6 output / handoff model
4. define the real OpenClaw materialization model for supervisor + operators
5. define how `b2_director` expands from `S3 -> S4` into `S3 -> S4 -> S5`
6. only then freeze the phased implementation plan

The conceptual boundary is already strong enough that implementation discussion is now appropriate — but only after these runtime-facing design questions are explicitly frozen.

---

## 8. Summary

S5 is now on a substantially stronger path.
The conceptual boundary is no longer the main bottleneck.

The new risk is not conceptual vagueness, but weak runtime freezing.
So the right move now is to:
- preserve the conceptual simplicity of V1
- freeze the runtime architecture carefully
- clarify S5 outputs and downstream handoff
- clarify real OpenClaw agent materialization
- clarify `b2_director` integration
- only then move into phased implementation
