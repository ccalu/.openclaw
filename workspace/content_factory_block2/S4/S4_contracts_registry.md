# S4 — Contracts Registry

_Status: canonical (V3)_
_Last updated: 2026-04-06_
_Owner: Tobias_

---

## 1. Purpose

This document is the S4-local registry of contracts governing artifact exchange between pipeline phases.

Updated for V3 architecture: helper-direct pattern for phases 2-5, OpenClaw dispatch only for phases 6-7.

---

## 2. Contract posture

S4 V3 keeps contracts conservative:
- Explicit artifact ownership
- Explicit producer/consumer mapping
- Explicit required paths
- Disk artifacts are source of truth

---

## 3. Shared enum definitions

### 3.1 Coverage state enum

Allowed values:
- `covered`
- `partially_covered`
- `inspiration_only`
- `unresolved`

### 3.2 Searchability enum

Allowed values:
- `retrievable`
- `retrievable_generic`
- `non_retrievable`

### 3.3 Target type enum

Allowed values:
- `person_historical`
- `location_historical`
- `object_artifact`
- `architectural_anchor`
- `interior_space`
- `symbolic_sequence`
- `event_reference`
- `environment_reference`

### 3.4 Priority enum

Allowed values:
- `critical`
- `high`
- `medium`
- `low`

---

## 4. Active contracts

## 4.1 `s4_requested.json`

### Purpose
Macro block checkpoint signaling that S4 has been requested.

### Producer
- `b2_director`

### Consumers
- `w3_block2.py`

### Required shape
```json
{
  "event": "s4_requested",
  "job_id": "string",
  "sector": "s4_asset_research",
  "bootstrap_path": "absolute_path",
  "requested_at": "ISO_TIMESTAMP",
  "status": "requested"
}
```

---

## 4.2 `s4.supervisor_bootstrap.v1`

### Purpose
Activate the S4 supervisor with all required runtime roots and upstream artifact paths.

### Producer
- `b2_director`

### Consumer
- `sm_s4_asset_research` -> `supervisor_shell.py`

### Required fields
- `kind = s4_start`
- `contract_version = s4.supervisor_bootstrap.v1`
- `job_id`, `video_id`, `account_id`, `language`
- `run_root`, `b2_root`, `sector_root`
- `upstream.compiled_entities_path`, `upstream.sector_report_path`
- `checkpoints_dir`, `intake_dir`, `targets_dir`, `compiled_dir`, `logs_dir`, `runtime_dir`

---

## 4.3 `s4.research_intake.v1`

### Purpose
Canonical intake artifact after target building and consolidation.

### Producer
- `target_builder.py` (helper-direct)

### Consumers
- `supervisor_shell.py` (validation gate)
- `web_investigator.py`
- `op_s4_coverage_analyst`
- `op_s4_pack_compiler`

### Required top-level fields
- `contract_version`, `sector`, `metadata`
- `source_refs`, `scene_index`, `research_targets`
- `intake_notes`, `warnings`

### Required `research_targets` item fields
- `target_id`, `canonical_label`, `target_type`
- `source_entity_ids`, `source_categories`
- `scene_ids`, `searchability`, `handling_mode`
- `research_modes`, `priority`, `research_needs`, `notes`
- `skip_reason` (when `handling_mode = skip_visual_retrieval`)

---

## 4.4 `target_builder_report.md`

### Purpose
Human-readable report describing normalization, consolidation, searchability classification, and warnings.

### Producer
- `target_builder.py` (helper-direct)

### Consumers
- Debugging / review workflows

---

## 4.5 `s4.research_batch_manifest.v1`

### Purpose
Freeze discovery batches and target ordering.

### Producer
- `batch_manifest_builder.py` (deterministic helper)

### Consumers
- `web_investigator.py`
- `supervisor_shell.py`

### Required fields
- `contract_version`, `job_id`, `batches`

---

## 4.6 `s4.target_research_brief.v1`

### Purpose
Per-target brief with search goals for the asset pipeline.

### Producer
- `web_investigator.py` (helper-direct)

### Consumers
- `s4_asset_pipeline.py`

### Required fields
- `contract_version`, `target_id`, `canonical_label`
- `target_type`, `scene_ids`, `search_goals`
- `storage_paths`

---

## 4.7 `s4.asset_materialization_report.v1` (NEW in V3)

### Purpose
Per-target report from the visual evaluation pipeline, documenting which images were approved and why.

### Producer
- `s4_visual_evaluator.py` (via `s4_asset_pipeline.py`)

### Consumers
- `op_s4_coverage_analyst` (primary input, new format)
- `op_s4_pack_compiler` (primary input, new format)

### Required fields
- `target_id`, `canonical_label`
- `approved_assets[]` — each with `filename`, `source_url`, `relevance_score`, `rationale`
- `rejected_count`, `total_evaluated`
- `evaluation_notes`

### Legacy fallback
Coverage analyst and pack compiler also accept `evaluated_candidate_set.json` (V1/V2 format) when `asset_materialization_report.json` is not present.

---

## 4.8 `s4.coverage_report.v1`

### Purpose
Target-level and scene-level coverage assessment.

### Producer
- `op_s4_coverage_analyst`

### Consumers
- `op_s4_pack_compiler`
- `supervisor_shell.py` (validation gate)
- Downstream S5/S6 readers

### Required top-level fields
- `contract_version`, `metadata`
- `target_coverage`, `scene_coverage`
- `unresolved_gaps`, `warnings`

