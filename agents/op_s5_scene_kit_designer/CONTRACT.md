# Contract

## Input
- `scene_direction_input_package` JSON (per-scene assembled input with scene_core, semantic_grounding, reference_layer, policy)
- `video_direction_frame` JSON (global constraints: era, style, grounding baseline, motion policy, generation modes)

## Output
- `scene_kit_spec` JSON written to `scene_kit_specs/{scene_id}.json`

## Validation
- Must pass `scene_kit_spec` JSON schema
- Must have `asset_families[]` with minItems: 1
- Each family must have: family_id, family_type (enum), family_intent (concrete text), priority, grounding_strength, creative_freedom_level, preferred_generation_modes[], reference_inputs[], preserve_requirements[]
