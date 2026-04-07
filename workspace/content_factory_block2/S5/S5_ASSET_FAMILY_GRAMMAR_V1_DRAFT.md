# S5 Asset Family Grammar V1 Draft

_Status: conceptual grammar draft_  
_Last updated: 2026-04-07_  
_Owner: Tobias_

---

## 1. Purpose of this document

This document proposes the preferred **V1 grammar** for `asset_families[]` inside the `scene_kit_spec` model.

Its purpose is to move the S5 design from high-level concept into a more operational object grammar without prematurely freezing final schemas.

This document specifically addresses:
- which grammar direction should be preferred for V1
- how `asset_families[]` should be structured
- how grounding-critical references should be represented
- how the grammar should support S6 materialization without over-closing S7 editorial freedom
- how to keep the model implementable and stable in V1

This draft also incorporates an important simplification:

> motion should not be freely invented by the S5 LLM in V1.

Instead, a deterministic system rule should decide whether motion is allowed for a scene.

---

## 2. Why this grammar matters

The entire scene-kit model depends on `asset_families[]` being well designed.

If the grammar is too weak:
- S6 will not know what kinds of material to produce
- S7 will receive a shallow or repetitive asset space
- the scene kit concept will collapse back toward rigid one-image thinking

If the grammar is too rich:
- LLM outputs will become inconsistent
- field usage will drift
- implementation will become slow and brittle
- V1 will over-design problems that the system is not ready to solve yet

So the goal is not maximal richness.
The goal is:

> the smallest grammar that can still express a real, grounded, editorially useful scene kit.

---

## 3. Candidate directions considered

Two directions were considered seriously for V1.

### Option B — role + function
A family carries:
- a role
- a more specific function
- plus grounding and production fields

This is compact and expressive, but it tends to overload a single family object with both production and editorial meaning at once.

### Option D — two-layer grammar
A family carries:
- a production-facing layer
- a lightweight editorial-facing layer

This is slightly more structured, but it separates concerns more cleanly and appears better aligned with the intended S5→S6→S7 chain.

---

## 4. Preferred direction for V1

The current preferred direction is:

## Option D — two-layer grammar (contained V1 version)

This means each asset family should contain:

### Layer 1 — production-facing fields
These fields are primarily for S5→S6 communication.
They define what kind of family this is, how important it is, how grounded it must be, and how it should be materialized.

### Layer 2 — lightweight editorial-facing fields
These fields provide minimal downstream usefulness for S7 without turning V1 into a full editorial grammar.

This split is attractive because it:
- keeps S6-facing structure clear
- preserves a future bridge into S7
- avoids overloading one field with both production and editorial semantics
- remains simpler than a fully editorial-first model

---

## 5. Core V1 principle: factual grounding is not optional in factual scenes

A crucial rule must be explicit in this grammar:

> when a scene depicts a real and identifiable person, place, building, city, object, weapon, vehicle, aircraft, artifact, or other factual element, the correct S4 references must be used as grounding inputs for generation.

This is not a stylistic preference.
It is a structural correctness requirement.

The reason is practical and proven:
- if the visuals drift away from the real referent
- viewers notice
- comments call out the inaccuracy
- trust degrades

That means V1 grammar must make room for:
- `reference_inputs[]`
- `preserve_requirements[]`
- grounding strength
- clear constraints against generic drift

These fields are not decorative.
They are central to the system’s factual integrity.

---

## 6. Proposed V1 grammar

Each `asset_family` should have the following structure.

---

## 6.1 Layer 1 — production-facing fields

### `family_id`
Stable identifier within the scene kit.

### `family_type`
The broad type of material this family represents.

Proposed V1 values:
- `hero`
- `support`
- `detail`
- `atmospheric`
- `transition`
- `fallback`

These values are intentionally modest.
They are expressive enough for V1 without becoming taxonomically heavy.
They also replace the need for a second competing family-role taxonomy in V1.

### `family_intent`
A short free-text statement describing the concrete mission of this family inside the scene kit.

This field is critical because `family_type` alone is too abstract for S6.
For example, `support` is not sufficiently actionable unless the system also knows support **for what**.

Examples:
- identify the central political actor of the prohibition decision
- provide institutional and decision-context visuals around the prohibition
- establish Hotel Quitandinha as the real architectural object of the ambition
- reinforce the gambling/casino reality being discussed
- keep the symbolic scene tied to the grounded world of the hotel/casino project

The combination of `family_type` + `family_intent` should be treated as the core production-facing language of the family.

### `priority`
How important this family is to the scene.

Proposed V1 values:
- `required`
- `preferred`
- `optional`

