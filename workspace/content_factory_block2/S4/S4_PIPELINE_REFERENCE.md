# S4 Pipeline Reference

Quick reference for every active Python file in the S4 pipeline.

---

## Runtime Core

### supervisor_shell.py
**Role:** Deterministic checkpoint-resume orchestrator  
**Entry:** `python supervisor_shell.py <bootstrap_path>`  
**Input:** `s4_supervisor_bootstrap.json`  
**Output:** Phase checkpoints, s4_completed.json  
**Calls:** target_builder, batch_manifest_builder, web_investigator, s4_asset_pipeline (as subprocess); coverage_analyst, pack_compiler (via OpenClaw CLI)  
**Dependencies:** All support substrate files  

### target_builder.py
**Role:** S3 entity → S4 target consolidation (dedup + contextualize + searchability)  
**Entry:** `python target_builder.py <compiled_entities_path> <sector_root> <job_id> <video_id> <account_id> <language>`  
**Input:** S3 `compiled_entities.json`  
**Output:** `intake/research_intake.json`, `intake/target_builder_report.md`  
**LLM:** GPT-5.4-nano (1 call for consolidation)  
**Dependencies:** openai, artifact_io, paths, schema_validator  

### web_investigator.py
**Role:** Generate target briefs with search goals  
**Entry:** `python web_investigator.py <intake_path> <manifest_path> <sector_root>`  
**Input:** research_intake.json, research_batch_manifest.json  
**Output:** `{tid}_brief.json` per target  
**Dependencies:** artifact_io, paths  

### s4_asset_pipeline.py
**Role:** Unified visual retrieval orchestrator  
**Entry:** `python s4_asset_pipeline.py <intake_path> <sector_root> <job_id>`  
**Input:** research_intake.json, target briefs, S3 source_package (for context)  
**Output:** video_context.json, openai_usage.json, and per-target: search_queries, serper_results, materialization_report, assets/  
**Sub-steps:** context extraction → query gen → image collection → visual eval  
**LLM:** GPT-5.4-nano (context: 1 call, queries: 1/target, eval: ~3 batches/target)  
**Dependencies:** openai, s4_query_generator, s4_image_collector, s4_visual_evaluator, artifact_io  

### s4_query_generator.py
**Role:** Generate 2 Google Images queries per target, anchored to video context  
**Input:** research_intake.json, target briefs, video_context  
**Output:** `{tid}_search_queries.json` per target  
**LLM:** GPT-5.4-nano, Semaphore(10)  
**Prompt:** `prompts/s4_query_generator_system.txt`  

### s4_image_collector.py
**Role:** Serper.dev search + parallel download + pHash dedup  
**Input:** `{tid}_search_queries.json` per target  
**Output:** `candidates/` directory + `{tid}_serper_results.json` per target  
**APIs:** Serper.dev (10 results/query)  
**Concurrency:** Semaphore(4) for targets, Semaphore(50) for downloads  
**Dependencies:** requests, aiohttp, shared/image_deduplicator  

### s4_visual_evaluator.py
**Role:** GPT-5.4-nano vision evaluation in batches of 5  
**Input:** `candidates/` images + target brief + video_context  
**Output:** `{tid}_asset_materialization_report.json`, `assets/` (approved images), `.reference_ready.json` sidecar per approved asset  
**LLM:** GPT-5.4-nano with base64 images, Semaphore(10)  
**Prompt:** `prompts/s4_visual_evaluator_batch_system.txt`  
**Threshold:** relevance >= 7 → approved  
**Reference readiness:** For approved images, the prompt also extracts `depicts`, `depiction_type`, `reference_value[]`, `preserve_if_used[]`, and `reasoning_summary`. These are written as `.reference_ready.json` sidecars next to each approved asset in `targets/{tid}/assets/`.  

### coverage_analyst.py
**Role:** Assess target/scene coverage from materialization reports  
**Entry:** `python coverage_analyst.py <intake_path> <sector_root>`  
**Input:** research_intake.json + asset_materialization_report.json per target  
**Output:** `compiled/coverage_report.json`  
**Format:** Reads new format first, falls back to legacy evaluated_candidate_set.json  

### pack_compiler.py
**Role:** Compile final research pack and sector report  
**Entry:** `python pack_compiler.py <intake_path> <sector_root> <job_id> <video_id> <account_id> <language>`  
**Input:** research_intake.json + coverage_report.json + materialization reports + `.reference_ready.json` sidecars  
**Output:** `compiled/research_pack.json`, `compiled/s4_reference_ready_asset_pool.json`, `compiled/s4_sector_report.md`  
**Format:** Reads new format first, falls back to legacy  
**Reference ready pool:** Aggregates all `.reference_ready.json` sidecars into `s4_reference_ready_asset_pool.json` with grouped views (`by_target`, `by_reference_value`, `by_depiction_type`) and `scene_relevance` per asset.  

---

## Support Substrate

| File | Role |
|------|------|
| `artifact_io.py` | `write_json`, `read_json`, `write_markdown`, `utc_now` |
| `batch_manifest_builder.py` | Creates research_batch_manifest from intake |
| `bootstrap_loader.py` | Loads and validates supervisor bootstrap JSON |
| `checkpoint_writer.py` | Phase checkpoints, sector status, completion/failure |
| `dirs.py` | `create_s4_directories`, `create_target_directories` |
| `paths.py` | Path derivation: intake, brief, queries, serper, report, etc. |
| `schema_validator.py` | `validate_artifact`, `validate_artifact_strict` |
| `shared/image_deduplicator.py` | pHash near-duplicate detection (imagehash) |

---

## Prompts

| File | Used by | Purpose |
|------|---------|---------|
| `s4_query_generator_system.txt` | s4_query_generator | Google Images query generation instructions |
| `s4_visual_evaluator_batch_system.txt` | s4_visual_evaluator | Batch image evaluation scoring rules |
