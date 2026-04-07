# S5 Scene Kit Spec V1 Draft

_Status: conceptual output draft_  
_Last updated: 2026-04-07_  
_Owner: Tobias_

---

## 1. Purpose of this document

This document defines the **draft canonical V1 shape** of the `scene_kit_spec` artifact that S5 should produce per scene.

Its purpose is to convert the S5 design work into a practical scene-level output structure that can:
- be authored from the real S5 input assembly layer
- communicate scene-kit intent clearly to S6
- avoid over-closing the final composition of the scene
- remain compact enough for V1
- still preserve enough structure to support real downstream editorial freedom later

This document is not yet a final JSON schema freeze.
It is the practical shape draft that the system can now think with consistently.

---

## 2. What this artifact is

A `scene_kit_spec` is the scene-level output of S5.

It is the artifact through which S5 says:
- what this scene needs visually
- what the scene is really about
- what factual anchors must remain grounded
- what kinds of asset families S6 must materialize
- what minimum delivery must exist for the scene to remain editable downstream

It is **not**:
- the final scene composition
- the final editing plan
- a rigid shot list
- a single prompt per scene

It is a scene-level specification of the **asset space** the scene needs.

---

## 3. Design principles for the V1 shape

### 3.1 Keep it compact but serious
V1 should avoid excessive richness while still being strong enough for real S6 consumption.

### 3.2 Preserve the difference between interpretation and instruction
The spec should contain:
- enough scene reading for the kit to make sense
- enough concrete family instructions for S6 to act

### 3.3 Do not confuse scene kit with final composition
The spec should define what the scene must have available, not how the final scene must be composed on screen.

### 3.4 Preserve factual integrity where necessary
When the scene includes real people, places, objects, vehicles, weapons, buildings, or artifacts, the spec must ensure that the correct references are used and preserved appropriately.

### 3.5 Support both grounded and symbolic scenes
The shape must remain viable for:
- highly factual scenes
- relational scenes
- partly symbolic scenes
- transition-oriented scenes

---

## 4. Canonical V1 shape

The current draft shape of `scene_kit_spec` is:

Top-level fields:
- `spec_version`
- `scene_id`

### A. `scene_core`
Basic identity and narrative normalization for the scene.

Fields:
- `scene_id`
- `scene_text`
- `scene_summary`
- `narrative_function`
- `sequence_position`

### B. `scene_direction`
Short, high-value reading of what the scene must communicate and what kind of scene it is.

Fields:
- `scene_thesis`
- `factual_anchors[]`
- `thematic_layer[]`
- `dominant_scene_mode`

### C. `applied_global_constraints`
The subset of the global direction frame that materially matters to this scene.

Fields:
- `dominant_visual_era`
- `dominant_style_mode`
- `grounding_baseline`
- `allowed_generation_modes[]`
- `motion_allowed`
- `kit_complexity_ceiling`

Clarification:
- the global frame should carry the policy (`motion_policy`)
- the scene kit spec should carry the resolved per-scene boolean (`motion_allowed`)

### D. `kit_strategy`
The scene-level statement of what the kit is trying to enable.

Fields:
- `kit_goal`
- `kit_size_target`
  - `minimum`
  - `ideal`
  - `maximum`

### E. `asset_families[]`
The core production-facing scene-kit content.

Each family contains:
- `family_id`
- `family_type`
- `family_intent`
- `priority`
- `target_asset_count`
  - `minimum`
  - `ideal`
  - `maximum`
- `grounding_strength`
- `creative_freedom_level`
- `preferred_generation_modes[]`
- `reference_inputs[]`
- `preserve_requirements[]`
- `avoid_literal_copy_notes[]`
- `editorial_notes`

### F. `delivery_expectations`
The minimum and preferred delivery conditions S6 should aim to satisfy.

Fields:
- `minimum_viable_delivery[]`
- `preferred_enrichment[]`

---

## 5. Why this shape is preferred