### `target_asset_count`
How many assets this family should ideally yield.

Suggested shape:
- `minimum`
- `ideal`
- `maximum`

### `grounding_strength`
How strongly the family must remain anchored to the factual world of the scene.

Proposed V1 values:
- `high`
- `medium`
- `low`

### `creative_freedom_level`
How much interpretive freedom S6 may use when materializing this family.

Proposed V1 values:
- `strict`
- `controlled`
- `moderate`
- `open`

### `preferred_generation_modes[]`
Which generation modes best fit this family.

Proposed V1 examples:
- `reference_guided_generation`
- `regeneration_from_reference`
- `from_scratch_generation`
- `multi_reference_synthesis`

These should remain under the limits of the active video-level generation policy.
In V1, `motion_generation` should not be listed here as a general mode because motion enablement is already controlled separately through `motion_policy` / `motion_allowed`.

### `reference_inputs[]`
The references from S4 or derived reference packages that should feed this family.

This field is especially important in factual scenes.
The preferred V1 shape is object-based, for example:
- `{ asset_id, source_target_id }`

This preserves traceability back into the S4 layer.

### `preserve_requirements[]`
A short list of what must remain accurate or legible if this family is generated from references.

Examples:
- facial identity
- building silhouette
- vehicle profile
- object shape
- period-accurate details

### `avoid_literal_copy_notes[]`
What should explicitly not be copied literally from the references.

Examples:
- exact source framing
- source watermark-bearing composition
- directly recognizable copyrighted layout
- source-specific visual signature

---

## 6.2 Layer 2 — lightweight editorial-facing fields

### `editorial_notes`
A lightweight free-text note on how this family is likely to be useful in the cut.

In the current preferred V1 direction, the editorial layer should remain textual rather than enum-heavy.
That means:
- no separate closed editorial role taxonomy is required yet
- no heavy editorial affordance system is required yet
- the family keeps its production-facing `family_type`
- downstream/editorial nuance is expressed through concise text

This is preferable in V1 because it is:
- easier for LLMs to generate naturally
- easier to interpret in context
- less brittle than forcing prematurely rigid editorial enums

---

## 7. Motion simplification for V1

V1 should avoid making motion a free design variable at the LLM level.

### 7.1 Current preferred policy
The preferred system-level rule is:

- `motion_policy: first_10_scenes_only`
- scenes with index `<= 10` receive `motion_allowed = true`
- scenes after that receive `motion_allowed = false`

### 7.2 Important consequence
This means:
- the S5 LLM does **not** decide motion from scratch
- `motion_allowed` should be injected deterministically by the substrate or boundary logic
- families may still prefer `motion_generation` only if the policy allows it for that scene

### 7.3 Why this simplification is good
It reduces:
- complexity
- inconsistency
- cost explosion
- unnecessary planner burden

while still enabling motion where the system most wants it.

---

## 8. Worked examples

The examples below are intentionally concrete because the grammar only becomes understandable when seen under real scene conditions.

A key clarification also applies here:
- `family_type` tells the system what broad kind of family this is
- `family_intent` tells the system what that family must actually achieve for the scene

Without `family_intent`, the grammar becomes too vague for S6 materialization.

---

## 8.1 Real person scene

### Scene
George S. Patton is introduced as the commanding force of an offensive.

### Example family
```yaml
family_id: f1
family_type: hero
family_intent: identify George S. Patton as the central military actor of the scene with high recognizability and authority
priority: required
target_asset_count:
  minimum: 1
  ideal: 2
  maximum: 2
grounding_strength: high
creative_freedom_level: controlled
preferred_generation_modes:
  - reference_guided_generation
  - regeneration_from_reference
reference_inputs:
  - asset_id: patton_face_reference_01
    source_target_id: t_patton
  - asset_id: patton_uniform_reference_02
    source_target_id: t_patton
preserve_requirements:
  - facial identity of George S. Patton
  - correct military uniform cues
avoid_literal_copy_notes:
  - avoid exact source framing
editorial_notes: Primary identity anchor for the scene; should sustain an opening or emphasis beat.
```

### Why this works
It tells S6 very clearly:
- who the scene must show
- what cannot drift
- how free the generation may be
- what editorial role the output is likely to serve

---

## 8.2 Real building / place scene

### Scene
Hotel Quitandinha appears as a symbol of scale, prestige, and national ambition.

