# S5 — Visual Direction Concept

_Status: conceptual architecture draft_
_Last updated: 2026-04-06_
_Owner: Tobias_

---

## 1. Purpose of this document

This document defines the **conceptual role, internal logic, and output model** of **S5 — Visual Direction** inside Block 2 of the Content Factory pipeline.

Important note:
- this older concept document still uses some earlier language such as `slot`
- in the stronger V1 grammar and runtime docs, the operational term is now `asset family`
- where this doc says `slot`, it should be read as an earlier conceptual precursor to the later `asset family` model

Its purpose is to make the newly defined S5 concept explicit enough that:

- Tobias main chat can reason about S5 without ambiguity
- Claude Code can understand what S5 is supposed to do before implementation details are frozen
- future S5 contracts, schemas, helpers, and runtime design can be derived from a stable conceptual foundation
- the team does not regress into a shallow interpretation of S5 as “just prompt writing” or “just choosing images”

This is intentionally a **concept document**, not yet an implementation spec.

It focuses on:
- what S5 is
- what it owns
- what it receives
- what it decides
- what it outputs
- how it relates to S4, S6, and final scene assembly

It does **not** yet freeze:
- agent materialization
- operator definitions
- CLI invocation details
- sector runtime contracts
- implementation substrate

Those should come later, after the concept is treated as stable.

---

## 2. Why S5 needed to be redefined

A weak interpretation of S5 would be something like:

- take scene text
- look at some references
- write prompts for image generation

That is not sufficient.

The real problem is more complex.

For each scene, the system must decide:

- what the scene needs to communicate visually
- what kind of visual treatment best serves the narrative
- whether the scene should be factual, evocative, symbolic, or hybrid
- whether one visual is enough or whether the scene needs multiple visual pieces
- whether existing references are usable only as grounding or should influence final generation strongly
- whether the scene should be resolved as a hero shot, progression, layered composition, sequence, or motion-led structure
- how to preserve coherence with surrounding scenes
- how to prepare the right terrain for downstream generation and final editing

That means S5 is not just selecting assets.

S5 is the sector where the system decides:

> **how each scene should be visually resolved**

This makes S5 one of the most important sectors in the entire Block 2 pipeline.

---

## 3. Position of S5 inside Block 2

### 3.1 Macro sequence

The intended macro sequence is:

- **S3 — Visual Planning**
- **S4 — Asset Research**
- **S5 — Visual Direction**
- **S6 — Visual Production / Generation / Materialization**
- downstream final scene assembly / editing layer

### 3.2 Role of S5 in that sequence

The clean formulation that emerged is:

- **S4**: “Here is what exists, what was found, and what may serve as a base.”
- **S5**: “From these references, here is how the scene should be resolved, and here is what S6 must produce.”
- **S6**: “I will produce the final visual assets based on that plan.”

This formulation is important because it prevents overlap between sectors.

### 3.3 Why this formulation is strong

It gives each sector a distinct responsibility:

- S4 owns **discovery and reference acquisition**
- S5 owns **creative direction and production planning**
- S6 owns **final visual materialization**

Without this separation, the block becomes confused:
- S4 risks becoming half-research, half-production
- S5 risks becoming vague or redundant
- S6 risks being forced to guess creative intent

---

## 4. Core mission of S5

### 4.1 Mission statement

S5 receives:
- scene narrative context
- semantic grounding
- reference material from S4
- downstream production constraints

and produces:
- a **scene-level visual production plan** that tells S6 what must be produced in order for the scene to be edited strongly and coherently.

### 4.2 Exact mission

S5 must answer, for each scene:

> Given what this scene needs to communicate, and given the references and constraints available, what is the best visual coverage strategy for this scene, and what exactly must S6 produce to make that strategy possible?

### 4.3 What S5 optimizes for

S5 should optimize for a combination of:

- **narrative correctness**
- **visual strength**
- **creative intelligence**
- **downstream editability**
- **production feasibility**
- **continuity across the video**
- **legal/practical safety**, especially around direct use of copyrighted reference imagery

This is critical.