---

## 4.9 `s4.research_pack.v1`

### Purpose
Final compiled output of S4 for downstream sectors.

### Producer
- `op_s4_pack_compiler`

### Consumers
- `supervisor_shell.py` (validation gate)
- `b2_director`
- S5 and later sectors

### Required top-level fields
- `contract_version`, `metadata`
- `target_results`, `scene_results`
- `asset_manifest`
- `unresolved_gaps`, `warnings`

---

## 4.10 `.reference_ready.json` (per-asset sidecar)

### Purpose
Per-asset sidecar written next to each approved image in `targets/{tid}/assets/`, enriching it with reference-readiness metadata for downstream S5 consumption.

### Producer
- `s4_visual_evaluator.py`

### Consumers
- `pack_compiler.py` (aggregated into compiled pool)
- S5 and later sectors (per-asset lookup)

### Required fields
- `asset_id` — string
- `source_target_id` — string
- `source_target_label` — string
- `source_target_type` — target type enum
- `filepath` — absolute path string
- `relevance` — integer (1-10)
- `quality` — integer (1-10)
- `depicts` — string (free-text description)
- `depiction_type` — string (e.g. `person`, `location`, `object`)
- `reference_value` — array of strings (e.g. `identity_anchor`, `period_anchor`)
- `preserve_if_used` — array of strings (traits to preserve in downstream generation)
- `reasoning_summary` — string

---

## 4.11 `s4.reference_ready_asset_pool.v1`

### Purpose
Compiled pool of all reference-ready assets across all targets, with grouped views for efficient downstream lookup.

### Producer
- `op_s4_pack_compiler` (via `pack_compiler.py`)

### Consumers
- S5 and later sectors
- `b2_director`

### Required top-level fields
- `contract_version` — fixed string `s4.reference_ready_asset_pool.v1`
- `metadata` — object with `generated_at` (ISO timestamp), `total_assets` (integer)
- `assets` — array of sidecar objects (same shape as `.reference_ready.json`)
- `grouped_views` — object with:
  - `by_target` — map of target_id to array of asset_ids
  - `by_reference_value` — map of reference value tag to array of asset_ids
  - `by_depiction_type` — map of depiction type to array of asset_ids

### Artifact path
- `compiled/s4_reference_ready_asset_pool.json`

---

## 4.12 `s4_sector_report.md`

### Purpose
Mandatory human-readable final sector report.

### Producer
- `op_s4_pack_compiler`

### Consumers
- `supervisor_shell.py` (required for completion)
- `b2_director`
- Humans / debugging workflows

---

## 4.13 `s4_completed.json`

### Purpose
Macro sector checkpoint indicating S4 finished successfully.

### Producer
- `supervisor_shell.py`

### Consumers
- `w3_block2.py`, `b2_director`

### Required shape
```json
{
  "event": "s4_completed",
  "job_id": "string",
  "sector": "s4_asset_research",
  "compiled_output_path": "absolute_path",
  "sector_report_path": "absolute_path",
  "completed_at": "ISO_TIMESTAMP",
  "status": "completed"
}
```

---

## 4.14 `s4_failed.json`

### Purpose
Macro sector checkpoint indicating S4 failed.

### Producer
- `supervisor_shell.py`

### Consumers
- `w3_block2.py`, `b2_director`

### Required shape
```json
{
  "event": "s4_failed",
  "job_id": "string",
  "sector": "s4_asset_research",
  "failed_at": "ISO_TIMESTAMP",
  "failure_reason": "string",
  "status": "failed"
}
```

---

## 5. Deprecated contracts (no active producer)

| Contract | Was produced by | Status |
|----------|----------------|--------|
| `s4.candidate_set.v1` | `op_s4_target_research_worker` (deprecated) | No producer in V3 |
| `s4.evaluated_candidate_set.v1` | `op_s4_candidate_evaluator` (deprecated) | Legacy fallback read only |
| `s4.target_builder_dispatch.v1` | `sm_s4_asset_research` (now helper-direct) | No producer in V3 |
| `s4.web_investigator_dispatch.v1` | `sm_s4_asset_research` (now helper-direct) | No producer in V3 |
| `s4.target_research_worker_dispatch.v1` | `sm_s4_asset_research` (deprecated) | No producer in V3 |
| `s4.evaluator_dispatch.v1` | `sm_s4_asset_research` (deprecated) | No producer in V3 |

---

## 6. Dispatch contracts (active, for OpenClaw actors only)

Only two dispatch contracts remain active:

### 6.1 `s4.coverage_analyst_dispatch.v1`

### Producer
- `supervisor_shell.py`

### Consumer
- `op_s4_coverage_analyst`

### Required fields
- `kind = s4_coverage_analyst_dispatch`
- `contract_version`, `job_id`
- `intake_path`
- `target_materialization_report_paths` (new V3 format)
- `evaluated_candidate_set_paths` (legacy fallback)
- `output.coverage_report_path`

### 6.2 `s4.pack_compiler_dispatch.v1`

### Producer
- `supervisor_shell.py`

### Consumer
- `op_s4_pack_compiler`

### Required fields
- `kind = s4_pack_compiler_dispatch`
- `contract_version`, `job_id`
- `intake_path`
- `target_materialization_report_paths` (new V3 format)
- `coverage_report_path`
- `output.research_pack_path`
- `output.sector_report_path`