### Example family
```yaml
family_id: f2
family_type: support
family_intent: establish Hotel Quitandinha as the real architectural object of the ambition and support broader scene coverage around the project
priority: preferred
target_asset_count:
  minimum: 2
  ideal: 3
  maximum: 4
grounding_strength: high
creative_freedom_level: controlled
preferred_generation_modes:
  - reference_guided_generation
reference_inputs:
  - asset_id: quitandinha_facade_01
    source_target_id: t_quitandinha
  - asset_id: quitandinha_architecture_detail_02
    source_target_id: t_quitandinha
preserve_requirements:
  - recognizable Hotel Quitandinha architecture
  - key facade and structure cues
avoid_literal_copy_notes:
  - avoid repetitive angle duplication
editorial_notes: Support progression from grounded establishing into richer architectural coverage.
```

### Why this works
The family remains grounded in the correct building while still supporting editorial richness.

---

## 8.3 Real equipment / vehicle scene

### Scene
A Tiger I tank is described as a symbol of German armored power.

### Example family
```yaml
family_id: f3
family_type: detail
family_intent: reinforce machine-specific factual identity so the tank does not collapse into a generic armored vehicle
priority: preferred
target_asset_count:
  minimum: 1
  ideal: 2
  maximum: 3
grounding_strength: high
creative_freedom_level: controlled
preferred_generation_modes:
  - reference_guided_generation
reference_inputs:
  - asset_id: tiger1_profile_01
    source_target_id: t_tiger1
  - asset_id: tiger1_turret_reference_02
    source_target_id: t_tiger1
preserve_requirements:
  - Tiger I silhouette
  - correct turret/body structure
avoid_literal_copy_notes:
  - avoid genericizing into an unspecified tank
editorial_notes: Factual machine-specific reinforcement.
```

### Why this works
It directly encodes the rule that the system must not drift into generic vehicles when factual specificity is essential.

---

## 8.4 Symbolic / evocative scene

### Scene
An empire is described as rotting from within.

### Example family
```yaml
family_id: f4
family_type: atmospheric
family_intent: create the emotional and symbolic visual field of decay, rot, and instability
priority: required
target_asset_count:
  minimum: 1
  ideal: 2
  maximum: 3
grounding_strength: low
creative_freedom_level: open
preferred_generation_modes:
  - from_scratch_generation
  - multi_reference_synthesis
reference_inputs:
  - asset_id: imperial_hall_reference_01
    source_target_id: t_symbolic_world
  - asset_id: decay_texture_reference_02
    source_target_id: t_symbolic_world
preserve_requirements:
  - tonal coherence with the rest of the video
avoid_literal_copy_notes:
  - avoid heavy-handed symbolic cliché
editorial_notes: Symbolic emotional expansion of the scene.
```

### Why this works
It shows that the same grammar can support scenes where factual identity is less rigid while still preserving coherence.

---

## 9. Why Option D is preferred over Option B

Option B remains a respectable alternative, but the current preference for D is based on the following advantages.

### 9.1 Cleaner separation of concerns
D separates:
- what S6 must produce
- how the family may be useful editorially

This is better than overloading one role/function pair with both meanings.

### 9.2 Better future bridge into S7
The lightweight editorial layer gives a path toward downstream editing without turning V1 into a fully editorial grammar.

### 9.3 Stronger long-term scalability
D is more likely to age well as the system becomes more sophisticated.

### 9.4 Still simple enough for V1
As long as the editorial layer remains light, D does not appear too heavy for V1.

---

## 10. What should remain out of scope for V1

V1 should not yet include:
- detailed sub-taxonomies for every family type
- complex timing grammars
- fine-grained motion strategy per family authored by the LLM
- deep scene-to-scene editorial logic
- asset scoring theory inside the grammar itself

Those can be added later if real downstream consumers demand them.

---

## 10.5 Additional stress-test examples still recommended

The current examples already cover an important spectrum, but before freezing the grammar more strongly it is still recommended to add at least:
- a transition-oriented scene example
- a person + location simultaneous scene example

These two cases are especially important because they are common in real videos and stress-test whether one family grammar can handle multiple factual anchors and editorial bridging needs at once.

---

## 11. Summary

The preferred V1 grammar for `asset_families[]` is now:

> Option D — a two-layer grammar with a strong production-facing layer and a lightweight editorial-facing layer.

The core production-facing language of the family should be:
- `family_type`
- `family_intent`

This grammar is preferred because it:
- preserves factual grounding where needed
- supports controlled creative freedom
- helps S6 materialize useful kits with more concrete intent
- gives S7 a better editorial bridge
- remains implementable in V1

A further V1 simplification also applies:
- motion should not be decided freely by the S5 LLM
- the preferred policy is `motion_policy: first_10_scenes_only`
- `motion_allowed` should be injected deterministically into the scene context

This keeps the grammar strong without making it unnecessarily complicated.