S5 is not optimizing only for “beauty”.
It is optimizing for:

> the strongest visual solution that can actually be generated, edited, and used safely downstream.

---

## 5. What S5 is not

S5 is **not**:

- a web research sector
- an asset sourcing sector
- a pure prompt-writing sector
- a final asset generation sector
- a final editing/compositing sector
- a simple scene-to-image mapper

S5 must not be reduced to:
- “pick an image for each scene”
- “write one prompt per scene”
- “choose references and move on”

That would collapse the creative and editorial intelligence the pipeline needs.

---

## 6. The key conceptual shift: references are not the final assets

One of the most important decisions reached in discussion is this:

### 6.1 S4 outputs are primarily a **reference layer**, not necessarily the final visual layer

The images and assets discovered in S4 may be useful for:
- factual grounding
- architectural reference
- historical anchoring
- mood reference
- composition hints
- period detail
- lighting reference
- transformation guidance

But they should **not** be assumed to be the preferred final assets used directly in the video.

### 6.2 Why this matters

There are many reasons why direct use is often undesirable:

- copyright risk
- watermarks
- inconsistent visual style
- incompatible framing
- poor quality or low resolution
- inability to maintain continuity across scenes
- lack of creative control

### 6.3 Resulting policy direction

The emerging conceptual policy is:

> S4 is largely **reference-first**.
> S6 should usually produce the final assets.
> Direct use of S4-discovered material should be exceptional and explicit, not the default assumption.

That means S5 must often treat S4 outputs as:
- things to learn from
- things to extract structure from
- things to guide generation with
- things to preserve selectively
- things to transform rather than use literally

---

## 7. The real job of S5: scene-level creative translation

If S4 is the reference layer and S6 is the production layer, then S5 becomes the **creative translation layer**.

It translates:
- narrative meaning
- semantic grounding
- discovered references
- production constraints
- editorial realities

into:
- a production-ready scene plan
- slot-by-slot visual requirements
- transformation rules for reference material
- generation instructions for S6
- editorial guidance for final assembly

That is why S5 is much closer to a **creative director of the video** than to a generic planning step.

---

## 8. The basic unit of work in S5

### 8.1 External unit = the scene

The natural external unit of S5 is the **scene**.

This is the level at which S5 should answer:
- what this part of the video needs visually
- what kind of coverage it requires
- what S6 must produce for it

### 8.2 Internal complexity inside the scene

Even though the scene is the unit, the decision is not simple.
A scene may require:

- a hero image
- multiple alternatives
- factual support visuals
- details
- overlays
- compositional elements
- transition assets
- short motion bases
- symbolic or atmospheric elements

So the true internal object is not “the one correct image for the scene”.

It is something closer to a:

- **scene visual coverage plan**
- **scene visual production plan**
- **scene kit plan**

### 8.3 Why one asset per scene is too weak

A strong editor does not usually work with only one asset per scene.
A stronger model is:

- one main piece
- several supports
- variants
- optional alternatives
- composition-ready components
- structured coverage that allows real editorial choice later

This is one of the defining insights of the S5 redesign.

---

## 9. The scene kit / coverage concept

### 9.1 Why S5 should not think in terms of one final image

If S5 tries to over-close the scene too early, it becomes brittle.
Any of the following can break the outcome:

- generation underperforms
- the reference is stronger than expected but legally unsafe to use directly
- one asset feels repetitive relative to nearby scenes
- the editor needs more than one beat to make the scene work

### 9.2 Stronger model

S5 should think in terms of:

> what visual **coverage** the scene needs

rather than:

> what single image should represent the scene

This allows the scene to be resolved as:
- hero shot
- hero plus supports
- contrast pair
- fast sequence
- layered composition
- base image plus overlays/stickers
- short motion base plus support elements

### 9.3 Practical meaning

The outcome of S5 should make it possible for S6 to produce a **production-ready scene kit**.

That kit can later be used by the final assembly layer to build the best scene composition.

---

## 10. What S5 must possess when it starts

For S5 to do its job properly, it must start with more than just a scene sentence and a folder of references.

