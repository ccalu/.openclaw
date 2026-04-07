# S4 Operational Runbook

---

## How to Run S4

### Option 1: Via W3 (S3 + S4 together)
```bash
python pipeline/workflows/w3_block2.py --account 006 --lang pt --video-dir <video_dir> --mode s3_s4
```
This runs S3 first, then automatically builds the S4 bootstrap and launches S4 via the SM actor.

### Option 2: S4 standalone (S3 already completed)
```bash
cd "C:\Users\User-OEM\Desktop\OpenClaw Workspace\content_factory_block2\S4\helpers"
python supervisor_shell.py <bootstrap_path>
```
The bootstrap JSON must exist at `<sector_root>/s4_supervisor_bootstrap.json`.

### Option 3: Asset pipeline only (target_builder + web_investigator already done)
```bash
cd "C:\Users\User-OEM\Desktop\OpenClaw Workspace\content_factory_block2\S4\helpers"
python s4_asset_pipeline.py <intake_path> <sector_root> <job_id>
```

---

## Prerequisites

### Python packages
```bash
pip install openai aiohttp requests imagehash Pillow httpx
```

### OpenClaw
- OpenClaw CLI installed and configured (`openclaw.cmd` on Windows)
- Agents materialized: `sm_s4_asset_research`, `op_s4_coverage_analyst`, `op_s4_pack_compiler`

### API Keys
| Key | Location | How to change |
|-----|----------|---------------|
| OpenAI (GPT-5.4-nano) | `s4_asset_pipeline.py:OPENAI_API_KEY` and `target_builder.py:OPENAI_API_KEY` | Edit the constant in both files |
| Serper.dev | `s4_image_collector.py:SERPER_API_KEY` | Edit the constant |

**Note:** Keys are currently hardcoded. This is a tactical shortcut. Future: migrate to env vars.

---

## Configuration

### Concurrency
| Parameter | File | Default | Meaning |
|-----------|------|---------|---------|
| `QUERY_SEMAPHORE_LIMIT` | s4_query_generator.py | 10 | Max parallel query generation calls |
| `EVAL_SEMAPHORE_LIMIT` | s4_visual_evaluator.py | 10 | Max parallel evaluation targets |
| `TARGET_SEMAPHORE_LIMIT` | s4_image_collector.py | 4 | Max parallel image collection targets |
| `DOWNLOAD_SEMAPHORE_LIMIT` | s4_image_collector.py | 50 | Max parallel image downloads |
| `BATCH_SIZE` | s4_visual_evaluator.py | 5 | Images per GPT vision call |

### Thresholds
| Parameter | File | Default | Meaning |
|-----------|------|---------|---------|
| `RELEVANCE_THRESHOLD` | s4_visual_evaluator.py | 7 | Minimum score for approval |
| `RESULTS_PER_QUERY` | s4_image_collector.py | 10 | Serper results per query |
| `MIN_IMAGE_SIZE` | s4_image_collector.py | 5000 | Min image bytes (skip tiny icons) |
| `MAX_IMAGE_SIZE` | s4_image_collector.py | 15000000 | Max image bytes (skip huge files) |

### Query count
Queries per target are controlled by:
- The system prompt (`prompts/s4_query_generator_system.txt`): "generate exactly 2"
- The validation in `s4_query_generator.py`: `valid = valid[:2]`

---

## Costs Per Video

| Component | Calls | Tokens | Cost |
|-----------|-------|--------|------|
| Context extraction | 1 | ~2K in, ~500 out | ~$0.001 |
| Target consolidation | 1 | ~3K in, ~3K out | ~$0.005 |
| Query generation | ~25 | ~1K in × 25 | ~$0.008 |
| Visual evaluation | ~75 | ~5K in × 75 (images) | ~$0.125 |
| **Total GPT-5.4-nano** | **~102** | **~465K in, ~37K out** | **~$0.14** |
| Serper.dev | ~56 queries | — | Free (2500/month) |

At 1 video/day: ~$4.20/month for GPT-5.4-nano, well within 10M free tokens/day.

---

## Monitoring

### During run
Watch supervisor_shell output for phase completion:
```
[supervisor] phase: target_builder DONE (22.8s)
[supervisor] phase: asset_pipeline DONE (144.8s)
```

### After run
Check these files:
- `runtime/openai_usage.json` — token counts and cost
- `runtime/video_context.json` — extracted video context
- `runtime/phase_checkpoints.json` — duration per phase
- `compiled/s4_sector_report.md` — human-readable summary
- `compiled/s4_reference_ready_asset_pool.json` — grouped reference-ready assets (by_target, by_reference_value, by_depiction_type)
- `targets/{tid}/assets/*.reference_ready.json` — per-asset reference readiness sidecars
- `intake/target_builder_report.md` — consolidation details

### Verify quality
Open a few `targets/{tid}/assets/` directories and visually inspect the approved images.
Confirm each approved asset has a `.reference_ready.json` sidecar with `depicts`, `depiction_type`, `reference_value[]`, `preserve_if_used[]`, and `reasoning_summary`.
Check `compiled/s4_reference_ready_asset_pool.json` exists and contains grouped views (`by_target`, `by_reference_value`, `by_depiction_type`).

---

## Troubleshooting

See `S4_TROUBLESHOOTING.md` for detailed failure modes and resolutions.

### Quick checks
| Issue | Check |
|-------|-------|
| No assets at all | Is OPENAI_API_KEY valid? Check openai_usage.json |
| Wrong images (generic) | Check video_context.json — is era/subject correct? |
| Pipeline hangs | Check supervisor_shell output for 429 errors |
| Schema validation fails | Check which phase failed — schema may not accept new fields |
| "s4_completed not found" | Check checkpoints/ directory, check for s4_failed.json |

---

## Clean Run

To start completely fresh for a video:
```bash
SR="<sector_root>"
rm -rf "$SR/targets/"* "$SR/intake/"* "$SR/compiled/"* "$SR/runtime/"* "$SR/checkpoints/"* "$SR/dispatch/"* "$SR/logs/"*
rm -f "$SR/s4_completed.json" "$SR/s4_failed.json"
```

---

## Resume After Interruption

The supervisor_shell supports checkpoint-resume. Simply re-run the same command — completed phases will be skipped automatically.

Phases are tracked in `runtime/phase_checkpoints.json`. To force re-run of a specific phase, remove it from the checkpoints file.
