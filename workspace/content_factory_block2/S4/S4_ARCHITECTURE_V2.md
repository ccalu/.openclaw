# S4 Asset Research — Architecture V2

**Status:** Canonical  
**Last updated:** 06 Apr 2026  
**Supersedes:** S4_asset_research_architecture.md (V1, Brave/text-first era)

---

## Overview

S4 is the Block 2 sector responsible for finding visual reference images for documentary video production. It receives visual targets from S3 (Visual Planning) and produces researched asset packs containing approved photographs for each target.

## Pipeline

```
S3 compiled_entities.json
  |
  v
supervisor_shell.py (deterministic checkpoint-resume orchestrator)
  |
  |-- Phase 1: bootstrap
  |-- Phase 2: target_builder (HELPER-DIRECT)
  |     - Collects entities from S3 (4 categories)
  |     - Deterministic: normalize, detect overlaps
  |     - LLM (GPT-5.4-nano): consolidate, contextualize labels, classify searchability
  |     - Deterministic: validate provenance, enforce schema
  |     - Output: research_intake.json (fewer targets, better labels, skipped non-retrievables)
  |
  |-- Phase 3: batch_manifest (HELPER, deterministic)
  |     - Output: research_batch_manifest.json
  |
  |-- Phase 4: web_investigator (HELPER-DIRECT)
  |     - Generates target briefs with search goals
  |     - Output: {tid}_brief.json per target
  |
  |-- Phase 5: asset_pipeline (HELPER-DIRECT, 4 sub-steps)
  |     |
  |     |-- Step 0: Context Extraction
  |     |     - GPT-5.4-nano reads first 20 scenes of the script
  |     |     - Extracts: title, subject, era, style, key_locations, visual_era_guidance
  |     |     - Output: runtime/video_context.json
  |     |
  |     |-- Step 1: Query Generation
  |     |     - GPT-5.4-nano generates 2 queries per active target
  |     |     - Queries anchored to video context (not generic concepts)
  |     |     - Semaphore(10), 1 call per target
  |     |     - Output: {tid}_search_queries.json per target
  |     |
  |     |-- Step 2: Image Collection
  |     |     - Serper.dev Google Images API (10 results per query)
  |     |     - Parallel download (aiohttp, Semaphore(50))
  |     |     - pHash deduplication (Hamming distance < 10)
  |     |     - Output: candidates/ directory + {tid}_serper_results.json per target
  |     |
  |     |-- Step 3: Visual Evaluation
  |           - GPT-5.4-nano vision evaluates images in batches of 5
  |           - Video context coherence rules (era, style, specific vs generic)
  |           - relevance >= 7 --> assets/, < 7 --> deleted
  |           - Approved images also get reference readiness metadata (depicts, depiction_type, reference_value[], preserve_if_used[], reasoning_summary)
  |           - Semaphore(10)
  |           - Output: {tid}_asset_materialization_report.json + assets/ + .reference_ready.json sidecars per target
  |
  |-- Phase 6: coverage_analyst (OPENCLAW ACTOR)
  |     - Reads asset_materialization_report.json (new format)
  |     - Falls back to evaluated_candidate_set.json (legacy)
  |     - Output: compiled/coverage_report.json
  |
  |-- Phase 7: pack_compiler (OPENCLAW ACTOR)
  |     - Reads new format + legacy fallback
  |     - Compiles reference_ready asset pool (by_target, by_reference_value, by_depiction_type views + scene_relevance)
  |     - Output: compiled/research_pack.json + s4_reference_ready_asset_pool.json + s4_sector_report.md
  |
  |-- Phase 8: completion
        - Writes s4_completed.json + mirrors to B2 checkpoints
```

## Actor Map

### Active OpenClaw Actors (2)

| Actor | Role | Invocation |
|-------|------|-----------|
| `op_s4_coverage_analyst` | Assess target/scene coverage from materialization reports | OpenClaw CLI dispatch |
| `op_s4_pack_compiler` | Compile final research pack and sector report | OpenClaw CLI dispatch |

### Active Helpers (9 runtime core + 9 support substrate)

**Runtime core** (defines sector behaviour):

