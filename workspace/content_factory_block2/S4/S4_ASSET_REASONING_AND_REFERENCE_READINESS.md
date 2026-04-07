# S4 Asset Reasoning and Reference Readiness

_Status: implemented (V1)_  
_Last updated: 2026-04-07_  
_Owner: Tobias (concept), Claude Code (implementation)_

---

## 1. Purpose of this document

This document captures a newly clarified requirement for S4:

> S4 should not only find and approve assets. It should also make approved assets more intelligible and reusable as downstream references.

This need emerged from deeper S5 design work.

As S5 evolves toward scene kit design, it becomes increasingly clear that downstream sectors do not only need:
- assets grouped by target
- approved images on disk
- target-local folders

They also need enough semantic understanding of each asset to answer questions like:
- what exactly does this asset show?
- why is it useful?
- what kind of reference value does it have?
- what should be preserved if it is used in generation?
- which scenes or family types might benefit from it?
- is it useful only inside its source target, or more broadly?

This document defines that requirement conceptually.

---

## 2. Why target-local organization is not enough

The current S4 structure already provides meaningful value by organizing assets under targets.
That is useful for retrieval and local grounding.

However, target-local storage alone is not enough for downstream reference selection.

Reasons include:
- multiple targets may surface visually overlapping material
- a highly useful asset may sit under a target that is only one of its valid interpretations
- target folders do not necessarily express why an asset is good
- target folders do not necessarily express how an asset should be used as a generation reference
- target assignment may be operationally acceptable while still being semantically incomplete

As a result, a downstream sector such as S5 can struggle to choose references efficiently if it only sees “approved assets inside target folders.”

---

## 3. Concrete motivating example

In the Quitandinha video, an asset may be stored under a particular target folder and still be more useful for another scene or another future family type.

For example, an image that lives under one target may:
- technically fit that target well enough
- but be even more valuable for a later scene about casino prohibition, social change, or institutional decline

This means the asset’s value is not fully captured by its target membership alone.

The system needs a way to express:
- what the asset depicts
- what kinds of factual anchors it contains
- what kinds of downstream uses it supports
- where it may be reusable beyond its source target

---

## 4. The new requirement

S4 needs to start producing a more **reference-ready layer**.

That means an approved asset should become more than:
- a file on disk
- a target-local hit
- a pass/fail evaluation outcome

It should also become a downstream-usable reference object.

In simpler terms:

> S4 should graduate from “asset found” toward “asset understood enough to be selected well later.”

---

## 5. What “reference-ready” means

A reference-ready asset is an approved asset that also carries enough structured meaning for downstream sectors to select it intelligently.

This does **not** necessarily require a huge metadata burden.
But it does require more than filename + target folder + quality score.

At minimum, a reference-ready asset should be understandable in terms of:
- what it depicts
- what kind of factual anchor it offers
- what kind of reference value it has
- what should be preserved if used in generation
- what risks exist if it is reused blindly

---

## 6. Why S5 needs this

The emerging S5 scene-kit model depends heavily on choosing the right `reference_inputs[]` for each asset family.

That selection becomes much easier if S4 already provides lightweight reasoning like:
- identity anchor
- architecture anchor
- object-detail reference
- mood reference
- symbolic support
- transition-friendly material
- broad scene relevance beyond the source target

Without this, S5 risks becoming an expensive re-interpretation layer that has to understand every image from scratch.

That would be a poor architectural split.

The better split is:
- S4 makes assets reference-ready
- S5 consumes that layer to build scene kits more intelligently

---

## 7. Conceptual fields that may be useful

The following fields are not yet final schema proposals, but they illustrate the kind of information that would make an asset reference-ready.

### Identity / source
- `asset_id`
- `source_target_id`
- `filepath`

### Depiction understanding
- `depicts_summary`
- `depiction_type`
  - examples: `person`, `building`, `location`, `object`, `vehicle`, `weapon`, `interior`, `mixed`, `symbolic`
- `factual_entities_present[]`

### Reference value
- `reference_value[]`
  - examples:
    - `identity_anchor`
    - `architecture_anchor`
    - `detail_reference`
    - `composition_hint`
    - `lighting_hint`
    - `mood_reference`
    - `symbolic_support`
    - `transition_support`

### Reuse / downstream utility
- `likely_use_cases[]`
- `cross_target_relevance[]`
- `scene_relevance_hints[]`

### Generation guidance
- `preserve_if_used[]`
- `avoid_if_used[]`
- `reasoning_summary`

