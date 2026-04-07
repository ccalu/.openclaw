# S4 Schema — Research Pack

_Status: planning draft_
_Last updated: 2026-04-04_
_Contract id: `s4.research_pack.v1`_

---

## 1. Purpose

This schema defines the final compiled output of S4, produced by `op_s4_pack_compiler`.

It is the main downstream artifact for:
- `sm_s4_asset_research` final closure validation
- `b2_director` resume validation
- S5 and later sectors

This artifact should represent the best structured summary of the entire S4 run, without replacing the target-local artifacts on disk.

A companion artifact, `compiled/s4_reference_ready_asset_pool.json` (contract `s4.reference_ready_asset_pool.v1`), is now generated alongside the research pack by the same compiler. It provides structured reference-readiness metadata (depiction type, reference value tags, preservation constraints) for all approved assets. The research pack schema itself is unchanged — downstream consumers that need reference metadata should read the pool file in addition to the research pack.

---

## 2. Producer and consumers

### Producer
- `op_s4_pack_compiler`

### Primary consumers
- `sm_s4_asset_research`
- `b2_director`
- downstream S5 / later sectors

### Secondary consumers
- humans
- debugging/review flows

---

## 3. Required top-level shape

```json
{
  "contract_version": "s4.research_pack.v1",
  "metadata": {},
  "target_results": [],
  "scene_results": [],
  "asset_manifest": [],
  "preview_manifest": [],
  "capture_manifest": [],
  "unresolved_gaps": [],
  "warnings": []
}
```

---

## 4. Field specification

## 4.1 `contract_version`
- required
- type: string
- fixed value: `s4.research_pack.v1`

## 4.2 `metadata`
- required
- type: object

### Required fields inside `metadata`
- `job_id` — string
- `video_id` — string
- `account_id` — string
- `language` — string
- `sector` — fixed string `s4_asset_research`
- `generated_at` — ISO timestamp string
- `status` — string

### Optional fields inside `metadata`
- `run_root` — absolute path string
- `sector_root` — absolute path string

## 4.3 `target_results`
- required
- type: array

### Required fields for each target result item
- `target_id` — string
- `canonical_label` — string
- `best_factual_evidence_ids` — array of strings
- `best_visual_reference_ids` — array of strings
- `best_stylistic_inspiration_ids` — array of strings
- `coverage_state` — string
- `notes` — string

### Optional fields for each target result item
- `scene_ids` — array of strings
- `unresolved_note` — string

## 4.4 `scene_results`
- required
- type: array

### Required fields for each scene result item
- `scene_id` — string
- `linked_target_ids` — array of strings
- `recommended_candidate_ids` — array of strings
- `coverage_state` — string
- `notes` — string

### Optional fields for each scene result item
- `unresolved_note` — string

## 4.5 `asset_manifest`
- required
- type: array
- contains materialized assets

### Required fields for each asset manifest item
- `candidate_id` — string
- `target_id` — string
- `local_asset_path` — absolute path string

### Optional fields
- `source_url` — string
- `notes` — string

## 4.6 `preview_manifest`
- required
- type: array
- contains preview files

### Required fields for each preview manifest item
- `candidate_id` — string
- `target_id` — string
- `preview_path` — absolute path string

## 4.7 `capture_manifest`
- required
- type: array
- contains page captures / screenshots

### Required fields for each capture manifest item
- `candidate_id` — string
- `target_id` — string
- `capture_path` — absolute path string

## 4.8 `unresolved_gaps`
- required
- type: array of strings
- may be empty

## 4.9 `warnings`
- required
- type: array of strings
- may be empty

---

## 5. Enums

## 5.1 `metadata.status`
Recommended v1 values:
- `completed`
- `degraded_completed`

## 5.2 `coverage_state`
Allowed values:
- `covered`
- `partially_covered`
- `inspiration_only`
- `unresolved`

---

## 6. Validation rules

1. `contract_version` must match exactly
2. `metadata.sector` must equal `s4_asset_research`
3. every manifest path must be absolute
4. every `target_results[*].coverage_state` must belong to the allowed enum
5. every `scene_results[*].coverage_state` must belong to the allowed enum
6. `asset_manifest`, `preview_manifest`, and `capture_manifest` must always exist even if empty
7. `unresolved_gaps` must always exist even if empty
8. `warnings` must always exist even if empty

---

## 7. Edge cases

## 7.1 No materialized assets
Valid case.

In that case:
- `asset_manifest = []`
- previews/captures may still exist
- target/scene results may still be useful to downstream sectors

## 7.2 Strong references but unresolved production usability
Possible case.

In that case:
- target may still have strong reference IDs
- but unresolved gaps should record what remains missing for downstream production decisions

## 7.3 Degraded completion
If the sector later adopts `degraded_completed` more formally:
- `metadata.status` may reflect that
- unresolved gaps should make the degraded scope explicit
- this should not be used vaguely or silently

---

## 8. Example

```json
{
  "contract_version": "s4.research_pack.v1",
  "metadata": {
    "job_id": "job_006_pt_001",
    "video_id": "video_006_pt_001",
    "account_id": "006",
    "language": "pt",
    "sector": "s4_asset_research",
    "generated_at": "2026-04-04T18:40:00Z",
    "status": "completed"
  },
  "target_results": [
    {
      "target_id": "rt_001",
      "canonical_label": "Hotel Quitandinha",
      "best_factual_evidence_ids": ["cand_001"],
      "best_visual_reference_ids": ["cand_004"],
      "best_stylistic_inspiration_ids": [],
      "coverage_state": "covered",
      "notes": "Exterior target is strongly covered."
    }
  ],
  "scene_results": [
    {
      "scene_id": "scene_001",
      "linked_target_ids": ["rt_001"],
      "recommended_candidate_ids": ["cand_001", "cand_004"],
      "coverage_state": "covered",
      "notes": "Opening scene has sufficient visual support."
    }
  ],
  "asset_manifest": [],
  "preview_manifest": [
    {
      "candidate_id": "cand_001",
      "target_id": "rt_001",
      "preview_path": "C:\\...\\targets\\rt_001_hotel_quitandinha\\previews\\preview_001.jpg"
    }
  ],
  "capture_manifest": [
    {
      "candidate_id": "cand_001",
      "target_id": "rt_001",
      "capture_path": "C:\\...\\targets\\rt_001_hotel_quitandinha\\captures\\capture_001.jpg"
    }
  ],
  "unresolved_gaps": [
    "Casino interior remains only partially covered."
  ],
  "warnings": []
}
```