This shape is preferred because it provides six important properties at once.

### 5.1 It is compact enough for V1
It avoids excessive explanatory sprawl.

### 5.2 It preserves a real scene reading layer
S5 is not reduced to blindly emitting families without understanding the scene.

### 5.3 It is actionable for S6
Families are concrete enough to drive materialization.

### 5.4 It preserves editorial openness for S7
It defines the asset space without freezing final composition.

### 5.5 It supports grounded factual scenes
It handles people, places, architecture, and object identity correctly.

### 5.6 It also supports symbolic or mixed scenes
It remains usable when scenes need mood, decay, interpretation, or transition rather than only strict factual depiction.

---

## 6. The role of `family_type + family_intent`

One of the most important conclusions of the S5 design work is that:

> `family_type` alone is too vague.

Broad labels such as:
- `hero`
- `support`
- `detail`
- `atmospheric`
- `transition`
- `fallback`

are useful categories, but they do not tell S6 enough unless the family also states its concrete mission.

That is why the production-facing language of the family in V1 must be:
- `family_type`
- `family_intent`

This combination is what makes the scene-kit structure concrete without over-fragmenting the taxonomy.

A further explicit rule now applies in V1:
- each `scene_kit_spec` should contain at least 1 `asset_family`
- if a scene has weak or zero S4 reference coverage, it should still receive a minimally viable family rather than an empty family list

---

## 7. Example A — relational factual scene

### Scene
“Joaquim Rolla sonhava transformar o Hotel Quitandinha no maior cassino do mundo.”

### Compact `scene_kit_spec` example

```yaml
scene_kit_spec:
  spec_version: v1_draft
  scene_id: scene_016

  scene_core:
    scene_text: "Joaquim Rolla sonhava transformar o Hotel Quitandinha no maior cassino do mundo."
    scene_summary: "The scene introduces Joaquim Rolla's ambition to turn Hotel Quitandinha into the world's largest casino."
    narrative_function: "introduce the human visionary and the scale of the project"
    sequence_position: 16

  scene_direction:
    scene_thesis: "This scene must communicate that Rolla is the human driver of a grand casino ambition attached to the real Hotel Quitandinha."
    factual_anchors:
      - Joaquim Rolla
      - Hotel Quitandinha
    thematic_layer:
      - casino ambition
    dominant_scene_mode: factual_plus_cinematic

  applied_global_constraints:
    dominant_visual_era: "1940-1946"
    dominant_style_mode: documentary_hybrid
    grounding_baseline: high
    allowed_generation_modes:
      - reference_guided_generation
      - regeneration_from_reference
      - from_scratch_generation
      - multi_reference_synthesis
    motion_allowed: false
    kit_complexity_ceiling: medium

  kit_strategy:
    kit_goal: "Provide enough grounded and expressive material for a relational scene centered on Rolla, the hotel, and the casino ambition."
    kit_size_target:
      minimum: 4
      ideal: 6
      maximum: 8

  asset_families:
    - family_id: f1
      family_type: hero
      family_intent: "Identify Joaquim Rolla as the visionary human agent behind the project."
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
        - asset_id: a_rolla_01
          source_target_id: t002
      preserve_requirements:
        - facial identity of Joaquim Rolla
        - period-compatible appearance
      avoid_literal_copy_notes:
        - do not produce a generic elegant businessman
      editorial_notes: "Human anchor of the scene."

    - family_id: f2
      family_type: support
      family_intent: "Establish Hotel Quitandinha as the real architectural object of Rolla's ambition."
      priority: required
      target_asset_count:
        minimum: 1
        ideal: 2
        maximum: 3
      grounding_strength: high
      creative_freedom_level: controlled
      preferred_generation_modes:
        - reference_guided_generation
        - multi_reference_synthesis
      reference_inputs:
        - asset_id: a_quitandinha_01
          source_target_id: t009
        - asset_id: a_quitandinha_04
          source_target_id: t009
      preserve_requirements:
        - recognizable Hotel Quitandinha silhouette
        - architectural identity
      avoid_literal_copy_notes:
        - do not collapse into a generic grand hotel
      editorial_notes: "Primary place anchor of the scene."

    - family_id: f3
      family_type: detail
      family_intent: "Reinforce the casino and luxury identity of what the project was meant to become."
      priority: preferred
      target_asset_count:
        minimum: 1
        ideal: 2
        maximum: 3
      grounding_strength: medium
      creative_freedom_level: controlled
      preferred_generation_modes:
        - reference_guided_generation
        - multi_reference_synthesis
      reference_inputs:
        - asset_id: a_casino_01
          source_target_id: t013
        - asset_id: a_casino_02
          source_target_id: t013
      preserve_requirements:
        - clear casino/luxury cues
        - coherence with Quitandinha project context
      avoid_literal_copy_notes:
        - do not become generic luxury décor
      editorial_notes: "Project-destination reinforcement."

    - family_id: f4
      family_type: atmospheric
      family_intent: "Elevate the ambition of the project with controlled cinematic grandeur while preserving factual anchors."
      priority: optional
      target_asset_count:
        minimum: 1
        ideal: 1
        maximum: 2
      grounding_strength: medium
      creative_freedom_level: moderate
      preferred_generation_modes:
        - multi_reference_synthesis
        - from_scratch_generation
      reference_inputs:
        - asset_id: a_quitandinha_01
          source_target_id: t009
        - asset_id: a_casino_01
          source_target_id: t013
      preserve_requirements:
        - keep the scene tied to Rolla + Quitandinha project
      avoid_literal_copy_notes:
        - do not drift into fantasy architecture
      editorial_notes: "Optional grandeur/elevation layer."

  delivery_expectations:
    minimum_viable_delivery:
      - one strong Rolla asset
      - one strong recognizably Quitandinha asset
      - one useful casino/luxury reinforcing asset
    preferred_enrichment:
      - multiple usable framings for Rolla and Quitandinha
      - at least one elevated/cinematic variant if grounding remains legible
```