### 10.1 Narrative scene package

For each scene, S5 should possess:
- `scene_id`
- scene text / narration segment
- scene summary
- narrative function
- emotional target
- sequence position
- relation to previous scene
- relation to next scene

Because S5 is not directing isolated images.
It is directing scenes inside a sequence.

### 10.2 Semantic grounding

From S3, S5 should possess enough grounding to understand:
- entities
- locations
- objects
- symbolic dimensions
- event structure
- scene-target linkage

This helps it distinguish:
- what is concrete
- what is interpretive
- what is symbolic
- what must remain historically or structurally grounded

### 10.3 Reference layer from S4

From S4, S5 should possess:
- references per scene/target
- factual anchors
- candidate images/pages/previews
- stylistic references where relevant
- coverage state
- unresolved gaps
- notes on whether material is suitable only as reference or potentially usable in other ways

### 10.4 Downstream production constraints

S5 should also possess enough downstream knowledge to reason practically, such as:
- what kind of generation the system can do
- whether motion generation is available or expensive
- what kind of assembly patterns are supported later
- how much visual density is acceptable
- what continuity constraints matter across scenes
- general stylistic constraints of the channel or account

This is what makes S5 creative **under constraints**, not creatively naive.

---

## 11. The decision stack S5 must resolve per scene

For each scene, S5 must answer a consistent set of decision questions.

### 11.1 What does the scene need to communicate visually?
This includes:
- what the viewer must understand
- what the viewer must feel
- whether the scene is literal, atmospheric, symbolic, or mixed

### 11.2 What visual mode is correct?
Examples:
- factual grounded
- factual plus cinematic enhancement
- evocative reconstruction
- symbolic visualization
- hybrid grounded-symbolic

### 11.3 What coverage strategy fits the scene?
Examples:
- single hero
- hero plus supports
- fast sequence
- layered composition
- motion-led coverage
- contrast progression

### 11.4 How many visual pieces does the scene need?
This defines whether the scene should be served by:
- one main visual
- multiple stills
- several supports
- overlays
- optional variants
- motion elements

### 11.5 What role does each piece serve?
Each planned visual piece must have a role, such as:
- hero establishing
- factual anchor
- support detail
- cinematic variant
- symbolic overlay
- transition bridge
- motion base
- fallback alternative

### 11.6 Which S4 references belong to each planned piece?
S5 must not just attach references vaguely.
It must decide:
- which references matter for which slot
- what each reference contributes
- which references are primary vs secondary

### 11.7 What must be preserved from those references?
Examples:
- architecture
- silhouette
- character identity
- period detail
- spatial logic
- mood
- lighting logic
- object design

### 11.8 What must not be copied literally?
This is critical because of copyright and quality.
Examples:
- exact composition
- exact framing
- watermark-bearing layout
- source-specific visual signatures
- overly direct recreation of protected imagery

### 11.9 What production method should be used for each visual slot?
Examples:
- fresh generation
- reference-guided generation
- image-to-image regeneration
- multi-reference synthesis
- stylized reconstruction
- motion generation

### 11.10 How much creative freedom is allowed per slot?
Some slots need strict fidelity.
Others can be more interpretive.

### 11.11 What continuity must the scene respect?
This may include:
- same location identity
- tonal progression from previous scene
- setup for next scene
- continuity of objects/characters
- palette or mood evolution

### 11.12 What editorial pattern is likely best downstream?
Examples:
- hold on a hero
- hero then detail support
- factual anchor after cinematic opening
- quick progression
- layered composition

This does not mean S5 edits the scene.
It means S5 prepares the scene intelligently for later editing.

---

## 12. The differentiated architecture of S5

The architecture that emerged for S5 is intentionally different from a naive linear step.

### 12.1 Why a single monolithic decision is wrong

If one agent or one long process tries to:
- understand the whole video
- direct every scene
- reconcile continuity
- plan every slot
- prepare downstream production

all in one pass, the likely result is:
- high latency
- cognitive overload
- inconsistent plans
- poor scene-level depth
- weak continuity handling