| File | Role |
|------|------|
| `supervisor_shell.py` | Deterministic orchestrator, checkpoint-resume, session cleanup |
| `target_builder.py` | S3 entity consolidation (dedup + contextualize + searchability via LLM) |
| `web_investigator.py` | Generates target briefs with search goals |
| `s4_asset_pipeline.py` | Unified visual retrieval orchestrator with usage tracking |
| `s4_query_generator.py` | GPT-5.4-nano query generation with video context anchoring |
| `s4_image_collector.py` | Serper API + parallel download + pHash dedup |
| `s4_visual_evaluator.py` | GPT-5.4-nano vision evaluation with coherence rules |
| `coverage_analyst.py` | Coverage assessment helper (called by OpenClaw actor) |
| `pack_compiler.py` | Pack compilation helper (called by OpenClaw actor) |

**Support substrate** (infrastructure):

| File | Role |
|------|------|
| `artifact_io.py` | JSON/markdown I/O with UTF-8 and parent dir creation |
| `batch_manifest_builder.py` | Deterministic manifest from intake |
| `bootstrap_loader.py` | Loads supervisor bootstrap JSON |
| `checkpoint_writer.py` | Phase checkpoints, sector status, completion/failure markers |
| `dirs.py` | Directory creation (sector-level + per-target) |
| `paths.py` | Path derivation functions for all artifacts |
| `schema_validator.py` | JSON Schema validation |
| `shared/image_deduplicator.py` | pHash near-duplicate detection via imagehash |
| `shared/__init__.py` | Package init |

### Deprecated Actors (4)

| Actor | Replaced by | Reason |
|-------|------------|--------|
| `op_s4_target_builder` | `target_builder.py` helper-direct | LLM actor invented own logic instead of calling helper |
| `op_s4_web_investigator` | `web_investigator.py` helper-direct | LLM actor mangled paths |
| `op_s4_target_research_worker` | `s4_query_generator.py` + `s4_image_collector.py` | Entire retrieval approach replaced |
| `op_s4_candidate_evaluator` | `s4_visual_evaluator.py` | Textual classification replaced by vision evaluation |

### SM Actor

`sm_s4_asset_research` delegates entirely to `supervisor_shell.py`. The SM's only job is to receive the dispatch message, extract the bootstrap path, and call `python supervisor_shell.py <bootstrap_path>`.

## Canonical Artifacts

### Per-Target

```
targets/{tid}/
  {tid}_brief.json                           <-- web_investigator
  {tid}_search_queries.json                  <-- s4_query_generator
  {tid}_serper_results.json                  <-- s4_image_collector
  {tid}_asset_materialization_report.json    <-- s4_visual_evaluator
  assets/                                   <-- approved images (relevance >= 7)
    {filename}.reference_ready.json         <-- s4_visual_evaluator (sidecar per approved asset)
```

### Sector-Level

```
intake/
  research_intake.json                       <-- target_builder (with consolidation)
  research_batch_manifest.json               <-- batch_manifest_builder
  target_builder_report.md                   <-- target_builder

compiled/
  coverage_report.json                       <-- coverage_analyst
  research_pack.json                         <-- pack_compiler
  s4_reference_ready_asset_pool.json         <-- pack_compiler (grouped by target, reference_value, depiction_type)
  s4_sector_report.md                        <-- pack_compiler

runtime/
  video_context.json                         <-- asset_pipeline step 0
  openai_usage.json                          <-- asset_pipeline usage tracking
  phase_checkpoints.json                     <-- supervisor_shell
  sector_status.json                         <-- checkpoint_writer

checkpoints/
  s4_completed.json                          <-- supervisor_shell (completion)
```

## Runtime Dependencies and Credentials

| Dependency | Used By | Auth | Key Location |
|------------|---------|------|-------------|
| OpenAI API (GPT-5.4-nano) | target_builder, s4_query_generator, s4_visual_evaluator, context extraction | API key | Hardcoded in `s4_asset_pipeline.py` and `target_builder.py` |
| Serper.dev (Google Images) | s4_image_collector | API key | Hardcoded in `s4_image_collector.py` |
| OpenClaw CLI | coverage_analyst, pack_compiler, SM, session cleanup | Machine config | System-level `.openclaw/` |

