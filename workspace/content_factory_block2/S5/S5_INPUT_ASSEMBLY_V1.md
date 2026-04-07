# S5 Input Assembly V1

_Status: practical input-layer definition_  
_Last updated: 2026-04-07_  
_Owner: Tobias_

---

## 1. Purpose of this document

This document defines the **V1 input assembly / input normalization layer** for S5.

Its purpose is to answer a practical question that became unavoidable during S5 design work:

> before S5 can design a scene kit, what real upstream artifacts must be gathered and normalized into a usable scene-level input package?

This document is intentionally grounded in the **real upstream state** observed in the Quitandinha video.
It does not assume an idealized clean input that does not yet exist.

It defines:
- what already exists upstream
- what can be assembled deterministically
- what must be derived during input assembly
- what global frame data still needs to be created in S5
- what the resulting `scene_direction_input_package` should contain in V1

This is not yet a runtime spec.
It is the practical input-layer definition that allows S5 to operate on real pipeline outputs rather than on conceptual placeholders.

---

## 2. Why this layer is necessary

S5 does not naturally receive a clean, scene-ready package today.

What exists upstream is distributed across multiple artifacts, including:
- scene/source packages
- screenplay analysis outputs
- S3 semantic grounding outputs
- S4 targets, approved assets, sidecars, and compiled reference-ready pools
- global video context

Those artifacts are useful, but they are not yet assembled into a single scene-level direction package.

So before S5 can produce a `scene_kit_spec`, an upstream layer must:
- gather the relevant artifacts
- normalize them per scene
- fill in a small number of missing derived fields
- present the result in a coherent scene-level package

This layer is what this document defines.

---

## 3. Design principles

### 3.1 Ground the design in real upstream artifacts
This input layer should be built from what the pipeline already produces where possible.

### 3.2 Prefer deterministic assembly where structure already exists
If a reliable deterministic path exists, V1 should use it instead of introducing unnecessary LLM interpretation.

### 3.3 Allow derivation only where upstream fields are materially missing
Fields like `scene_summary` and `narrative_function` are not available in complete upstream form today, so the assembly layer should derive them.

### 3.4 Do not overload S5 with raw upstream chaos
The purpose of this layer is to spare S5 from having to rediscover upstream structure from scratch.

### 3.5 Keep V1 scoped
This V1 definition deliberately avoids deeper temporal/audio enrichment and other downstream-heavy concerns until they are clearly needed.

---

## 4. What the input layer should gather

The V1 S5 input layer should gather from four sources:

1. **scene/narrative layer**
2. **S3 semantic grounding layer**
3. **S4 reference layer**
4. **global direction frame**

---

## 5. Source A — scene / narrative layer

### 5.1 Real upstream source
The closest current source of truth for scenes is:
- `s3_source_package.json`

Related supporting source:
- `screenplay_analysis.json`

### 5.2 Fields already available upstream
The following fields already exist or are trivially derivable:
- `scene_id`
- `scene_text`
- `scene_number`
- `sequence_position` (derivable from `scene_number`)

### 5.3 Fields not yet available as complete upstream truths
The following are not currently present in a sufficiently strong finished form:
- `scene_summary`
- `narrative_function`

`screenplay_analysis.json` may contain partial hints such as:
- `scene_type`
- `interpretation_mode`
- `emotional_tone`

But these do not yet constitute a complete and stable `scene_summary` or `narrative_function` suitable for S5.

### 5.4 V1 decision
The input assembly layer should **derive semantically**:
- `scene_summary`
- `narrative_function`

These should be treated as normalized scene-level fields required by S5, even if they do not yet exist upstream as final fields.

This is an explicitly semantic derivation step, not a deterministic transformation.
In runtime terms, this should be understood as a Python-controlled LLM step rather than a pure mechanical field mapping.

### 5.5 Why this is correct
S5 needs to understand:
- what the scene says
- what the scene does in the video

Without these fields, S5 would be forced to infer too much from raw scene text every time.

---

## 6. Source B — S3 semantic grounding layer

### 6.1 Real upstream source
The main relevant source is:
- `compiled_entities.json`

This currently contains entities across categories such as:
- human subjects
- environments / locations
- objects / artifacts
- symbolic events

Each entity already carries scene linkage via `scene_ids[]`.

