# Context

S5 sits between S4 (asset research / reference discovery) and S6 (materialization).

S5 designs **scene kits** — structured asset spaces per scene that give downstream S6 and S7 real creative freedom. A scene kit is NOT a single image assignment. It defines the space of editorial possibility.

## Upstream
- S3: compiled entities (people, places, objects, events)
- S4: reference-ready asset pool (grounded visual references with semantic metadata)

## Downstream
- S6: materializes the scene kits (generates actual images/assets)
- S7: editorial resolution (assembles final video from materialized kits)

## Key Artifacts Produced
- `video_direction_frame.json` — global visual posture for the video
- `scene_kit_specs/<scene_id>.json` — per-scene kit specifications
- `s5_scene_kit_pack.json` — compiled downstream handoff
