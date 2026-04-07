# S5 Scene Kit Objects V1

_Status: conceptual object model (V1)_  
_Last updated: 2026-04-07_  
_Owner: Tobias_

---

## 1. Purpose of this document

This document defines the **first conceptual object model** for the new S5→S6→S7 boundary.

Its goal is not to freeze final JSON schemas yet.
Its goal is to define the minimum set of objects that the team should now think with consistently.

These objects are:
- `video_direction_frame`
- `scene_kit_spec`
- `scene_kit_delivery`
- `scene_editorial_input`

This V1 object model is intentionally **simpler than the maximum conceptual richness available**.
That simplification is deliberate.

The design principle is:

> V1 should optimize for legibility, consistency, and downstream usefulness rather than semantic completeness.

---

## 2. Object overview

### 2.1 `video_direction_frame`
A video-level directional artifact produced before scene-level kit specs.

Purpose:
- establish shared visual posture across scenes
- constrain drift
- define broad generation and budget posture
- provide a common baseline for all scene kit design

### 2.2 `scene_kit_spec`
A scene-level specification describing what kind of asset space the scene needs.

Purpose:
- tell S6 what kinds of assets must exist for the scene
- preserve grounding where required
- allow controlled creative freedom where useful
- give downstream editorial resolution enough material to work intelligently
- act as one of the canonical per-scene truth artifacts of S5

### 2.3 `scene_kit_delivery`
A scene-level delivery artifact produced by S6 after materialization.

Purpose:
- describe what was actually produced
- map produced assets back to the intended kit structure
- expose usability and quality information for editorial consumption

### 2.4 `scene_editorial_input`
A conceptual downstream package consumed by S7.

Purpose:
- combine scene timing/audio context with the materialized kit and relevant metadata
- give S7 a real editorial space rather than an opaque asset dump

---

## 3. `video_direction_frame` (V1)

## 3.1 Role

This object establishes the shared directional frame for the whole video before scene kits are created.

It should answer questions like:
- what visual world are we operating in?
- how grounded vs evocative should the video be overall?
- what production modes are allowed?
- what broad cost/complexity ceiling should scene kits respect?

---

## 3.2 Suggested V1 fields

### Identity / context
- `video_id`
- `video_title` (if available)
- `source_package_ref`
- `version`

### Global visual posture
- `dominant_visual_era`
  - example values: `historical`, `contemporary`, `mixed`
- `dominant_style_mode`
  - example values: `photoreal`, `illustrated`, `documentary`, `hybrid`
- `tonal_palette_posture`
  - example values: `warm`, `cool`, `neutral`, `mixed_controlled`
- `grounding_baseline`
  - example values: `high`, `medium`, `low`

### Global constraints
- `global_constraints[]`
  - free-text or short structured notes
- `identity_integrity_priority`
  - example values: `high`, `medium`, `low`
- `copyright_safety_posture`
  - example values: `strict_transformative`, `guided_transformative`, `controlled_exception_only`

### Production constraints
- `allowed_generation_modes[]`
  - example values:
    - `reference_guided_generation`
    - `regeneration_from_reference`
    - `from_scratch_generation`
    - `multi_reference_synthesis`
    - `motion_generation`
- `motion_policy`
  - example values: `first_10_scenes_only`
- `motion_allowed`
  - boolean, injected deterministically per scene from the active motion policy rather than authored freely by the LLM
- `kit_complexity_ceiling`
  - example values: `low`, `medium`, `high`
- `asset_density_guidance`
  - short guidance note such as “prefer 4–6 strong assets per scene unless scene is structurally central”

---

## 3.3 What V1 should avoid

V1 should avoid putting too much into this object.

It should **not** yet try to model:
- exact scene-to-scene continuity links
- deep transition logic
- precise sequence-wide intensity graphs
- hard budget math at the shot level

Its role is to create a usable shared frame, not to become a universal control object.

---

## 4. `scene_kit_spec` (V1)

## 4.1 Role

This is the core object of the new boundary.

A `scene_kit_spec` tells S6 what kind of materialized kit should exist for the scene.

It should define:
- what the scene needs visually
- what kinds of asset families are needed
- what grounding requirements apply
- how much freedom is allowed
- what minimum delivery expectation exists

It should **not** over-close the scene into a final edit plan.

---

## 4.2 Suggested V1 fields

