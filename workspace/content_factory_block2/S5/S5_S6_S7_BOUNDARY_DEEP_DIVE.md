# S5 → S6 → S7 Boundary Deep Dive

_Status: conceptual deep-dive / working reference_  
_Last updated: 2026-04-07_  
_Owner: Tobias_

---

## 1. Purpose of this document

This document preserves the **richer reasoning layer** behind the new S5→S6→S7 boundary.

It complements the more structured V1 documents by capturing:
- the design intent behind the scene kit model
- the strategic shift away from rigid scene closure
- the role of grounding references from S4
- the relationship between kit design, kit materialization, and downstream editorial freedom
- why this architecture is stronger than earlier, more rigid formulations

This document is intentionally more explanatory than `S5_SCENE_KIT_OBJECTS_V1.md`.
It should be read as a conceptual working reference rather than a final contract document.

---

## 2. The central problem this boundary is solving

The system is trying to move away from a rigid visual pipeline where scenes become over-determined too early.

In a rigid pipeline, the pattern tends to be:
- decide what the scene should show
- generate one or a few narrow outputs
- force the downstream editor to use them

This creates several problems:
- low editorial freedom
- weak resilience when generation underperforms
- repetitive visual treatment
- poor ability to vary pacing or emphasis
- little room for downstream creative judgment

The new boundary exists to solve that.

The new objective is not to predict the single correct visual outcome for the scene.
The objective is to ensure that the scene has the **right structured asset space** to be resolved well later.

---

## 3. The strongest formulation of the new chain

The chain is now best understood as:

### S4 = factual visual grounding
S4 discovers:
- who and what is real in the scene world
- what people, locations, architecture, objects, and artifacts matter
- what reference material exists that can anchor generation later

### S5 = scene kit design
S5 decides:
- what kinds of assets the scene needs
- how much grounding vs freedom each part of the scene requires
- what the downstream production space for the scene should look like

### S6 = scene kit materialization
S6 produces:
- actual assets matching the intended scene kit
- enough diversity and grounding to satisfy the kit
- usable material for downstream editorial work

### S7 = editorial scene resolution
S7 receives:
- the materialized kit
- audio and timing context
- enough metadata to understand the kit

S7 then behaves more like a real editorial team, choosing and assembling from a meaningful asset space rather than obeying a rigid instruction script.

---

## 4. The key insight: a scene should receive a kit, not a verdict

A weak planner gives the scene a verdict.
A strong scene-kit system gives the scene a kit.

A verdict sounds like:
- this is the image for the scene
- this is the exact composition
- this is the exact treatment

A kit sounds like:
- this scene needs a grounded establishing option
- this scene also needs stronger supporting detail
- it may benefit from a more cinematic reinterpretation
- it needs at least one usable transition-capable option
- downstream should have enough material to hold, cut, or contrast intelligently

This is a radically better fit for a system that wants real editorial behavior later.

---

## 5. Why S4 is foundational in this architecture

The move toward scene kits does not reduce the importance of S4.
It makes its role more strategically precise.

The system has already seen the real failure mode where videos mention:
- a specific person
- a specific building
- a specific object
- a specific historical artifact

but the visual layer shows the wrong thing.

That error damages trust and quality immediately.

So S4 is indispensable because it gives the system a factual base layer.

However, S4 references are often not directly suitable as final assets because they may contain:
- copyright issues
- watermarks
- weak composition
- inconsistent style
- low resolution
- framing that does not serve the scene well

So the correct rule is:

> S4 should usually be treated as a **grounding and reference layer**, not a direct-final-asset layer.

That rule is one of the strongest foundations of the new design.

---

## 6. What S5 is really doing now

S5 is not primarily selecting images.
It is not primarily writing prompts.
It is not primarily deciding the final cut.

S5 is defining the **scene kit target**.

That means S5 is deciding things like:
- how much visual coverage the scene needs
- what different functions the scene’s assets should serve
- where factual fidelity is essential
- where a more cinematic or evocative approach is allowed
- what S6 should produce so that S7 has genuine editorial freedom later

This is much closer to a creative director designing a production-ready asset space than to a generic visual planner.

---

## 7. Why scene kits enable real editorial emergence

The deeper purpose of scene kits is to create the conditions for S7 to be meaningfully creative.

If S7 receives:
- one asset per scene
- or a tiny rigid set of outputs
- or a pre-closed instruction that already decides too much

