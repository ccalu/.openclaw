# S5 Scene Kit Pack V1 Draft

_Status: runtime-facing output draft_
_Last updated: 2026-04-07_
_Owner: Tobias_

---

## 1. Purpose of this document

This document defines the preferred V1 direction for the compiled sector-level handoff artifact:
- `s5_scene_kit_pack.json`

Its purpose is to make explicit how the S5 output layer should be organized so that:
- truth remains granular and inspectable
- S6 receives a clear sector-level handoff surface
- retries and re-runs remain scene-granular
- the compiled pack does not silently become a competing source of truth

This document exists because the question is **not only** whether S5 should emit one file or many files.
The stronger question is:

> what should be the canonical truth layer of S5, and what should be the practical downstream handoff surface for S6?

---

## 2. Core decision

The preferred V1 decision is:

### 2.1 Canonical truth layer
S5 should treat the following as canonical truth:
- `video_direction_frame.json`
- `scene_kit_specs/<scene_id>.json`

### 2.2 Derived downstream handoff surface
S5 should also emit:
- `s5_scene_kit_pack.json`

This compiled pack should be treated as:
- a downstream-facing handoff artifact
- a sector-level index / readiness surface
- a practical entry surface for S6

It should **not** be treated as a sovereign truth artifact independent from the underlying canonical artifacts.

---

## 3. Why this hierarchy is preferred

This hierarchy is preferred because it preserves both sides of the problem.

### 3.1 It preserves granular truth
Per-scene artifacts remain the right truth layer for:
- inspection
- retry
- re-run
- debugging
- scene-level downstream work

### 3.2 It gives S6 a cleaner entry surface
A compiled pack gives S6:
- a single sector-level handoff surface
- scene ordering
- readiness/index information
- a simple place to begin consuming S5 outputs

### 3.3 It prevents compiled-truth drift
If the compiled pack becomes a second independent truth, drift risk appears quickly.

The preferred rule is:

> the pack is derived from the canonical artifacts and must not silently become a separate truth model.

---

## 4. Preferred artifact set for S5

The preferred output posture is:

### 4.1 Canonical global artifact
- `video_direction_frame.json`

### 4.2 Canonical per-scene artifacts
- `scene_kit_specs/<scene_id>.json`

### 4.3 Derived compiled handoff artifact
- `s5_scene_kit_pack.json`

### 4.4 Runtime/control artifacts
- `status.json`
- `checkpoint.json`
- `s5_completed.json`
- `s5_failed.json`

---

## 5. Role of `s5_scene_kit_pack.json`

The pack should be understood as the **sector-level handoff surface** between S5 and S6.

Its main roles are:
- tell S6 that S5 is ready
- expose the global video-level frame
- expose scene ordering / scene inclusion
- expose where the per-scene canonical specs live
- expose enough metadata that S6 can reason about readiness without having to scan the entire sector folder blindly

It is a downstream convenience and coordination artifact.
It is not the place where the canonical per-scene truth should primarily live.

---

## 6. Preferred V1 posture: index/light handoff, not full duplicate truth

A key design choice is whether the compiled pack should:
- embed every full `scene_kit_spec`
- or act mainly as an index / handoff layer pointing to the canonical per-scene specs

The preferred V1 direction is:

> **index/light handoff first**

That means the pack should contain:
- global metadata
- global frame (or a strong embedded copy/reference of it)
- scene ordering and scene index
- references/paths to the canonical per-scene scene-kit artifacts
- short per-scene summary metadata where useful
- readiness/completion metadata

This is preferred over embedding full copies of every scene spec because it:
- reduces duplication
- reduces drift risk
- keeps the canonical truth layer explicit
- still gives S6 a clean sector-level entry surface

---

## 7. Should the pack include `video_direction_frame` inline?

The preferred V1 answer is:
- **yes, likely inline or at least strongly embedded**

Reason:
- it is a single global artifact
- duplication cost is low
- downstream convenience is high
- it reduces friction for S6 at the start of sector consumption

This is not the same as making the pack the truth source.
The canonical truth still remains the original `video_direction_frame.json` artifact.

---

## 8. Suggested V1 shape of `s5_scene_kit_pack.json`

A practical V1 shape should likely include something like:

### A. Pack identity
- `pack_version`
- `sector`
- `video_id`
- `run_id`
- `generated_at`

### B. Sector status
- `status`
- `scene_count_total`
- `scene_count_included`
- `ready_for_s6`

### C. Global frame
- `video_direction_frame`
  - embedded object or embedded-strong subset
- `video_direction_frame_ref`
  - canonical file path/reference

### D. Scene index
- `scenes[]`

Each scene entry may include:
- `scene_id`
- `sequence_position`
- `scene_summary`
- `narrative_function`
- `scene_kit_spec_ref`
- `materialization_priority` (optional, if later useful)
- `status`
  - example values: `ready`, `missing`, `invalid`
- `notes` (optional)

### E. Sector-level notes
- `warnings[]`
- `incomplete_scenes[]`
- `handoff_notes[]`

---

## 9. What the pack should not try to do in V1

The pack should **not** try to become:
- a second full truth copy of all scene specs unless strongly necessary
- a full editorial object
- a final materialization control object for S6
- a dense continuity graph
- a replacement for the per-scene artifacts

The pack should stay legible and coordination-oriented.

---

## 10. How S6 should consume the pack

The preferred V1 downstream pattern is:

### Step 1
S6 opens `s5_scene_kit_pack.json` as its sector-level handoff surface.

### Step 2
S6 reads:
- sector readiness
- global frame
- scene ordering/index
- references to canonical scene specs

### Step 3
S6 then consumes the canonical per-scene `scene_kit_spec` artifacts when materializing each scene.

This gives S6 both:
- a clean starting surface
- and a clean truth model

---

## 11. Why this aligns with earlier Block 2 lessons

This design is aligned with a proven pattern in Block 2:
- preserve granular truth locally
- provide a compiled downstream-facing surface when useful
- do not let the compiled surface silently become an independent truth source

That pattern keeps the runtime easier to debug, easier to resume, and easier to evolve.

---

## 12. Summary

The preferred V1 output posture for S5 is:
- `video_direction_frame.json` = canonical global truth
- `scene_kit_specs/<scene_id>.json` = canonical per-scene truth
- `s5_scene_kit_pack.json` = derived sector-level handoff surface for S6

The pack should remain:
- compiled
- downstream-friendly
- coordination-oriented
- derived from canonical artifacts

It should **not** become a sovereign competing truth artifact.

This is the strongest current direction for the S5 output contract heading into S6.