---

## 8. Example B — symbolic grounded scene

### Scene
“O império do jogo começava a apodrecer antes mesmo de florescer.”

### Compact `scene_kit_spec` example

```yaml
scene_kit_spec:
  spec_version: v1_draft
  scene_id: scene_symbolic_01

  scene_core:
    scene_text: "O império do jogo começava a apodrecer antes mesmo de florescer."
    scene_summary: "The scene introduces the idea that the gambling empire was already decaying before it fully matured."
    narrative_function: "shift from factual exposition into symbolic decline and thematic foreshadowing"
    sequence_position: 27

  scene_direction:
    scene_thesis: "This scene must communicate decay, instability, and collapse-in-advance while remaining tied to the grounded world of the hotel/casino project."
    factual_anchors:
      - Hotel Quitandinha project world
      - gambling/casino universe
    thematic_layer:
      - decay
      - premature collapse
      - grandeur rotting from within
    dominant_scene_mode: symbolic_grounded

  applied_global_constraints:
    dominant_visual_era: "1940-1946"
    dominant_style_mode: documentary_hybrid
    grounding_baseline: high
    allowed_generation_modes:
      - reference_guided_generation
      - regeneration_from_reference
      - from_scratch_generation
      - multi_reference_synthesis
    motion_allowed: false
    kit_complexity_ceiling: medium

  kit_strategy:
    kit_goal: "Provide enough evocative and grounded material for a symbolic scene that still belongs to the same factual video world."
    kit_size_target:
      minimum: 3
      ideal: 4
      maximum: 6

  asset_families:
    - family_id: f1
      family_type: atmospheric
      family_intent: "Create the emotional and symbolic visual field of decay, rot, and instability around the gambling empire."
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
        - asset_id: a_casino_01
          source_target_id: t013
        - asset_id: a_hotel_interior_03
          source_target_id: t009
      preserve_requirements:
        - tonal coherence with the project world
        - visual relation to luxury/casino/hotel environment
      avoid_literal_copy_notes:
        - do not become generic dark symbolism
        - do not sever connection to the video's grounded world
      editorial_notes: "Primary symbolic/emotional carrier of the scene."

    - family_id: f2
      family_type: support
      family_intent: "Keep the scene visually tied to the real hotel/casino project so the symbolic layer does not float away from the narrative world."
      priority: required
      target_asset_count:
        minimum: 1
        ideal: 1
        maximum: 2
      grounding_strength: medium
      creative_freedom_level: controlled
      preferred_generation_modes:
        - reference_guided_generation
        - multi_reference_synthesis
      reference_inputs:
        - asset_id: a_quitandinha_01
          source_target_id: t009
        - asset_id: a_casino_02
          source_target_id: t013
      preserve_requirements:
        - recognizability of project/hotel/casino world
        - continuity with previous factual scenes
      avoid_literal_copy_notes:
        - do not become generic luxury imagery
        - do not over-literalize decline in a way that breaks historical coherence
      editorial_notes: "Grounding tether for the symbolic layer."

    - family_id: f3
      family_type: transition
      family_intent: "Provide bridge material between the factual casino-world exposition and the more interpretive mood of decline."
      priority: optional
      target_asset_count:
        minimum: 1
        ideal: 1
        maximum: 2
      grounding_strength: medium
      creative_freedom_level: moderate
      preferred_generation_modes:
        - multi_reference_synthesis
        - reference_guided_generation
      reference_inputs:
        - asset_id: a_casino_01
          source_target_id: t013
        - asset_id: a_quitandinha_04
          source_target_id: t009
      preserve_requirements:
        - maintain visual continuity with the factual world
      avoid_literal_copy_notes:
        - do not make the bridge feel like an unrelated visual detour
      editorial_notes: "Useful when the editor needs to turn the viewer from explanation into foreboding mood."

  delivery_expectations:
    minimum_viable_delivery:
      - one strong symbolic/atmospheric asset tied to the casino-hotel world
      - one grounded support asset that keeps the scene recognizably inside the Quitandinha project universe
    preferred_enrichment:
      - more than one atmospheric variation
      - one useful bridge asset between factual world and symbolic decay
```

