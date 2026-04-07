# S4 — Runtime Control Flow

_Status: canonical (V3)_
_Last updated: 2026-04-06_
_Owner: Tobias_

---

## 1. Purpose

This document describes the **runtime control flow** for S4 — Asset Research in its current V3 architecture.

The architecture document (S4_ARCHITECTURE_V2.md) defines what S4 is and why it exists.
This document defines **how S4 actually progresses in runtime**.

---

## 2. Central runtime model

### supervisor_shell.py is the deterministic orchestrator

All S4 runtime progression is controlled by `supervisor_shell.py`, a checkpoint-resume Python orchestrator. The SM actor (`sm_s4_asset_research`) delegates entirely to it.

Key properties:
- Filesystem-first truth
- Checkpoint-driven progression (`runtime/phase_checkpoints.json`)
- Automatic resume from last completed phase if re-executed
- Session cleanup before each run (all S4 agent sessions)
- 8 sequential phases, no parallelism between phases

### Invocation model

There are two invocation patterns in V3:

| Pattern | Used by | Mechanism |
|---------|---------|-----------|
| **Helper-direct** | target_builder, web_investigator, asset_pipeline | `supervisor_shell.py` calls Python helper directly (subprocess or import) |
| **OpenClaw CLI dispatch** | coverage_analyst, pack_compiler | `supervisor_shell.py` dispatches via `openclaw agent` CLI |

Helper-direct replaced OpenClaw dispatch for phases where LLM actors produced unreliable results (mangled paths, invented logic). Only the final two analysis/compilation phases remain as OpenClaw actors.

---

## 3. Runtime actors

### 3.1 `w3_block2.py` / boundary workflow

Responsibilities:
- Observe B2 checkpoints
- Launch `sm_s4_asset_research` after detecting `s4_requested.json`
- Detect `s4_completed.json` / `s4_failed.json` for B2 resume

### 3.2 `b2_director`

Responsibilities:
- Create S4 request checkpoint and bootstrap payload
- Resume on `s4_completed` / `s4_failed`

### 3.3 `sm_s4_asset_research`

Responsibilities:
- Read bootstrap path from activation message
- Validate bootstrap fields and upstream paths
- Delegate to `supervisor_shell.py <bootstrap_path>`
- Confirm completion/failure from exit code + checkpoint files

### 3.4 `supervisor_shell.py`

The real orchestrator. Responsibilities:
- Session cleanup for all S4 agents
- Bootstrap validation + directory creation
- Execute 8 phases sequentially with checkpoint gates
- Resume from last checkpoint on re-execution
- Write `s4_completed.json` + B2 mirror on success
- Write `s4_failed.json` + B2 mirror on failure

### 3.5 Active OpenClaw actors (2)

| Actor | Phase | Role |
|-------|-------|------|
| `op_s4_coverage_analyst` | 6 | Reads materialization reports, produces coverage report |
| `op_s4_pack_compiler` | 7 | Compiles final research pack and sector report |

### 3.6 Deprecated actors (4)

| Actor | Replaced by | Reason |
|-------|------------|--------|
| `op_s4_target_builder` | `target_builder.py` helper-direct | LLM actor invented own logic instead of calling helper |
| `op_s4_web_investigator` | `web_investigator.py` helper-direct | LLM actor mangled paths |
| `op_s4_target_research_worker` | `s4_query_generator.py` + `s4_image_collector.py` | Entire retrieval approach replaced |
| `op_s4_candidate_evaluator` | `s4_visual_evaluator.py` | Textual classification replaced by vision evaluation |

---

## 4. Canonical runtime sequence

### Phase 0 — Upstream completion (precondition)

S3 has completed and persisted:
- `compiled_entities.json`
- `s3_sector_report.md`
- `s3_completed.json`

The B2 boundary has validated S3 completion.

---

### Phase 1 — Bootstrap

**Actor:** `supervisor_shell.py`

Actions:
1. Clean all S4 agent sessions (`openclaw sessions cleanup --enforce`)
2. Read and validate bootstrap artifact
3. Confirm upstream S3 artifacts exist on disk
4. Create sector directory structure
5. Write initial phase checkpoint

---

### Phase 2 — Target building (HELPER-DIRECT)

**Actor:** `target_builder.py` (called directly by supervisor_shell)

Inputs:
- `compiled_entities.json` from S3

Actions:
1. Collect entities from S3 (4 categories)
2. Deterministic: normalize strings, detect label overlaps
3. LLM (GPT-5.4-nano): consolidate overlapping entities, contextualize labels, classify searchability
4. Deterministic: validate provenance, enforce schema
5. Write `research_intake.json` and `target_builder_report.md`

Outputs:
- `intake/research_intake.json`
- `intake/target_builder_report.md`

---

### Phase 3 — Batch manifest (HELPER, deterministic)

**Actor:** `batch_manifest_builder.py` (called by supervisor_shell)

Actions:
1. Read intake
2. Build deterministic batch manifest

Outputs:
- `intake/research_batch_manifest.json`

---

### Phase 4 — Web investigation (HELPER-DIRECT)

**Actor:** `web_investigator.py` (called directly by supervisor_shell)

Actions:
1. Read intake and batch manifest
2. Generate target briefs with search goals

Outputs:
- `targets/{tid}/{tid}_brief.json` per target

---

### Phase 5 — Asset pipeline (HELPER-DIRECT, 4 sub-steps)