### Identity / scene context
- `scene_id`
- `scene_label`
- `scene_summary`
- `narrative_function`
- `sequence_position`
- `audio_context_ref`
- `scene_duration_estimate`

### Scene direction summary
- `scene_visual_intent`
  - short text describing what the scene must communicate visually
- `visual_mode`
  - example values:
    - `factual`
    - `grounded_cinematic`
    - `evocative`
    - `symbolic`
    - `hybrid`
- `coverage_objective`
  - short text describing what the kit should make possible downstream

### Grounding / freedom posture
- `factual_grounding_priority`
  - example values: `high`, `medium`, `low`
- `reference_dependence_mode`
  - example values:
    - `strongly_reference_anchored`
    - `reference_guided`
    - `reference_informed`
    - `mostly_free_generation`
- `identity_integrity_requirements[]`
  - free-text list of what must remain accurate
- `do_not_literal_copy_notes[]`
  - short list of what should not be copied literally from references

### Kit structure
- `kit_strategy`
  - example values:
    - `hero_centered`
    - `layered_coverage`
    - `factual_plus_cinematic`
    - `sequence_ready`
    - `contrast_pair`
    - `motion_assisted`
- `kit_size_target`
  - object with `minimum`, `ideal`, `maximum`
- `asset_families[]`

### Scene-level production constraints
- `allowed_generation_modes[]`
  - optional scene-level restriction or override within global limits
- `motion_allowed`
  - boolean injected deterministically by the substrate from the active motion policy; not a free scene-level decision by the S5 LLM
- `scene_budget_posture`
  - example values: `low`, `medium`, `high`

### Editorial guidance (lightweight in V1)
- `editorial_notes`
  - short free-text note instead of overly rich enum stacks

---

## 4.3 `asset_families[]` (V1)

This is the internal primitive of the kit.

Each asset family represents a category of assets the scene needs.

However, `family_type` alone is not sufficient.
A family also needs a concrete mission inside the scene kit so that S6 can understand what kind of material it must actually produce.

That is why `family_intent` should be treated as a core V1 field alongside `family_type`.

### Suggested V1 fields per family
- `family_id`
- `family_type`
  - constrained but practical V1 values such as:
    - `hero`
    - `support`
    - `detail`
    - `atmospheric`
    - `transition`
    - `fallback`
- `family_intent`
  - short free-text statement describing the concrete mission of this family inside the scene kit
  - examples:
    - identify the central political actor of the prohibition decision
    - establish Hotel Quitandinha as the real architectural object of the ambition
    - reinforce the gambling/casino reality being discussed
    - keep the symbolic scene tied to the grounded world of the video
- `family_label`
  - short descriptive label
- `priority`
  - example values: `required`, `preferred`, `optional`
- `target_asset_count`
  - object with `minimum`, `ideal`, `maximum`
- `grounding_strength`
  - example values: `high`, `medium`, `low`
- `creative_freedom_level`
  - example values: `strict`, `controlled`, `moderate`, `open`
- `preferred_generation_modes[]`
- `reference_inputs[]`
  - references from S4 or derived reference packages
- `preserve_requirements[]`
- `avoid_literal_copy_notes[]`
- `editorial_notes`
  - lightweight free-text downstream note
- `family_notes`

---

## 4.4 Why V1 keeps `asset_families` modest

V1 intentionally avoids too many fine-grained enums like:
- detailed editorial energy scales
- detailed timing use cases
- overly nuanced visual function taxonomies
- a separate heavy editorial role taxonomy beyond `family_type`

Instead of trying to solve vagueness through more enums, V1 should rely on the combination of:
- `family_type` for broad category
- `family_intent` for concrete mission

Those may become useful later, but for now they are more likely to increase output instability than practical value.

---

## 4.5 Runtime-facing output posture (clarification)

A runtime-facing clarification now applies to the object model.

The preferred S5 output posture is:
- `video_direction_frame.json` = global canonical truth artifact
- `scene_kit_specs/<scene_id>.json` = per-scene canonical truth artifacts
- `s5_scene_kit_pack.json` = compiled downstream handoff surface

This means the object model should be read with an explicit truth hierarchy:
- the global frame and per-scene specs are the truth layer
- the compiled pack is derived from them and should not become an independent sovereign truth

This distinction is operationally important for:
- retries
- re-runs
- scene-level debugging
- downstream legibility for S6