### 12.2 Why a purely flat parallel swarm is also wrong

If every scene is planned independently with no shared global frame, the likely result is:
- inconsistency between scenes
- drift in style
- conflicting continuity
- different levels of ambition and density scene by scene

### 12.3 The conceptual answer

The most coherent structure is:

> **global understanding -> scene-level direction -> global reconciliation**

Even before implementation details are specified, this is the right mental model.

### 12.4 What that means conceptually

S5 should behave like a sector that:
1. first understands the video as a whole
2. then directs scenes individually
3. then re-checks the set as a whole before handing off to S6

This is one of the most important architectural conclusions of the discussion.

---

## 13. The global layer of S5

Before scene-level plans are created, S5 needs a **global direction frame** for the video.

### 13.1 Why this layer exists

Without a global layer:
- every scene may invent its own visual logic
- continuity becomes accidental
- the overall arc of the video is weakened

### 13.2 What the global layer should establish conceptually

It should establish things like:
- overall visual posture of the video
- how grounded vs cinematic the video should feel overall
- continuity anchors across scenes
- whether some scenes should deliberately intensify or contrast with others
- what kinds of scene resolutions are encouraged or discouraged
- how dense the visual coverage should be in different portions of the video

### 13.3 What the global layer is not

It is not yet the final plan per scene.
It is the **shared directional context** that individual scene plans must obey or at least relate to.

---

## 14. The scene-level layer of S5

This is the core of the sector.

### 14.1 What happens here

For each scene, S5 should produce a specific visual production plan that includes:
- scene understanding
- visual strategy
- coverage pattern
- slots to be produced
- slot roles
- linked references
- preserve rules
- avoid rules
- generation modes
- continuity notes
- editorial guidance

### 14.2 Why this is the heart of S5

This is where S5 stops being abstract and becomes operational.

A good S5 scene plan should make S6’s job dramatically easier because S6 no longer needs to guess:
- what the scene wants
- what the references are for
- what the final production pattern should be

---

## 15. The reconciliation layer of S5

After multiple scene plans exist, they still need to be read as a set.

### 15.1 Why this layer is necessary

Individual scenes can be good in isolation and still fail together.

Common risks include:
- repeated visual patterns across too many scenes
- inconsistency of tone
- over-generation in trivial scenes and under-planning in key scenes
- discontinuity between adjacent scenes
- conflicting treatment of recurring locations or characters

### 15.2 What this layer should conceptually do

The reconciliation layer should ensure:
- the plans make sense as one video
- continuity is explicit where needed
- contrast is intentional, not accidental
- the final S5 output is coherent enough for S6 to execute without amplifying contradictions

This layer does not eliminate scene individuality.
It keeps the video from fragmenting.

---

## 16. The main output object of S5

The conceptual core output of S5 should be a per-scene artifact similar to:

- `scene_visual_production_plan.json`

This should be understood as the scene-level contract between S5 and S6.

### 16.1 What this scene plan should contain conceptually

For each scene it should contain, at minimum:
- what the scene means
- what the scene must communicate
- what visual mode is correct
- what coverage pattern it needs
- what slots must exist
- what role each slot serves
- what references feed each slot
- what must be preserved
- what must not be copied literally
- what generation mode is expected per slot
- what continuity constraints matter
- what editorial pattern is recommended

### 16.2 Why this matters

The scene plan is the place where the S5 intelligence becomes explicit and inspectable.
Without this, S6 would be forced to infer too much.

---

## 17. The compiled output of S5

In addition to scene-level plans, S5 should produce a compiled sector-level artifact similar to:

- `s5_visual_direction_pack.json`

### 17.1 Purpose of the compiled pack

This pack should serve as the sector-level downstream handoff.
It should consolidate:
- shared video direction context
- scene plans
- continuity notes
- sector-level warnings
- delivery expectations for S6

### 17.2 Why both scene-level and compiled outputs matter

Scene-level outputs are needed because scenes are the real unit of direction.
Compiled output is needed because downstream sectors also need a coherent sector-wide handoff.

---

