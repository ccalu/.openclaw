# S4 Schema — Research Batch Manifest

_Status: planning draft_
_Last updated: 2026-04-04_
_Contract id: `s4.research_batch_manifest.v1`_

---

## 1. Purpose

This schema defines the batch-planning artifact owned by `sm_s4_asset_research`.

Its purpose is to freeze:
- the bounded discovery batches for the current run
- target ordering and batch grouping
- expected worker output planning
- the explicit v1 single-pass posture

This artifact exists to make batch planning explicit on disk instead of implicit in supervisor memory.

---

## 2. Producer and consumers

### Producer
- `sm_s4_asset_research`

### Primary consumers
- `op_s4_web_investigator`
- `sm_s4_asset_research`

### Secondary consumers
- debugging/review flows
- implementation/runtime observability

---

## 3. Required top-level shape

```json
{
  "contract_version": "s4.research_batch_manifest.v1",
  "job_id": "string",
  "parallelism_cap": 1,
  "batches": [],
  "expected_worker_outputs": [],
  "v1_second_round_policy": "disabled"
}
```

---

## 4. Field specification

## 4.1 `contract_version`
- required
- type: string
- fixed value: `s4.research_batch_manifest.v1`

## 4.2 `job_id`
- required
- type: string

## 4.3 `parallelism_cap`
- required
- type: integer
- minimum: 1

## 4.4 `batches`
- required
- type: array

### Required fields for each batch item
- `batch_id` — string
- `target_ids` — array of strings
- `priority_order` — array of strings
- `notes` — string

### Optional fields for each batch item
- `batch_label` — string
- `rationale` — string

## 4.5 `expected_worker_outputs`
- required
- type: array

### Required fields for each expected worker output item
- `target_id` — string
- `brief_path` — absolute path string
- `candidate_set_path` — absolute path string

### Optional fields for each expected worker output item
- `target_root` — absolute path string
- `assets_dir` — absolute path string
- `previews_dir` — absolute path string
- `captures_dir` — absolute path string

## 4.6 `v1_second_round_policy`
- required
- type: string
- fixed v1 value: `disabled`

---

## 5. Validation rules

1. `contract_version` must match exactly
2. `parallelism_cap` must be >= 1
3. every `batches[*].batch_id` must be non-empty
4. every `batches[*].target_ids` entry must be non-empty
5. every `batches[*].priority_order` entry should reference a target present in that batch
6. every `expected_worker_outputs[*].target_id` must be non-empty
7. every `brief_path` and `candidate_set_path` must be absolute
8. `v1_second_round_policy` must equal `disabled`

---

## 6. Interpretation guidance

## 6.1 Why this artifact exists
This artifact is not just bookkeeping.
It freezes the supervisor's bounded execution plan so that:
- investigator planning is explicit
- worker expectations are explicit
- batch grouping is inspectable
- v1 policy remains visible in runtime artifacts

## 6.2 V1 posture
S4 v1 is intentionally conservative:
- one strong pass
- no automatic second round
- bounded supervisor-controlled dispatch

This schema should reflect that posture clearly.

---

## 7. Edge cases

## 7.1 Single-batch run
Valid and likely common in v1.

In that case:
- `batches` may contain exactly one batch
- `parallelism_cap` may still be greater than 1 if the supervisor allows multiple workers inside the batch

## 7.2 Empty intake / zero targets
Possible but unusual.

In that case:
- `batches` may be empty
- `expected_worker_outputs` may be empty
- runtime should handle this explicitly rather than silently

## 7.3 Priority order equals target order
Valid case.

If there is no distinction between grouping order and execution priority:
- `priority_order` may simply mirror `target_ids`

---

## 8. Example

```json
{
  "contract_version": "s4.research_batch_manifest.v1",
  "job_id": "job_006_pt_001",
  "parallelism_cap": 3,
  "batches": [
    {
      "batch_id": "batch_001",
      "target_ids": ["rt_001", "rt_002", "rt_003"],
      "priority_order": ["rt_001", "rt_003", "rt_002"],
      "notes": "Start with hotel exterior and symbolic entrance support."
    }
  ],
  "expected_worker_outputs": [
    {
      "target_id": "rt_001",
      "brief_path": "C:\\...\\targets\\rt_001_hotel_quitandinha\\target_research_brief.json",
      "candidate_set_path": "C:\\...\\targets\\rt_001_hotel_quitandinha\\candidate_set.json"
    },
    {
      "target_id": "rt_002",
      "brief_path": "C:\\...\\targets\\rt_002_cassino_interior\\target_research_brief.json",
      "candidate_set_path": "C:\\...\\targets\\rt_002_cassino_interior\\candidate_set.json"
    }
  ],
  "v1_second_round_policy": "disabled"
}
```
