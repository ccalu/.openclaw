# S5 Scene Kit Boundary Concept

_Status: conceptual boundary freeze (V1 direction)_  
_Last updated: 2026-04-07_  
_Owner: Tobias_

---

## 1. Purpose of this document

This document freezes the **correct conceptual boundary** between **S5**, **S6**, and the downstream editorial layer currently referred to as **S7**.

Its purpose is to document a critical design shift that emerged after deeper discussion:

- S5 should **not** be framed as a sector that chooses a final image per scene
- S5 should **not** over-close the scene too early
- S5 should instead define the **scene kit target** for each scene
- S6 should materialize that kit
- S7 should receive a real editorial asset space rather than a rigid instruction set

This document exists because the older “visual direction” framing is directionally useful but insufficiently precise for the actual system being designed.

The goal here is to make explicit:
- what changed in the conceptual model
- what S5 is now understood to own
- how S5 relates to S4, S6, and S7
- what must be true in **V1** of this boundary
- what must explicitly wait for later versions

This is **not** yet:
- a runtime spec
- an agent materialization plan
- a JSON schema freeze
- an implementation design

It is the conceptual freeze that should guide those later documents.

---

## 2. Why the earlier framing was too weak

A weaker framing of S5 sounds like:

- take the scene
- inspect the references
- decide what image should represent it
- write instructions for generation

That framing is too narrow.

It still assumes that the goal is to resolve each scene into one or a few tightly pre-decided outputs.

That is not the real objective.

The actual objective is to move away from a brittle and over-controlled pipeline where scenes are effectively pre-closed too early, leaving little room for downstream editorial intelligence.

The newer understanding is stronger:

> S5 should define the **space of visual assets** each scene needs in order to be edited well downstream.

That means S5 should create structure, but not premature closure.

---

## 3. The core conceptual shift

The key shift is this:

### Old intuition
S5 determines the visual resolution of the scene.

### Stronger formulation
S5 determines the **scene kit target** of the scene.

A scene kit target is:
- a structured set of asset needs
- with different roles and priorities
- with different degrees of factual grounding vs creative freedom
- designed to give downstream sectors enough material to build a strong scene

This shift matters because it changes the purpose of the entire middle of the visual pipeline.

The new question is no longer:

> What is the image for this scene?

The new question is:

> What asset space should exist for this scene so that the scene can later be edited professionally, flexibly, and coherently?

---

## 4. The new macro chain

The intended chain is now best understood as:

- **S3** → semantic structuring of the video
- **S4** → factual visual grounding and reference discovery
- **S5** → scene kit design
- **S6** → scene kit materialization
- **S7** → editorial scene resolution / assembly

### 4.1 Sector responsibilities in this chain

#### S4
S4 is responsible for discovering and organizing:
- people
- locations
- objects
- architecture
- visual references
- grounding material

Its main function is to ensure that the pipeline has access to the **real-world visual anchors** required by the video.

This is strategically important because the system has previously suffered from factual visual mismatch, such as:
- showing the wrong person
- showing the wrong place
- showing the wrong object or artifact

S4 exists to reduce that error surface.

#### S5
S5 is responsible for deciding what **scene kit** each scene needs.

It receives:
- scene context
- narrative role
- audio/timing context where needed
- semantic grounding
- S4 grounding references
- production constraints

It outputs a structured specification of what kinds of assets must exist for the scene.

#### S6
S6 is responsible for materializing the kit that S5 specified.

This may include:
- reference-guided generation
- regeneration from references
- generation from scratch
- multi-reference synthesis
- motion generation where allowed
- tool-specific production paths

S6 should not be forced to guess what the scene needs. It should execute against a strong scene kit specification.

#### S7
S7 is responsible for actual editorial resolution.

S7 should receive:
- scene audio
- scene timing
- a materialized kit
- editorial metadata
- enough freedom to make scene-level choices

S7 should **not** receive a brittle pre-closed scene instruction.
It should receive a structured but open editorial space.

---

## 5. Why this shift matters strategically

The purpose of this boundary is not only better generation.
It is to move the entire pipeline away from early over-determination.

The desired direction is:

- preserve factual grounding where it matters
- preserve reference traceability
- preserve production structure
- but avoid hard-coding the final visual outcome too early