### Risk notes
- `reuse_risks[]`
  - examples:
    - misleading if used as direct identity proof
    - visually strong but target assignment too narrow
    - useful as mood reference, weak as factual anchor

---

## 8. Two possible implementation directions

This requirement can be met in at least two ways.

---

## 8.1 Option A — embed lightweight reasoning into the current evaluator path

Under this option, the current asset evaluation step would be extended so that approved assets also receive lightweight semantic/reference metadata.

This is attractive because:
- the evaluator already looks at the asset
- no extra full sector step is required immediately
- the system can evolve incrementally

This path would likely be the fastest way to improve downstream reference selection.

### Risks
- the evaluator may become overloaded
- “is this a good asset?” and “what kind of reusable reference is this?” are not identical questions
- the metadata shape may grow too much if not controlled carefully

---

## 8.2 Option B — create a later explicit asset reasoning step

Under this option, S4 would first approve assets, then a later step would annotate or interpret them for downstream reuse.

This is attractive because:
- responsibilities stay cleaner
- reasoning can evolve independently
- downstream reference-selection support can become more sophisticated later

### Risks
- more moving parts
- more latency
- more implementation work
- possible redundancy if a lighter embedded solution would have been enough initially

---

## 9. Current recommendation

The current recommendation is:

> start with a lightweight embedded approach inside the evaluator or immediately adjacent to it, but design the output so it can later be separated into its own step if needed.

This provides a good balance between:
- near-term practicality
- downstream usefulness
- future architectural cleanliness

In other words:
- do not create a heavy new subsystem immediately
- but do start producing reference-ready reasoning now

---

## 10. What this changes downstream

If S4 becomes reference-ready, S5 gains several important advantages.

### 10.1 Better `reference_inputs[]` selection
S5 can choose references based on:
- what they actually depict
- what they are best at anchoring
- what kind of family they should feed

### 10.2 Better cross-target reuse
Useful assets are no longer trapped conceptually inside one target folder.

### 10.3 Better grounding discipline
S5 can more reliably choose the correct references for scenes involving:
- real people
- places
- architecture
- equipment
- vehicles
- objects
- artifacts

### 10.4 Lower cognitive burden in S5
S5 no longer needs to rediscover what each asset means from scratch.

---

## 11. What this requirement does not mean

This requirement does **not** mean:
- S4 must become a giant semantic knowledge base immediately
- every asset needs an essay attached to it
- target-local structure should be abandoned
- downstream sectors should stop reasoning about references altogether

The target-local structure remains useful.
The point is simply that it is not sufficient by itself for the newer architecture.

---

## 12. Summary

The emerging S5 architecture revealed a new upstream requirement:

> S4 should not only produce approved assets per target. It should also produce assets that are more understandable and more selectable as references for downstream generation and scene-kit design.

The right next step is not to overbuild this immediately.
The right next step is to make approved assets more reference-ready with lightweight asset-level reasoning, likely embedded in or near the evaluator path first.

This would significantly strengthen the S4→S5 boundary and improve the quality of scene-kit design later.

---

## 13. Implementation status

**Implemented 2026-04-07** following the recommended Option A (embedded in evaluator) + compiled pool approach.

### What was built

**Two-layer output architecture:**

1. **Per-asset sidecar** (`{filename}.reference_ready.json`) — written by `s4_visual_evaluator.py` next to each approved asset in `targets/{tid}/assets/`. Contains: `asset_id`, `source_target_id`, `source_target_label`, `source_target_type`, `filepath`, `relevance`, `quality`, `depicts`, `depiction_type`, `reference_value[]`, `preserve_if_used[]`, `reasoning_summary`.

2. **Compiled pool** (`compiled/s4_reference_ready_asset_pool.json`) — generated by `pack_compiler.py`. Aggregates all sidecars with `scene_relevance` (derived from target→scene linkage in intake) and provides grouped views: `by_target`, `by_reference_value`, `by_depiction_type`.

### How it works
- The evaluator prompt was extended to request reference readiness fields for approved images (relevance >= 7) in the same API call — zero extra latency
- GPT-5.4-nano produces the extra fields alongside the existing evaluation
- The sidecar is the granular source of truth; the compiled pool is the downstream selection surface

### E2E validation (Quitandinha pilot, 006_pt)
- 61 assets with 100% field fill rate across all reference readiness fields
- Grouped views: 18 targets with assets, 7 reference value categories, 7 depiction types
- Cost impact: +$0.03-0.05/video (negligible — within existing $0.14 budget)
- Latency impact: none (same API calls, slightly more output tokens)
