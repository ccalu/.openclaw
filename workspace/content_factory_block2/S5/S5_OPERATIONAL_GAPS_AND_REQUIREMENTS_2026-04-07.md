# S5 Operational Gaps and Requirements — 2026-04-07

_Status: implementation-preflight checklist_
_Last updated: 2026-04-07_
_Owner: Tobias_

---

## 1. Purpose of this document

This document records the operational requirements and document-level fixes identified during the deep S5 review performed against:
- the current S5 docs
- the proven S4 runtime pattern
- implementation lessons already learned in Block 2

It exists to ensure these requirements are not lost between conceptual design and implementation planning.

This is not the phase plan.
It is the list of operational truths that should already be reflected in the docs and then carried into implementation.

---

## 2. Runtime architecture requirement

The preferred S5 runtime shape is now:
- `sm_s5_scene_kit_design` = OpenClaw supervisor
- `input_assembly.py` = helper-direct phase
- `direction_frame_builder.py` = helper-direct phase
- `op_s5_scene_kit_designer` = OpenClaw operator
- compile + validators = helper-direct

This should be treated as the current preferred runtime baseline for implementation planning.

---

## 3. Shared operational requirements

### 3.1 Session cleanup is mandatory
The supervisor should explicitly clean S5 OpenClaw sessions before each run.
This should not be optional.

### 3.2 `llm_client.py` requires concurrency and retry discipline
The shared LLM client should include:
- `Semaphore(10)`
- retry with exponential backoff
- provider abstraction

### 3.3 Validation is required even before final schema freeze
Even before final JSON schema freeze, each gate should still perform structural validation such as:
- required fields exist
- expected types are present
- required artifacts exist where expected

### 3.4 Bootstrap parsing must be explicit
S5 needs an explicit bootstrap loading/parsing layer.
This may exist as:
- `bootstrap_loader.py`
- or equivalent integrated logic in the supervisor

### 3.5 Minimum viable family rule
A `scene_kit_spec` should not produce zero families in V1.
If reference support is weak or absent, the minimum viable behavior is still to emit at least one family.

---

## 4. Object-model requirements

### 4.1 `reference_inputs[]`
The preferred V1 shape is object-based:
- `{ asset_id, source_target_id }`

### 4.2 `scene_id`
`scene_id` must be treated as a formal field of the `scene_kit_spec`, not only as something shown in examples.

### 4.3 `spec_version`
`spec_version` should be treated as a formal top-level field of the `scene_kit_spec`.

### 4.4 `allowed_generation_modes[]`
This field should exist in `applied_global_constraints`.
The preferred V1 values are:
- `reference_guided_generation`
- `regeneration_from_reference`
- `from_scratch_generation`
- `multi_reference_synthesis`

`motion_generation` should not be listed there in V1 because motion enablement is already represented by `motion_policy` / `motion_allowed`.

### 4.5 `motion_allowed`
The relationship should be explicit:
- global frame owns `motion_policy`
- scene-level spec owns resolved `motion_allowed`

### 4.6 `scene_entities[]`
`scene_entities[]` from S3 should be treated as consumed input, not raw pass-through output.
Their downstream influence should be transformed into the scene-kit language.

### 4.7 `symbolic_anchors[]`
`symbolic_anchors[]` from S3 should be treated as one of the inputs informing `thematic_layer[]`, not as a literal pass-through output field.

---

## 5. Example coverage requirement

The docs should include at least one explicit low-reference / zero-reference example.
This is necessary because low-reference scenes are common in the actual upstream reality.

---

## 6. Summary

The purpose of this checklist is simple:
- do not let implementation start from conceptually strong docs that are still missing operational discipline
- make the S5 docs reflect the real runtime lessons already learned in S4
- preserve a cleaner path into the implementation phase plan