This is what makes real editorial emergence possible later.

Without this shift:
- the pipeline remains rigid
- the editor layer becomes decorative rather than intelligent
- the system keeps behaving like a prompt factory

With this shift:
- scenes can receive real coverage
- downstream can choose between alternatives
- the system gains room for professional editing behavior

---

## 6. S4 remains indispensable

The move toward scene kits does **not** reduce the importance of S4.

In fact, it clarifies S4’s value.

S4 is the layer that provides:
- factual anchors
- identity references
- location references
- architecture references
- object/artifact references
- mood/context references where useful

These references are often **not** directly safe or desirable as final assets because they may contain:
- copyright issues
- watermarks
- weak framing
- inconsistent quality
- style mismatch
- compositional limitations

But they remain essential as:
- grounding material
- reference guidance
- anti-hallucination anchors
- identity preservation support

The correct conceptual rule is:

> S4 outputs are usually **reference-first**, not final-asset-first.

That principle is preserved in this boundary.

---

## 7. S5 as scene kit designer

S5 should now be understood as:

> the sector that designs the asset space each scene needs

This means S5 should define, per scene:
- what kinds of visual assets are needed
- what roles those assets should serve
- which parts of the scene require strong factual grounding
- which parts permit more creative freedom
- how much coverage the scene should have
- how much diversity is useful
- what S6 must deliver for the scene to be editable downstream

This is not the same as selecting the final cut.
It is not the same as choosing one final image.
It is the design of a **usable scene kit**.

---

## 8. The scene kit concept

### 8.1 What a scene kit is

A scene kit is a structured set of assets or asset requirements that gives the downstream editorial layer enough material to build a scene well.

A scene kit may include, depending on the scene:
- hero visuals
- factual anchors
- supporting visuals
- detail inserts
- cinematic reinterpretations
- atmospheric variants
- transition-friendly material
- optional motion bases
- fallback alternatives

### 8.2 Why the kit concept is stronger than “one image per scene”

A one-image-per-scene model is too weak because:
- it leaves no room for editorial adaptation
- it creates brittleness if generation underperforms
- it cannot support richer pacing or scene evolution
- it gives downstream editors too little usable material

The kit concept is stronger because it creates:
- structured choice
- resilience
- real coverage
- downstream flexibility

### 8.3 Why the kit concept is still structured

The scene kit is **not** meant to become chaos.

This is not an argument for “generate many random assets and let the editor improvise blindly.”

The scene kit must remain:
- intentional
- role-aware
- budget-aware
- grounded where necessary
- bounded in complexity

It is an expansion of editorial possibility, not an abandonment of direction.

---

## 9. V1 design principles

To keep the first version usable, this boundary should obey the following principles.

### 9.1 Prefer simplicity over semantic richness

V1 should avoid over-designing the scene kit spec.

If the object becomes too semantically rich too early, likely failures include:
- inconsistent LLM output
- weak schema stability
- unclear downstream interpretation
- poor repeatability across scenes

V1 should optimize for:
- consistency
- legibility
- strong core fields
- modest controlled enums
- limited cognitive overhead

### 9.2 Prefer a usable global frame over complex cross-scene continuity modeling

V1 should include a global directional artifact, but it should remain simple.

The most important first use of the global layer is to prevent major style drift across scenes.

V1 does **not** need a sophisticated continuity graph between scenes yet.

### 9.3 Prefer budget-aware scene kits over idealized unlimited kits

S5 must not design kits in a vacuum.

If S5 asks for too many assets, too much motion, or too many expensive modes, S6 becomes impractical.

Therefore V1 must include explicit production boundaries such as:
- allowed generation modes
- kit complexity ceiling
- a simple motion policy
- baseline asset count expectations

For V1, motion should be handled through a deterministic system rule rather than open-ended LLM choice.
The current preferred policy is:
- `motion_policy: first_10_scenes_only`
- scenes with index `<= 10` receive `motion_allowed = true`
- scenes after that receive `motion_allowed = false`

This should be injected by the substrate or boundary logic rather than freely invented by S5.

### 9.4 Preserve grounding while allowing controlled freedom

Not all asset families need the same grounding level.

