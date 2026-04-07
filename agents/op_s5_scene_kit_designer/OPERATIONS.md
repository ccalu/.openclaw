# Operations

## Family Design Rules

### family_type options
`hero`, `support`, `detail`, `atmospheric`, `transition`, `fallback`

### family_intent
Must be a concrete mission statement, NOT a vague label.
- Good: "Identify Joaquim Rolla as the central historical figure with 1940s period attire"
- Bad: "Show the person"

### reference_inputs
When S4 reference assets exist for the scene, link them:
```json
{"asset_id": "c001", "source_target_id": "t002"}
```

### preserve_requirements
Must be specific to the reference:
- Good: ["facial identity if confirmed", "1940s period attire", "hotel facade with enxaimel architecture"]
- Bad: ["preserve the reference"]

### Motion Policy
- `motion_allowed` is injected deterministically (first 10 scenes only)
- Only include `motion_generation` in preferred_generation_modes if motion_allowed is true

### Zero-Reference Scenes
- Emit atmospheric or from_scratch families
- Ground in the video's era/style/world, not generic stock imagery
- Minimum 1 family per scene (hard rule)

### dominant_scene_mode options
`factual`, `grounded_cinematic`, `evocative`, `symbolic`, `hybrid`