then S7 is not really editing.
It is decorating or mechanically sequencing.

But if S7 receives:
- a structured set of grounded, role-aware assets
- multiple options with different functions
- enough variety to hold, cut, contrast, or bridge
- enough metadata to understand what it is working with

then S7 can begin to behave like a real editor.

That is the larger strategic value of the scene kit model.

---

## 8. The role of asset families

The best internal primitive for the scene kit is not “one exact slot equals one exact asset.”

The better primitive is the **asset family**.

An asset family says:
- what kind of material this group represents
- what concrete mission it serves in the scene
- how important it is
- roughly how many assets should exist in that group
- how grounded or free it should be

This distinction matters because a broad type like `support` is still too vague for S6 unless the family also says support **for what**.

That is why the emerging grammar needs both:
- a broad family category
- and a concrete family-level intent / mission

This is better than rigid slots because it preserves structure while still allowing:
- variation
- alternative versions
- partial satisfaction
- richer materialization behavior

Examples of family purposes include:
- grounded establishing material
- supporting factual material
- detail inserts
- atmospheric variation
- cinematic reinterpretation
- transition-capable material
- motion-friendly material
- fallback alternatives

But in practice these need to be made more concrete through family-level intent, such as:
- identify the central political actor of the scene
- establish the real architectural object of the scene’s ambition
- reinforce the gambling/casino reality under discussion
- keep a symbolic scene tied to the grounded world of the video

In V1, these should remain modest and practical rather than over-taxonomized.

---

## 9. Grounding versus freedom is the heart of the system

One of the most important tensions in the new architecture is:

- some parts of the visual output must remain tightly grounded
- other parts should be allowed to open up creatively

If everything is tightly constrained by reference, the system becomes stiff.
If everything is free, the system drifts away from the reality of the video.

The point of the scene kit is not to choose one side.
The point is to distribute this tension intelligently across the scene.

For example:
- the identity of a real person may need very high grounding
- a building exterior may require strong architectural fidelity
- a mood-supporting insert may tolerate more freedom
- a symbolic punctuation shot may tolerate even more freedom

This is why a scene kit is superior to a single-scene prompt.
It lets the system express mixed requirements within one scene.

---

## 10. S6 is not just “generation” — it is kit materialization

S6 becomes much clearer under this model.

It is not merely generating whatever the prompt says.
It is materializing the intended scene kit.

That means S6 needs to reason in terms of:
- family satisfaction
- coverage completeness
- usable variety
- grounding preservation
- production feasibility

S6 may use different methods to do this, such as:
- reference-guided generation
- regeneration from references
- multi-reference synthesis
- generation from scratch
- motion generation where appropriate

The important point is that S6 is not inventing the scene kit.
It is delivering against a designed kit.

---

## 11. Why S6 constraints must influence S5

A naive version of S5 would design the ideal creative kit for every scene.
That would fail immediately if S6 cannot afford or realize it.

So the boundary must include practical constraints, such as:
- which generation modes are allowed
- whether motion generation is allowed
- how much motion budget exists
- how complex kits are allowed to become
- what asset density is realistic for a given video

This prevents the system from designing impossible kits.

The correct principle is:

> S5 should design for creative usefulness under real materialization constraints.

---

## 12. Why `video_direction_frame` matters more than it first appears

Without a global frame, scene kits may drift into incompatible local logic.

That can create problems like:
- one scene strongly documentary
- another heavily stylized in an unrelated way
- another visually loose despite the video needing high factual discipline

The role of `video_direction_frame` is to give all scenes a common directional baseline.

For V1, this should focus on:
- dominant visual era
- dominant style posture
- tonal/palette posture
- grounding baseline
- production ceiling
- allowed generation modes
- motion posture

This is enough to prevent major drift without forcing early over-modeling of continuity.

---

## 13. Why V1 should stay simpler than the full conceptual richness

The full concept can support many nuanced distinctions.
But V1 should not try to encode all of them.

If V1 becomes too rich too early, likely failure modes include:
- LLM inconsistency
- schema instability
- poorly understood downstream fields
- fake precision without real consumer value

So the right move is:
- preserve conceptual richness in explanatory docs
- compress the actual V1 object model
- only expand later when downstream consumers truly need more structure

This is why fields like detailed editorial timing grammar should remain lightweight in V1.

---

## 14. Stress-test examples the boundary must survive