### 6.2 What can be assembled deterministically
The following scene-level fields can be assembled deterministically from current upstream data:
- `scene_entities[]`
- `factual_anchors[]`
- `symbolic_anchors[]` (when applicable)

### 6.3 What does not yet exist cleanly
A formal `scene_relations[]` layer does not currently exist upstream in a finished form.

At present, the upstream system mainly provides:
- entities
- their categories
- their presence across scenes

It does not yet provide a strong explicit scene-level relation model such as:
- `Rolla -> owner_of -> Quitandinha`
- `Dutra -> prohibits -> gambling`

### 6.4 V1 decision
The S5 input assembly layer should include:
- `scene_entities[]`
- `factual_anchors[]`
- `symbolic_anchors[]` where useful

It should **not require** formal `scene_relations[]` in V1.
If relations are later added, they can enrich the package, but they should not block the first working version.

### 6.5 Why this is correct
This gives S5 enough semantic grounding to understand:
- what factual anchors exist
- whether the scene is single-anchor, multi-anchor, or partly symbolic

without waiting for a full relation-extraction subsystem.

---

## 7. Source C — S4 reference layer

### 7.1 Real upstream sources
The relevant current S4 artifacts are:
- `research_intake.json` (especially `scene_index`)
- `s4_reference_ready_asset_pool.json`
- per-asset sidecars `.reference_ready.json`

### 7.2 What already works today
The real Quitandinha upstream now supports a deterministic path:

`scene_id -> scene_index[scene_id].linked_target_ids -> pool.by_target[target_id] -> reference-ready assets`

This is the current backbone of S4→S5 reference retrieval.

### 7.3 V1 decision on `relevant_targets[]`
In V1, `relevant_targets[]` should be assembled **deterministically**.

That means:
- use `research_intake.json::scene_index`
- use its `linked_target_ids`
- do not introduce LLM-driven target discovery inside the core V1 input assembly path

### 7.4 Why this deterministic decision is correct for V1
This choice is preferred because it is:
- stable
- auditable
- cheap
- already available in real upstream data
- easier to debug than interpretive target selection

It is acknowledged that deterministic linkage may not always be semantically perfect.
However, V1 should prefer practical reliability over early complexity.
If real-world usage later reveals systematic omissions, expansion/refinement can be revisited in a later version.

### 7.5 V1 decision on `reference_ready_assets[]`
The package should include the reference-ready assets that arise from the deterministic scene→target→pool path.

In practice, V1 should:
- use the assets naturally available through linked targets
- avoid introducing unnecessary extra selection logic prematurely
- rely on the observed real distribution in the Quitandinha upstream

### 7.6 Observed real distribution
The real Quitandinha upstream shows:
- many scenes with 0 assets
- some scenes with 1–5 assets
- a smaller set of richer scenes with 6–12 assets

This means the dominant V1 problem is **not overload**.
The dominant V1 problem is **scarcity** in many scenes.

### 7.7 Practical implication
The S5 input assembly should not assume that every scene will arrive richly grounded by S4 assets.
Some scenes will arrive with:
- strong reference support
nwhile others will arrive with:
- little or no direct reference support

This is a core design reality for S5.

### 7.8 Use of sidecars
The per-asset `.reference_ready.json` files remain the granular source of truth.

The compiled pool should act as the primary selection surface for S5 input assembly.
Sidecars should only need to be opened directly when the pool lacks enough detail for a specific case.

---

## 8. Source D — global direction frame

### 8.1 What already exists partially upstream
Some global context already exists implicitly in artifacts such as:
- `video_context.json`

Examples of already available partial global context include:
- era
- style description
- anti-anachronism guidance

### 8.2 What does not yet exist as a proper upstream artifact
The following fields do not yet exist as a finished scene-direction frame and need to be created in the S5 layer:
- `grounding_baseline`
- `motion_policy`
- `kit_complexity_ceiling`
- `identity_integrity_priority`
- `allowed_generation_modes[]`
- any other explicit scene-kit-level global constraints

### 8.3 V1 decision
The S5 layer must create a proper **global direction frame** artifact rather than assuming it already exists upstream.

In V1, this frame may be partially derived from current global context artifacts, but it must still become a new explicit S5-facing object.