---

## 5. `scene_kit_delivery` (V1)

## 5.1 Role

This object is produced by S6 after the scene kit is materialized.

It should tell downstream consumers:
- what was actually delivered
- how it maps to the intended families
- where delivery is strong or weak
- what editorially useful capabilities now exist

---

## 5.2 Suggested V1 fields

### Identity / lineage
- `scene_id`
- `scene_kit_spec_ref`
- `delivery_version`
- `materialization_status`
  - example values: `complete`, `partial`, `weak`, `failed`

### Delivered families
- `delivered_families[]`

Each delivered family may include:
- `family_id`
- `delivery_status`
  - example values: `satisfied`, `partially_satisfied`, `weak`, `missing`
- `generated_assets[]`
- `delivery_notes`

### Each generated asset may include
- `asset_id`
- `filepath`
- `asset_type`
  - example values: `still`, `motion`, `variant`, `detail`, `overlay_source`
- `source_family_id`
- `generation_method`
- `reference_trace[]`
- `grounding_strength`
- `editorial_affordances[]`
  - free-text or constrained-lite values such as:
    - `hold_friendly`
    - `insert_friendly`
    - `sequence_friendly`
    - `transition_friendly`
- `quality_notes`
- `risk_notes`

### Delivery evaluation
- `coverage_satisfaction_summary`
- `missing_capabilities[]`
- `notable_strengths[]`
- `continuity_flags[]`
- `delivery_risks[]`

---

## 5.3 Why `scene_kit_delivery` matters

S7 should not receive only raw files.

It should receive a delivery object that preserves:
- intention
- traceability
- usability
- weakness reporting

This is what makes the kit legible rather than opaque.

---

## 6. `scene_editorial_input` (conceptual V1 package)

## 6.1 Role

This is the effective package S7 consumes.

`scene_editorial_input` should currently be understood as a **conceptual downstream package**, not necessarily as a single canonical on-disk artifact.

It may eventually be implemented as:
- one compiled artifact
- a structured bundle of multiple artifacts
- or a runtime-composed package assembled from several persisted sources

For V1, the important point is not file singularity.
The important point is that S7 must receive a coherent editorial input surface rather than a disconnected set of files.

---

## 6.2 Expected contents

A conceptual `scene_editorial_input` should include:
- scene audio reference
- scene timing / word alignment / timing metadata
- scene summary / scene meaning context
- `scene_kit_spec`
- `scene_kit_delivery`
- produced asset files
- family-level and asset-level editorial notes
- any relevant global frame context from `video_direction_frame`

---

## 6.3 Why this package matters

The editor layer should not have to reconstruct the scene from disconnected files.

It should receive a package that makes clear:
- what the scene is trying to do
- what material exists
- which assets are strongest
- which families are weak or incomplete
- what room for editorial choice exists

---

## 7. What stays out of V1

The following should remain out of scope for V1:
- final JSON schema freeze
- exhaustive enum systems
- deep scene-to-scene continuity graphs
- exact runtime orchestration model
- exact tool contracts for Freepik/Higgsfield or other S6 producers
- full S7 editing contract
- exact scoring systems for asset quality

These should be revisited after the V1 conceptual object model proves stable.

---

## 8. Summary

The V1 object model for the new boundary is:

- `video_direction_frame` = global visual and production frame
- `scene_kit_spec` = scene-level asset-space specification
- `scene_kit_delivery` = what S6 actually materialized
- `scene_editorial_input` = the conceptual package S7 receives

Together, these objects shift the pipeline away from early rigid scene closure and toward a structured, grounded, editorially usable scene kit model.

A practical V1 simplification also applies here:
- motion should not be treated as an open-ended scene-level planning variable
- instead, `motion_allowed` should be determined by system policy and injected into the scene context
- the currently preferred policy is `motion_policy: first_10_scenes_only`

A runtime-layer clarification also now applies:
- these objects remain the correct conceptual boundary objects
- but the operational architecture around them is expected to use a small real actor map rather than a single monolithic S5 agent
- the currently preferred runtime shape is:
  - one supervisor: `sm_s5_scene_kit_design`
  - three operators: `op_s5_input_assembler`, `op_s5_video_direction_frame_builder`, `op_s5_scene_kit_designer`
- helper/substrate logic should remain consolidated and pragmatic rather than fragmented into many micro-modules