---

## 9. Example C — low-reference / zero-reference scene

### Scene
“O projecto ainda vivia mais na promessa do que na matéria.”

### Compact `scene_kit_spec` example

```yaml
scene_kit_spec:
  spec_version: v1_draft
  scene_id: scene_lowref_01

  scene_core:
    scene_text: "O projecto ainda vivia mais na promessa do que na matéria."
    scene_summary: "The scene communicates that the project still existed more as promise than as materially realized reality."
    narrative_function: "bridge between factual setup and a more interpretive statement about ambition not yet solidified"
    sequence_position: 22

  scene_direction:
    scene_thesis: "This scene should communicate unrealized ambition and partial abstraction without breaking coherence with the grounded world of the video."
    factual_anchors:
      - Quitandinha project world
    thematic_layer:
      - ambition not yet materialized
      - promise over substance
    dominant_scene_mode: hybrid

  applied_global_constraints:
    dominant_visual_era: "1940-1946"
    dominant_style_mode: documentary_hybrid
    grounding_baseline: medium
    allowed_generation_modes:
      - reference_guided_generation
      - regeneration_from_reference
      - from_scratch_generation
      - multi_reference_synthesis
    motion_allowed: false
    kit_complexity_ceiling: medium

  kit_strategy:
    kit_goal: "Provide at least one usable family even under low-reference conditions, while keeping the scene tied to the broader project world."
    kit_size_target:
      minimum: 1
      ideal: 2
      maximum: 3

  asset_families:
    - family_id: f1
      family_type: atmospheric
      family_intent: "Represent the unrealized, still-forming nature of the project when direct factual reference support is weak or absent."
      priority: required
      target_asset_count:
        minimum: 1
        ideal: 2
        maximum: 2
      grounding_strength: low
      creative_freedom_level: controlled
      preferred_generation_modes:
        - from_scratch_generation
        - multi_reference_synthesis
      reference_inputs: []
      preserve_requirements:
        - maintain coherence with the Quitandinha project world
      avoid_literal_copy_notes:
        - do not drift into generic fantasy imagery
        - do not sever visual relation with the historical documentary frame
      editorial_notes: "Minimum viable family for a low-reference bridge scene."

  delivery_expectations:
    minimum_viable_delivery:
      - one usable visual that communicates unrealized ambition while staying coherent with the project world
    preferred_enrichment:
      - one alternate variation with slightly stronger architectural/project cues
```

