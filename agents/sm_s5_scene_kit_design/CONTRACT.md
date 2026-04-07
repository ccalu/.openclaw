# Contract

## Bootstrap
- Contract: `s5.supervisor_bootstrap.v1`
- Kind: `s5_start`
- Required upstream paths: source_package, compiled_entities, research_intake, reference_ready_asset_pool, video_context

## Outputs
- `compiled/video_direction_frame.json` — global direction frame
- `scene_kit_specs/*.json` — per-scene canonical kit specs
- `compiled/s5_scene_kit_pack.json` — compiled handoff for S6
- `compiled/s5_sector_report.md` — human-readable summary

## Completion
- Success: writes `checkpoints/s5_completed.json` + mirrors to `b2/checkpoints/s5_completed.json`
- Failure: writes `checkpoints/s5_failed.json` + mirrors to `b2/checkpoints/s5_failed.json`

## Completion Payload
```json
{
  "event": "s5_completed",
  "sector": "s5_scene_kit_design",
  "outputs": {
    "video_direction_frame_path": "...",
    "scene_kit_specs_dir": "...",
    "scene_kit_pack_path": "...",
    "sector_report_path": "..."
  },
  "counts": {
    "scene_count_total": N,
    "scene_kit_specs_generated": N,
    "scene_kit_specs_valid": N
  },
  "readiness": {
    "ready_for_s6": true
  }
}
```
