# S4 Schema — Research Intake

_Status: planning draft_
_Last updated: 2026-04-04_
_Contract id: `s4.research_intake.v1`_

---

## 1. Purpose

This schema defines the canonical intake artifact produced by `op_s4_target_builder` and consumed by the rest of S4.

It is the first major boundary artifact inside S4.

It transforms:
- S3 compiled entities

into:
- research-ready targets for discovery/evaluation/coverage/compilation

---

## 2. Producer and consumers

### Producer
- `op_s4_target_builder`

### Primary consumers
- `sm_s4_asset_research`
- `op_s4_web_investigator`
- `op_s4_coverage_analyst`
- `op_s4_pack_compiler`

### Secondary consumers
- debugging/review tools
- humans

---

## 3. Required top-level shape

```json
{
  "contract_version": "s4.research_intake.v1",
  "sector": "s4_asset_research",
  "metadata": {},
  "source_refs": {},
  "scene_index": [],
  "research_targets": [],
  "intake_notes": [],
  "warnings": []
}
```

---

## 4. Field specification

## 4.1 `contract_version`
- required
- type: string
- fixed value: `s4.research_intake.v1`

## 4.2 `sector`
- required
- type: string
- fixed value: `s4_asset_research`

## 4.3 `metadata`
- required
- type: object

### Required fields inside `metadata`
- `job_id` — string
- `video_id` — string
- `account_id` — string
- `language` — string
- `generated_at` — ISO timestamp string
- `generated_from` — string (usually upstream artifact path or artifact name)

### Optional fields inside `metadata`
- `run_root` — absolute path string
- `sector_root` — absolute path string
- `upstream_sector` — string, expected `s3_visual_planning`
- `builder_run_id` — string

## 4.4 `source_refs`
- required
- type: object

### Required fields inside `source_refs`
- `compiled_entities_path` — absolute path string

### Optional fields inside `source_refs`
- `s3_sector_report_path` — absolute path string
- `bootstrap_path` — absolute path string

## 4.5 `scene_index`
- required
- type: array
- may be empty only if `research_targets` is also empty and the run is explicitly classified as no-target / no-scene case

### Required fields for each scene item
- `scene_id` — string
- `linked_target_ids` — array of strings
- `notes` — string

### Optional fields for each scene item
- `scene_title` — string
- `scene_summary` — string
- `priority_hint` — string

## 4.6 `research_targets`
- required
- type: array
- in normal operation should contain at least one item

### Required fields for each target item
- `target_id` — string
- `canonical_label` — string
- `target_type` — string
- `source_entity_ids` — array of strings
- `scene_ids` — array of strings
- `research_modes` — array of strings
- `priority` — string
- `research_needs` — array of strings
- `notes` — string

### Optional fields for each target item
- `aliases` — array of strings
- `historical_specificity` — string
- `visual_priority_note` — string
- `dedupe_group_id` — string

## 4.7 `intake_notes`
- required
- type: array of strings
- may be empty

## 4.8 `warnings`
- required
- type: array of strings
- may be empty

---

## 5. Frozen enums

## 5.1 `target_type`
Allowed values:
- `person_historical`
- `location_historical`
- `object_artifact`
- `architectural_anchor`
- `interior_space`
- `symbolic_sequence`
- `event_reference`
- `environment_reference`

## 5.2 `research_modes`
Allowed values:
- `factual_evidence`
- `visual_reference`
- `stylistic_inspiration`
- `contextual_reference`

## 5.3 `priority`
Allowed values:
- `critical`
- `high`
- `medium`
- `low`

---

## 6. Validation rules

1. `contract_version` must match exactly
2. `sector` must equal `s4_asset_research`
3. every `scene_index.linked_target_ids[*]` must reference an existing `research_targets[*].target_id`
4. every `research_targets[*].scene_ids[*]` should reference an existing `scene_index[*].scene_id`
5. every target must have at least one `source_entity_id`
6. every target must have at least one `research_mode`
7. every target must have at least one `research_need`
8. `warnings` and `intake_notes` must always exist, even if empty

---

## 7. Edge cases

## 7.1 Zero targets
If zero targets are produced, the file must still be written.

In that case:
- `research_targets = []`
- `warnings` must include explicit explanation
- supervisor must treat this as a special case, not as a missing file condition

## 7.2 Partial scene mapping
If some targets cannot be confidently linked to scenes:
- keep target
- allow `scene_ids = []` only if warning is added
- prefer explicit warning over silent omission

---

## 8. Example

```json
{
  "contract_version": "s4.research_intake.v1",
  "sector": "s4_asset_research",
  "metadata": {
    "job_id": "job_006_pt_001",
    "video_id": "video_006_pt_001",
    "account_id": "006",
    "language": "pt",
    "generated_at": "2026-04-04T18:00:00Z",
    "generated_from": "compiled_entities.json"
  },
  "source_refs": {
    "compiled_entities_path": "C:\\...\\compiled_entities.json"
  },
  "scene_index": [
    {
      "scene_id": "scene_001",
      "linked_target_ids": ["rt_001", "rt_002"],
      "notes": "Opening and hotel exterior setup"
    }
  ],
  "research_targets": [
    {
      "target_id": "rt_001",
      "canonical_label": "Hotel Quitandinha",
      "target_type": "architectural_anchor",
      "source_entity_ids": ["l2", "o1"],
      "scene_ids": ["scene_001"],
      "research_modes": ["factual_evidence", "visual_reference"],
      "priority": "critical",
      "research_needs": [
        "historical exterior views",
        "wide iconic facade shots"
      ],
      "notes": "Deduplicated from location/object overlap"
    }
  ],
  "intake_notes": [
    "Deduped overlapping architectural targets"
  ],
  "warnings": []
}
```
