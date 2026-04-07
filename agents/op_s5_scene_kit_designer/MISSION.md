# Mission

Given a scene_direction_input_package and the video_direction_frame, produce a complete `scene_kit_spec` for the scene.

The spec must:
- Define asset families with concrete `family_type` + `family_intent`
- Preserve factual grounding where reference assets exist
- Allow controlled creative freedom where appropriate
- ALWAYS produce at least 1 asset family per scene (even for zero-reference scenes)
- NOT collapse scenes into single-image verdicts — design the asset space, not the final edit