A concept like this should not be trusted until it survives multiple scene types.

At minimum, the boundary should be tested against the following scene classes.

### 14.1 Factual person-centered scene
Example pattern:
- a scene about a real historical figure
- identity fidelity matters strongly
- at least one family should protect recognizability
- other families may still allow more cinematic support material

What this tests:
- identity grounding
- reference dependence
- controlled freedom

### 14.2 Architecture / place scene
Example pattern:
- a scene anchored around a real location or building
- architecture must remain legible and correct
- scene may still benefit from atmospheric or cinematic variation

What this tests:
- structural grounding
- scene coverage diversity
- relation between factual establishing and evocative support

### 14.3 Symbolic / evocative scene
Example pattern:
- a scene where emotional or conceptual weight matters more than factual depiction
- no direct literal visual exists that fully resolves the scene

What this tests:
- openness of the kit model
- symbolic freedom without total drift
- whether grounding posture can relax safely where appropriate

### 14.4 Transition-oriented scene
Example pattern:
- a scene that mainly exists to bridge energy, theme, or pacing between two stronger scenes
- scene may require less heavy factual anchoring but stronger editorial usefulness

What this tests:
- whether the kit can include material designed primarily for editorial transition value
- whether the model handles lower-content but high-function scenes

---

## 15. What S7 should feel like under this model

The intended downstream experience is not:
- “here is the only thing you can use for this scene”

The intended downstream experience is:
- here is the scene
- here is the audio and timing context
- here is the materialized kit
- here are the roles and strengths of the available assets
- now edit the scene intelligently

This is the architecture required if S7 is expected to act like a real editorial layer rather than a deterministic renderer of pre-chosen shots.

---

## 15.1 Scene kit versus final composition

A key conceptual distinction must remain explicit.

The scene kit is **not** the final composition of the scene.

That means S5 should not act as if it is already deciding:
- the exact split-screen layout
- the exact grid or multi-panel layout
- the exact sticker arrangement
- the exact layering pattern used on screen
- the exact sequence timing of visual changes
- the final edit structure of the scene

Those decisions belong more naturally to S7, which is the layer expected to use real editorial judgment.

What S5 must do is something different and more upstream:
- ensure that the kit is rich enough to support multiple legitimate downstream resolutions
- ensure that the scene has enough grounded and useful material for varied editorial treatment
- ensure that the kit does not collapse the scene into a single brittle option too early

So the correct distinction is:

- **S5 designs the scene’s asset space**
- **S7 resolves the final composition from that space**

This matters because otherwise the system risks one of two failures:
- S5 becomes too controlling and reintroduces rigidity
- or S5 becomes too vague and leaves S7 with freedom in name only

The intended architecture is the middle path:

> S5 prepares the space of editorial possibility.  
> S7 turns that possibility into an actual composed scene.

---

## 16. A compact example

Consider a scene about Hotel Quitandinha as both a real place and a symbol of lost grandeur.

A weak system might ask for:
- one image of the hotel

A stronger scene-kit system might ask for:
- a grounded establishing family showing the real hotel clearly
- a supporting detail family showing architectural details or relevant areas
- an atmospheric family emphasizing grandeur/decay tension
- a transition-capable family useful for pacing or movement across adjacent scenes

Then S6 materializes those families.
Then S7 can decide whether to:
- open with the factual establishing image
- cut into details
- shift into a more atmospheric reinterpretation
- bridge to the next scene using transition-capable material

That is exactly the kind of flexibility the rigid pipeline lacks.

---

## 17. What this boundary deliberately does not solve yet

This deep-dive should not be mistaken for a claim that everything is already defined.

It does **not** yet freeze:
- final JSON shapes
- exact enums for all fields
- runtime topology
- exact S6 operator decomposition
- exact S7 editing protocol
- deep continuity modeling

What it does freeze is the stronger conceptual architecture that those future decisions should now obey.

---

## 18. Final summary

The most important change is this:

> The pipeline should stop trying to decide the final image of the scene too early and should instead design and materialize the right scene kit for that scene.

Under this model:
- S4 anchors reality
- S5 designs the kit
- S6 materializes the kit
- S7 edits from the kit

This creates a pipeline that is:
- less rigid
- more grounded
- more editorially useful
- more capable of real creative behavior downstream

That is the deeper strategic meaning of the S5→S6→S7 boundary redesign.