**Actor:** `s4_asset_pipeline.py` (called directly by supervisor_shell)

Uses GPT-5.4-nano (OpenAI API) + Serper.dev. Orchestrates 4 sub-steps:

#### Step 0 — Context extraction
- GPT-5.4-nano reads first 20 scenes of the script
- Extracts: title, subject, era, style, key_locations, visual_era_guidance
- Output: `runtime/video_context.json`

#### Step 1 — Query generation
- GPT-5.4-nano generates 2 queries per active target
- Queries anchored to video context (not generic concepts)
- Semaphore(10), 1 call per target
- Output: `{tid}_search_queries.json` per target

#### Step 2 — Image collection
- Serper.dev Google Images API (10 results per query)
- Parallel download (aiohttp, Semaphore(50))
- pHash deduplication (Hamming distance < 10)
- Output: `candidates/` directory + `{tid}_serper_results.json` per target

#### Step 3 — Visual evaluation
- GPT-5.4-nano vision evaluates images in batches of 5
- Video context coherence rules (era, style, specific vs generic)
- relevance >= 7 --> `assets/`, < 7 --> deleted
- Semaphore(10)
- Output: `{tid}_asset_materialization_report.json` + `assets/` per target + `assets/*.reference_ready.json` sidecars (for approved images)

---

### Phase 6 — Coverage analysis (OPENCLAW ACTOR)

**Actor:** `op_s4_coverage_analyst` (dispatched via OpenClaw CLI)

Inputs:
- `research_intake.json`
- `{tid}_asset_materialization_report.json` (new V3 format)
- Falls back to `evaluated_candidate_set.json` (legacy format)

Actions:
1. Compute target-level coverage
2. Compute scene-level coverage
3. Identify unresolved gaps

Outputs:
- `compiled/coverage_report.json`

---

### Phase 7 — Pack compilation (OPENCLAW ACTOR)

**Actor:** `op_s4_pack_compiler` (dispatched via OpenClaw CLI)

Inputs:
- `research_intake.json`
- Materialization reports (new format + legacy fallback)
- `coverage_report.json`

Actions:
1. Compile target-level and scene-level results
2. Build asset manifest
3. Generate human-readable sector report

Outputs:
- `compiled/research_pack.json`
- `compiled/s4_sector_report.md`
- `compiled/s4_reference_ready_asset_pool.json` (grouped views: by_target, by_reference_value, by_depiction_type, with scene_relevance per asset)

---

### Phase 8 — Completion

**Actor:** `supervisor_shell.py`

Actions:
1. Validate final pack and sector report exist
2. Write `s4_completed.json` in sector checkpoints
3. Mirror to `{b2_root}/checkpoints/s4_completed.json`

---

## 5. Runtime truth model

### 5.1 Disk is the source of truth

- Files on disk are primary truth
- Conversational summaries are secondary evidence only
- Process exit code is not completion truth
- Checkpoint presence plus artifact validation determines progression

### 5.2 Checkpoint resume

`supervisor_shell.py` persists phase completion in `runtime/phase_checkpoints.json`. On re-execution, it reads the last completed phase and resumes from the next one. This makes the pipeline idempotent across crashes.

---

## 6. State machine

| State | Checkpoint / Artifact | Writer |
|-------|----------------------|--------|
| `bootstrap` | `phase_checkpoints.json` phase=1 | `supervisor_shell.py` |
| `target_building` | `intake/research_intake.json` | `target_builder.py` |
| `batch_manifest` | `intake/research_batch_manifest.json` | `batch_manifest_builder.py` |
| `web_investigation` | `targets/{tid}/{tid}_brief.json` | `web_investigator.py` |
| `asset_pipeline` | `{tid}_asset_materialization_report.json` + `runtime/video_context.json` + `assets/*.reference_ready.json` | `s4_asset_pipeline.py` |
| `coverage_analysis` | `compiled/coverage_report.json` | `op_s4_coverage_analyst` |
| `pack_compilation` | `compiled/research_pack.json` + `s4_sector_report.md` + `s4_reference_ready_asset_pool.json` | `op_s4_pack_compiler` |
| `completed` | `checkpoints/s4_completed.json` + B2 mirror | `supervisor_shell.py` |
| `failed` | `checkpoints/s4_failed.json` + B2 mirror | `supervisor_shell.py` |

---

## 7. Failure handling

| Phase | Failure | Action |
|-------|---------|--------|
| target_builder | Sector FAILS | `s4_failed.json` |
| web_investigator | Sector FAILS | `s4_failed.json` |
| asset_pipeline (partial) | Sector CONTINUES | Gaps reflected in coverage/pack |
| coverage_analyst | Sector FAILS | `s4_failed.json` |
| pack_compiler | Sector FAILS | `s4_failed.json` |

---

## 8. Session management

Before each S4 run, `supervisor_shell.py` cleans all OpenClaw agent sessions via `openclaw sessions cleanup --enforce` for each S4 agent. This prevents context accumulation between videos.

Agents cleaned:
- `sm_s4_asset_research`
- `op_s4_coverage_analyst`
- `op_s4_pack_compiler`
- (deprecated actors also cleaned for safety)

---

## 9. Performance

Typical V3 run: ~3 minutes, ~$0.14 in OpenAI costs per video.

| Resource | Per-Video Usage |
|----------|----------------|
| GPT-5.4-nano calls | ~110 |
| Serper.dev queries | ~56 |