---

## 10. What these examples prove

These two compact examples demonstrate that the same V1 shape can support materially different scene types:

### Example A proves the shape can handle:
- relational factual scenes
- two-anchor scenes
- strong grounding requirements
- project/ambition framing

### Example B proves the shape can handle:
- symbolic scenes
- grounded-yet-interpretive scenes
- scenes without a dominant human anchor
- scenes that need tethering rather than strict literal resolution

This is an important validation of the compact V1 shape.

---

## 11. Why the compact V1 shape is preferred over the richer exploratory shape

A richer exploratory version of the scene kit spec was useful during design.
However, the compact version is preferred for V1 because it:
- reduces output verbosity
- lowers cognitive overhead
- reduces inconsistency risk
- remains highly actionable for S6
- still preserves the distinction between:
  - scene reading
  - family-level instruction
  - delivery expectation

This is the right tradeoff for a first operational version.

---

## 12. Additional clarifications for downstream use

### 12.1 `scene_entities[]` from S3
`scene_entities[]` are consumed by S5 during scene understanding and family design.
They should not be passed through literally to S6 as a raw field.

Instead, their influence should be reflected through:
- `factual_anchors[]`
- `reference_inputs[]`
- `preserve_requirements[]`
- `family_intent`

### 12.2 `symbolic_anchors[]` from S3
`symbolic_anchors[]` should be understood as one of the inputs that inform `thematic_layer[]` inside `scene_direction`.
They should not be treated as a literal pass-through field in the output.

---

## 13. Remaining open questions

This draft does not yet freeze:
- final JSON schema
- exact enum list for every field
- whether additional compact fields should exist for risk handling
- whether scene-level secondary fields should be added later
- exact runtime implementation path for S5

Those should come only after the team is satisfied that this compact shape is the right output target.

---

## 14. Relationship between `scene_kit_spec` and the S5 output layer

A runtime-facing clarification now applies to this artifact.

The preferred S5 output posture is:
- `video_direction_frame.json` as the global canonical artifact
- `scene_kit_specs/<scene_id>.json` as the per-scene canonical artifacts
- `s5_scene_kit_pack.json` as a compiled downstream handoff surface

This means:
- each `scene_kit_spec` is part of the **canonical truth layer** of S5
- the compiled pack should be derived from these scene-level artifacts rather than treated as an independent sovereign truth

This is important because:
- retries and re-runs should remain scene-granular
- debugging should remain scene-granular
- S6 should be able to consume a sector-level handoff surface without collapsing the truth model into one giant compiled artifact

So in practical terms:
- `scene_kit_spec` is the core per-scene truth object
- `s5_scene_kit_pack.json` is the sector-level entry surface for downstream consumption

---

## 15. Summary

The current preferred V1 output shape for S5 is a compact `scene_kit_spec` that includes:
- scene identity and normalized scene reading
- scene-level direction and anchors
- applied global constraints
- kit strategy
- family-level kit instructions via `asset_families[]`
- delivery expectations for S6

This shape is now considered strong enough to support both:
- grounded factual scenes
- grounded symbolic scenes

without collapsing into either under-specification or premature editorial over-control.
