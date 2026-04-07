# S4 Schema — Coverage Report

_Status: planning draft_
_Last updated: 2026-04-04_
_Contract id: `s4.coverage_report.v1`_

---

## 1. Purpose

This schema defines the coverage artifact produced by `op_s4_coverage_analyst`.

Its job is not to judge individual candidates in detail.
Its job is to answer the structural question:

- how well is each target covered?
- how well is each scene covered?
- what remains unresolved?

This artifact is the sector-level sufficiency map for S4.

---

## 2. Producer and consumers

### Producer
- `op_s4_coverage_analyst`

### Primary consumers
- `sm_s4_asset_research`
- `op_s4_pack_compiler`

### Secondary consumers
- S5 / downstream sectors
- humans
- debugging/review flows

---

## 3. Required top-level shape

```json
{
  "contract_version": "s4.coverage_report.v1",
  "metadata": {},
  "target_coverage": [],
  "scene_coverage": [],
  "unresolved_gaps": [],
  "warnings": []
}
```

---

## 4. Field specification

## 4.1 `contract_version`
- required
- type: string
- fixed value: `s4.coverage_report.v1`

## 4.2 `metadata`
- required
- type: object

### Required fields inside `metadata`
- `job_id` — string
- `video_id` — string
- `sector` — fixed string `s4_asset_research`
- `generated_at` — ISO timestamp string

### Optional fields inside `metadata`
- `account_id` — string
- `language` — string

## 4.3 `target_coverage`
- required
- type: array

### Required fields for each target coverage item
- `target_id` — string
- `coverage_state` — string
- `supporting_candidate_ids` — array of strings
- `notes` — string

### Optional fields for each target coverage item
- `canonical_label` — string
- `coverage_rationale` — string
- `risk_note` — string

## 4.4 `scene_coverage`
- required
- type: array

### Required fields for each scene coverage item
- `scene_id` — string
- `coverage_state` — string
- `linked_target_ids` — array of strings
- `notes` — string

### Optional fields for each scene coverage item
- `recommended_candidate_ids` — array of strings
- `risk_note` — string

## 4.5 `unresolved_gaps`
- required
- type: array of strings
- may be empty

## 4.6 `warnings`
- required
- type: array of strings
- may be empty

---

## 5. Enums

## 5.1 `coverage_state`
Allowed values:
- `covered`
- `partially_covered`
- `inspiration_only`
- `unresolved`

---

## 6. Validation rules

1. `contract_version` must match exactly
2. `metadata.sector` must equal `s4_asset_research`
3. every `target_coverage[*].target_id` must be non-empty
4. every `scene_coverage[*].scene_id` must be non-empty
5. every `coverage_state` must belong to the allowed enum
6. `supporting_candidate_ids` may be empty for weak/unresolved cases
7. `warnings` must always exist

---

## 7. Interpretation guidance

## 7.1 `covered`
Use when the target/scene has sufficiently strong evaluated support for downstream use.

## 7.2 `partially_covered`
Use when there is some usable support but important dimensions are still missing.

## 7.3 `inspiration_only`
Use when the available support is mostly stylistic / indirect / suggestive rather than grounded enough for stronger downstream confidence.

## 7.4 `unresolved`
Use when the target/scene remains materially under-supported.

---

## 8. Edge cases

## 8.1 No targets in intake
If S4 intake had zero targets:
- `target_coverage` may be empty
- `scene_coverage` may be empty
- `warnings` must explain the no-target condition

## 8.2 Target with evaluated candidates but none accepted as useful
Valid case.

In that case:
- `supporting_candidate_ids` may be empty
- `coverage_state` should likely be `unresolved` or `inspiration_only`
- note should explain why

## 8.3 Scene with mixed coverage quality
A scene may link to multiple targets with different states.
The scene-level `coverage_state` should reflect the aggregate practical readiness of that scene, not a simple average.

---

## 9. Example

```json
{
  "contract_version": "s4.coverage_report.v1",
  "metadata": {
    "job_id": "job_006_pt_001",
    "video_id": "video_006_pt_001",
    "sector": "s4_asset_research",
    "generated_at": "2026-04-04T18:30:00Z"
  },
  "target_coverage": [
    {
      "target_id": "rt_001",
      "coverage_state": "covered",
      "supporting_candidate_ids": ["cand_001", "cand_004"],
      "notes": "Strong factual and visual support found for the hotel exterior."
    },
    {
      "target_id": "rt_005",
      "coverage_state": "partially_covered",
      "supporting_candidate_ids": ["cand_031"],
      "notes": "Some contextual visual support exists, but interior gambling-floor evidence is still thin."
    }
  ],
  "scene_coverage": [
    {
      "scene_id": "scene_001",
      "coverage_state": "covered",
      "linked_target_ids": ["rt_001"],
      "notes": "Opening setup is well supported by the current target findings."
    }
  ],
  "unresolved_gaps": [
    "Casino interior remains only partially covered."
  ],
  "warnings": []
}
```