## 18. Relationship between S5 and S6

### 18.1 S5 does not generate the final visuals

S5 prepares the production plan.
S6 produces the final visual assets.

### 18.2 What S6 should receive from S5

S6 should receive, directly or indirectly:
- scene-level production plans
- compiled sector-level visual direction pack
- slot definitions
- reference mappings
- transformation rules
- generation modes
- continuity constraints
- minimum delivery expectations

### 18.3 Why this handoff is strong

It means S6 does not have to guess:
- why the scene exists
- what role each output should play
- how tightly it should stay to the reference
- whether it is generating hero material, support material, overlays, or fallback visuals

S6 becomes a production executor of a strong creative plan rather than an improviser.

---

## 19. Relationship between S5 and final scene assembly

### 19.1 S5 does not do final editing

S5 is not the final compositing layer.
It should not decide exact timing, exact cuts, or final frame ordering in the way a downstream editor would.

### 19.2 But S5 must still think editorially

S5 must prepare scenes with downstream editing in mind.
That means it should express:
- whether the scene likely works as a hero hold or sequence
- whether it benefits from contrast between multiple pieces
- whether overlays should remain secondary
- whether a factual anchor should enter before or after a cinematic variant
- whether the scene needs more than one beat

### 19.3 Why this matters

Without this editorial intelligence, S5 would produce technically complete but strategically weak plans.
The final editor would then be forced to re-invent creative direction from scratch.

The correct separation is:
- **S5** directs the coverage
- **S6** materializes the assets
- **final assembly** composes and edits using that directed asset space

---

## 20. S5 as the creative director of the video

The strongest interpretation of S5 is this:

> S5 is the sector that acts as the creative director of the video at the scene-resolution layer.

That means S5 must be able to reason like a strong human video editor/director would reason:
- not only what to show
- but how to show it
- how much of it to show
- what type of visual treatment is correct
- what should be grounded
- what can be transformed
- what must remain coherent across the sequence
- how to leave the final editor enough material to build a strong scene

This is why S5 is strategically central.

---

## 21. The differentiated architecture in one sentence

If the concept of S5 had to be summarized in one sentence, it would be:

> S5 is the sector that converts narrative + semantic grounding + S4 references into scene-level visual production plans that define how each scene should be covered and what S6 must generate for strong downstream editing.

---

## 22. Conceptual success criteria for S5

S5 should be considered conceptually successful if it can do all of the following:

1. treat scenes as directed visual units, not just prompt targets
2. use S4 outputs as reference material intelligently rather than naively
3. define scene coverage rather than just one image per scene
4. prepare S6 with enough structure to avoid guesswork
5. preserve continuity and sequence logic across scenes
6. reduce direct copyright exposure by preferring transformed/generated final outputs over literal direct reuse
7. leave the final editor with a strong, structured visual asset space rather than a brittle one-shot plan

---

## 23. Open design questions that remain for later documents

This concept document deliberately leaves some things open, to be frozen later in more technical docs.

These include:

- exact schema of `scene_visual_production_plan.json`
- exact schema of `s5_visual_direction_pack.json`
- exact enums for scene modes, slot roles, and generation modes
- exact distinction between required and optional fields
- exact handling of scene-internal beats versus scene-level planning only
- exact continuity modeling across scenes
- exact relationship between S5 scene plans and S6 output grouping
- exact runtime orchestration model and materialization strategy

These should be defined only after the conceptual foundation in this document is accepted.

---

## 24. Summary

The new concept of S5 is much stronger than a generic “visual direction” placeholder.

S5 is not just about choosing images or writing prompts.
It is the sector where the system decides, scene by scene:

- what the scene must communicate visually
- what kind of visual treatment is correct
- what references matter
- how those references should be transformed
- what visual coverage the scene needs
- what final production slots must exist
- what S6 must generate
- how the scene should be prepared for final editing

S4 provides the discovered world.
S5 decides how to turn that discovered world into directed visual coverage.
S6 materializes that coverage.
Final assembly uses it to build the scene.

That is the conceptual core of the new S5.