### 8.4 Why this matters
Without this frame, S5 would be forced to make scene-kit decisions without a consistent video-level posture for:
- style
- grounding
- complexity
- motion policy
- production constraints

---

## 9. What stays out of V1

The S5 input assembly V1 should **not** center on:
- detailed audio durations
- word-level timestamps
- timing density
- audio rhythm modeling

These may become useful later, but they are not currently treated as core S5 input concerns in V1.

This keeps the layer focused on:
- narrative understanding
- semantic grounding
- visual reference support
- global constraints

---

## 10. The resulting `scene_direction_input_package`

The V1 package assembled for each scene should look conceptually like this:

### A. Scene core
- `scene_id`
- `scene_text`
- `scene_number`
- `sequence_position`
- `scene_summary` (derived in assembly)
- `narrative_function` (derived in assembly)

### B. Semantic grounding
- `scene_entities[]`
- `factual_anchors[]`
- `symbolic_anchors[]` where useful

### C. S4 reference layer
- `relevant_targets[]` (deterministic)
- `reference_ready_assets[]` (deterministic from the compiled pool via linked targets)

### D. Global direction frame
- `dominant_visual_era`
- `dominant_style_mode`
- `grounding_baseline`
- `motion_policy`
- `motion_allowed` for the scene when applicable
- `kit_complexity_ceiling`
- any other relevant video-level kit constraints

---

## 11. Two real S5 operating regimes revealed by the upstream

The real Quitandinha upstream reveals that S5 must operate in two practical modes.

### 11.1 Reference-supported scene mode
Scenes with meaningful S4 support:
- receive linked targets
- receive usable reference-ready assets
- can design grounded kits around those references

### 11.2 Low-reference or no-reference scene mode
Scenes with little or no S4 support:
- may still receive narrative + S3 grounding + global frame
- may need to push S6 toward from-scratch or more open generation
- cannot assume strong visual references are available

This is a major practical reality of V1.

S5 must be designed to function in both modes.

---

## 12. Assembly logic summary

The V1 input assembly logic should be:

### Step 1 — gather scene core
From scene/source package artifacts.

### Step 2 — derive narrative normalization fields
Generate:
- `scene_summary`
- `narrative_function`

### Step 3 — gather S3 grounding
Assemble scene-linked entities and anchors from `compiled_entities.json`.

### Step 4 — gather S4 reference layer deterministically
Use:
- `scene_index`
- linked target IDs
- compiled reference-ready pool

### Step 5 — derive deterministic scene policy fields
Apply deterministic system rules such as:
- `motion_allowed`
- any scene-level policy fields that arise from global runtime rules rather than semantic interpretation

### Step 6 — attach the global direction frame context
Partly derived from existing global video context, partly newly defined in S5.

### Step 7 — emit the normalized package per scene
The result is a scene-level input package that S5 can actually reason over.

---

## 13. Why V1 keeps `relevant_targets` deterministic

This decision deserves explicit emphasis.

A purely deterministic `relevant_targets[]` backbone is preferred in V1 because:
- the necessary structure already exists
- the path has been proven in the real upstream
- it minimizes unnecessary complexity
- it improves auditability and debugging
- it avoids introducing LLM interpretation before it is truly needed

This does **not** claim that deterministic linkage is semantically perfect forever.
It only claims that V1 should not complicate this layer prematurely.

The project can later observe real results and decide whether controlled expansion/refinement becomes necessary.

---

## 14. Summary

The S5 input assembly V1 is now defined as a practical layer that:
- gathers real scene artifacts
- derives missing narrative-normalization fields semantically
- assembles S3 grounding
- assembles S4 references through a deterministic scene→target→pool path
- derives deterministic policy fields such as `motion_allowed`
- attaches a new global direction frame
- produces a usable scene-level package for S5

The key V1 decisions are:
- `scene_summary` and `narrative_function` are semantically derived in assembly
- `relevant_targets[]` are deterministic in V1
- `reference_ready_assets[]` come from the deterministic linked-target pool path
- `motion_allowed` should be injected deterministically from system policy rather than freely invented by the S5 LLM
- the major V1 challenge is not reference overload but the reality that many scenes have sparse or zero asset coverage
- the global direction frame is a genuinely new artifact that S5 must introduce

This gives S5 a realistic and implementable upstream input model based on the actual state of the Quitandinha pipeline.