**IMPORTANT:** Hardcoded API keys are a **tactical development shortcut**, not an approved architectural pattern. This must NOT be replicated in future sectors. Migration path: env vars or KMS integration.

### Rate Limits and Costs

| Resource | Limit | Cost | Per-Video Usage |
|----------|-------|------|----------------|
| GPT-5.4-nano | 5,000 RPM, 50K images/min, 10M tokens/day free | $0.20/M in, $1.25/M out | ~110 calls, ~$0.14 |
| Serper.dev | 2,500 free queries | Free tier | ~56 queries |

## Target Consolidation

The target_builder performs **entity-to-target consolidation** at the S3-S4 boundary:

1. **Deterministic pre-pass:** collect all entities, normalize strings, detect exact label overlaps
2. **LLM consolidation (GPT-5.4-nano):** merge overlapping entities, contextualize labels for unambiguous search, classify searchability (retrievable / retrievable_generic / non_retrievable)
3. **Deterministic validation:** ensure all entity_ids preserved, no orphans, schema-valid output

### Searchability Classification

| Class | Meaning | Handling |
|-------|---------|---------|
| `retrievable` | Concrete visual subject, specific to the video | Full visual retrieval pipeline |
| `retrievable_generic` | Generic concept, similar images work | Full pipeline but expectations adjusted |
| `non_retrievable` | Abstract concept, no visual search equivalent | `handling_mode: skip_visual_retrieval`, preserved in intake with trace |

### Provenance

Every consolidated target carries:
- `source_entity_ids[]` — which S3 entities were merged
- `source_categories[]` — which S3 operator categories produced them
- `searchability` — LLM classification
- `handling_mode` — visual_retrieval or skip_visual_retrieval
- `skip_reason` — why non-retrievable targets were skipped

## Video Context Injection

Before query generation and visual evaluation, the pipeline extracts context from the video script:

```json
{
  "title": "O Quitandinha ia ser o maior casino do mundo...",
  "subject": "Hotel Quitandinha, Petropolis",
  "era": "1940-1950, Era Vargas",
  "style": "documentary, nostalgic, investigative",
  "key_locations": ["Petropolis", "Serra de Petropolis"],
  "visual_era_guidance": "Accept 1940s photography, reject modern architecture..."
}
```

This context is injected into:
- **Query generator:** "Every query MUST be anchored to this video's subject"
- **Visual evaluator:** coherence rules (reject wrong era, toys, generic modern content)

## Session Management

Before each S4 run, `supervisor_shell.py` cleans all OpenClaw agent sessions via `openclaw sessions cleanup --enforce` for each S4 agent. This prevents context accumulation between videos.

## Schemas

| Schema | Contract Version | Status |
|--------|-----------------|--------|
| `research_intake.schema.json` | `s4.research_intake.v1` | Active |
| `supervisor_bootstrap.schema.json` | `s4.supervisor_bootstrap.v1` | Active |
| `research_batch_manifest.schema.json` | `s4.research_batch_manifest.v1` | Active |
| `target_research_brief.schema.json` | `s4.target_research_brief.v1` | Active |
| `coverage_report.schema.json` | `s4.coverage_report.v1` | Active |
| `research_pack.schema.json` | `s4.research_pack.v1` | Active |
| `asset_materialization_report.schema.json` | `s4.asset_materialization_report.v1` | Active |
| `candidate_set.schema.json` | `s4.candidate_set.v1` | Deprecated (no producer) |
| `evaluated_candidate_set.schema.json` | `s4.evaluated_candidate_set.v1` | Deprecated (no producer) |

## Architectural History

| Era | Period | Stack | Outcome |
|-----|--------|-------|---------|
| V1 (Brave/text) | 04 Apr 2026 | Brave Search + textual classification + Firecrawl | Terrible image quality |
| V2 (Gemini/KMS) | 06 Apr AM | Serper + Gemini Vision via KMS cascade | 429 storms, never completed |
| V3 (GPT-5.4-nano) | 06 Apr PM | Serper + GPT-5.4-nano + target consolidation | 3 min, $0.14/video, production-ready |