Some should be strongly tied to references.
Others can be more interpretive.

V1 should preserve that distinction, but in a simple and inspectable way.

---

## 10. The global artifact: `video_direction_frame`

Before scene kits are defined, S5 should establish a global directional frame for the video.

This frame exists to create shared context across all scene kit specs.

### 10.0 Requirement status

For V1, `video_direction_frame` should be treated as a **required upstream artifact** for scene kit design, not as an optional enhancement.

In practical terms:
- scene kit design should not begin from an unconstrained per-scene vacuum
- every `scene_kit_spec` should be authored under an active `video_direction_frame`
- if the frame is missing, that is a boundary incompleteness problem, not a normal operating state

This requirement exists because the whole point of the frame is to prevent local scene kits from drifting into incompatible style, grounding, or production assumptions.

### 10.1 What V1 should focus on

The V1 global frame should primarily capture:
- dominant visual era or historical posture
- dominant generation style
- broad tonal/palette posture
- grounding baseline for the video
- global constraints all scenes must respect
- generation budget posture for the whole video
- allowed generation modes
- whether motion is allowed under the active deterministic motion policy

### 10.2 What V1 should explicitly avoid

V1 should **not** attempt full detailed modeling of:
- every transition between adjacent scenes
narrative continuity graphs
- deep global sequencing logic
- heavy scene-to-scene dependency models

Those may become relevant later, but they should not block the first conceptual freeze.

### 10.3 Why this global frame matters

Without it, scene kit specs may drift into incompatible local decisions, such as:
- one scene heavily photorealistic
- another illustration-like
- another overly symbolic without relation to the video baseline

The frame creates controlled coherence.

---

## 11. The role of asset families

The scene kit should be built around **asset families** rather than prematurely rigid one-to-one asset slots.

### 11.1 Why asset families are the right primitive

Asset families make it possible to say:
- what kind of asset group the scene needs
- what role that group serves
- how many outputs are appropriate
- how much flexibility the materialization layer has

This is stronger than saying “produce exact image X, Y, and Z.”

### 11.2 Example family types

Examples may include:
- hero factual anchor
- hero reinterpretation
- supporting factual coverage
- detail inserts
- atmospheric variation
- transition material
- motion base
- fallback alternative

These examples are conceptual, not yet final enums.

### 11.3 Why this matters downstream

Asset families help S6 understand what to materialize and help S7 understand what each delivered asset is for.

They create structure without over-closing the scene.

---

## 12. Grounding vs freedom

One of the central design tensions in this boundary is the relationship between:
- factual grounding
- legal/practical safety
- creative freedom
- downstream editability

A correct scene kit must express this tension rather than hide it.

Some scene material should remain strongly anchored to:
- real people
- real places
- real objects
- historically relevant details

Other material can be more:
- interpretive
- cinematic
- atmospheric
- symbolic
- reconstructive

The key is not to force one rule for the entire scene.

The scene kit should be able to distinguish between:
- highly grounded parts of the scene
- more open-ended parts of the scene

This is a foundational principle of the new S5 boundary.

---

## 13. S6 constraints must enter the boundary

S5 must design kits that S6 can realistically materialize.

This means the conceptual boundary must include practical production constraints such as:
- `allowed_generation_modes`
- `motion_policy`
- `motion_allowed` (injected deterministically per scene rather than freely authored by the LLM)
- `kit_complexity_ceiling`
- high-level asset count guidance

Without these, S5 risks becoming a purely aspirational planner.

That would immediately recreate friction downstream.

### 13.1 Why this is especially important now

The intended S6 direction includes tool-driven generation flows such as:
- reference-based generation
- regeneration from source images
- Freepik-driven asset generation
- Higgsfield-driven generation
- motion production in selective cases

Those flows are not free.
They have:
- latency
- cost
- retry overhead
- mode-specific limitations

The scene kit boundary must acknowledge that reality.

---

## 14. What S7 should receive

The downstream editorial layer should receive:
- scene audio
- scene timing or alignment data
- the scene kit specification context
- the materialized scene kit
- editorially useful metadata
- enough room to choose and assemble intelligently

The purpose is to let S7 behave more like a real editorial team and less like an executor of rigid prewritten instructions.

The scene kit model exists specifically to enable this.

---

## 14.1 Scene kit is not final scene composition

An important clarification is required here.

The scene kit should **not** be confused with the final composition of the scene.

S5 should not decide, in a rigid downstream-binding way:
- the final on-screen layout
- the exact split/grid/collage choice
- the exact sequencing pattern
- the exact edit timing
- the final compositional arrangement used in the cut

Those belong more properly to the downstream editorial layer.

What S5 must do instead is ensure that the scene has a sufficiently rich, well-grounded, and intentionally structured asset space so that S7 can later resolve the scene intelligently.

This means S5 is responsible for:
- preparing the scene’s asset space
- preserving factual integrity where necessary
- ensuring enough diversity and utility in the kit
- making multiple valid downstream resolutions possible

But S5 is **not** responsible for choosing the final edit-level composition.

A useful formulation is:

> S5 defines the space of editorial possibility.  
> S7 chooses the final concrete resolution of the scene.

This distinction matters because the system should avoid both extremes:
- over-closing the scene too early in S5
- or under-designing the kit so badly that S7 has only nominal freedom

---

## 15. V1 boundaries: what is in scope

V1 should include:
- the correct scene kit framing
- the global `video_direction_frame`
- a simple V1 object model
- asset families as the conceptual primitive
- grounding vs freedom distinctions
- S6 constraint awareness
- downstream editorial orientation

V1 should **not** yet include:
- full final JSON schema freeze
- deep continuity graphs
- exhaustive enum taxonomies
- exact runtime orchestration
- final agent materialization strategy
- detailed S7 editing logic

---

## 16. Stress-test examples are required

Before deeper implementation work begins, this boundary should be tested against multiple scene types.

At minimum, the concept should be stress-tested against:
- a factual person-centered scene
- a location/architecture scene
- a symbolic or evocative scene
- a transition-oriented scene

This is necessary to verify that the boundary is not only theoretically elegant but structurally adequate.

---

## 17. Output posture and truth hierarchy (V1 runtime-facing clarification)

A runtime-facing clarification now needs to be made explicit.

S5 should not be expected to choose between:
- only per-scene artifacts
- or only one giant compiled artifact

The stronger V1 posture is:
- produce **granular canonical artifacts**
- and also produce a **compiled downstream handoff surface**

### 17.1 Canonical truth
The preferred canonical truth layer is:
- `video_direction_frame.json` as the global truth artifact
- `scene_kit_specs/<scene_id>.json` as the per-scene truth artifacts

These artifacts should be treated as the source of truth for:
- inspection
- retry / re-run
- scene-level debugging
- downstream per-scene consumption

### 17.2 Compiled handoff surface
S5 should also produce a compiled sector artifact such as:
- `s5_scene_kit_pack.json`

This pack should be treated as:
- a downstream-facing handoff surface
- a sector-level index / readiness surface
- a practical entry point for S6

It should **not** be treated as a sovereign truth artifact independent from the underlying canonical scene artifacts.

### 17.3 Why this hierarchy is preferred
This hierarchy is preferred because it preserves both:
- granular truth and inspectability
- downstream legibility and convenience

It also reduces the risk that the compiled handoff pack drifts into becoming an independent truth that later conflicts with the real scene-level artifacts.

### 17.4 Practical implication
The practical expectation is:
- S6 may begin from the compiled pack as its sector-level handoff surface
- but real scene materialization should still rely on the canonical per-scene `scene_kit_spec` artifacts

This is now the preferred V1 direction for the S5 output posture.

---

## 18. Summary

The correct conceptual understanding is now:

- S4 provides factual visual grounding and reference material
- S5 designs the **scene kit target** for each scene
- S6 materializes that kit under real production constraints
- S7 uses the kit as a true editorial asset space

The central design goal is not to decide one final image per scene.
It is to create the right structured asset space so that scenes can later be edited professionally, flexibly, and with strong factual grounding.

A corresponding output posture now also follows from this:
- `video_direction_frame.json` + per-scene `scene_kit_spec` artifacts are the canonical truth
- `s5_scene_kit_pack.json` is the derived downstream handoff surface

That is the conceptual core of the S5→S6→S7 boundary in V1.
