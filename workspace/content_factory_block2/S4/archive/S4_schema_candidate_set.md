# S4 Schema — Candidate Set

_Status: planning draft_
_Last updated: 2026-04-04_
_Contract id: `s4.candidate_set.v1`_

---

## 1. Purpose

This schema defines the canonical raw discovery output for one target, produced by `op_s4_target_research_worker`.

It is the first artifact that contains actual findings from the web research phase, including:

- discovered candidates
- source metadata
- acquisition mode
- local asset / preview / capture paths
- worker notes and warnings

This artifact is intentionally **pre-evaluation**.
It preserves what the worker found before the evaluator performs final qualification.

---

## 2. Producer and consumers

### Producer
- `op_s4_target_research_worker`

### Primary consumers
- `sm_s4_asset_research`
- `op_s4_candidate_evaluator`
- `op_s4_pack_compiler`

### Secondary consumers
- debugging/review flows
- humans

---

## 3. Required top-level shape

```json
{
  "contract_version": "s4.candidate_set.v1",
  "target_id": "string",
  "canonical_label": "string",
  "target_type": "string",
  "scene_ids": [],
  "candidates": [],
  "worker_notes": [],
  "warnings": []
}
```

---

## 4. Field specification

## 4.1 `contract_version`
- required
- type: string
- fixed value: `s4.candidate_set.v1`

## 4.2 `target_id`
- required
- type: string

## 4.3 `canonical_label`
- required
- type: string

## 4.4 `target_type`
- required
- type: string

## 4.5 `scene_ids`
- required
- type: array of strings
- may be empty only with explicit warning

## 4.6 `candidates`
- required
- type: array
- may be empty in legitimate no-result cases, but the file must still exist

### Required fields for each candidate item
- `candidate_id` — string
- `source_url` — string
- `page_title` — string
- `source_domain` — string
- `preliminary_classification` — string
- `rationale` — string
- `confidence` — number between `0.0` and `1.0`
- `licensing_note` — string
- `acquisition_mode` — string
- `local_asset_path` — string or null
- `preview_path` — string or null
- `capture_path` — string or null
- `timestamp` — ISO timestamp string

### Optional fields for each candidate item
- `image_url` — string
- `snippet` — string
- `search_query` — string
- `download_status` — string
- `worker_decision_note` — string

## 4.7 `worker_notes`
- required
- type: array of strings
- may be empty

## 4.8 `warnings`
- required
- type: array of strings
- may be empty

---

## 5. Enums

## 5.1 `preliminary_classification`
Allowed values:
- `factual_evidence`
- `visual_reference`
- `stylistic_inspiration`
- `reject`

This is preliminary and may later be corrected by evaluator.

## 5.2 `acquisition_mode`
Allowed values:
- `reference_only`
- `preview_asset`
- `materialized_asset`

## 5.3 `download_status` (optional)
Recommended enum:
- `not_attempted`
- `succeeded`
- `failed`
- `partial`

---

## 6. Validation rules

1. `contract_version` must match exactly
2. `target_id` must not be empty
3. `canonical_label` must not be empty
4. every candidate must have `candidate_id`
5. every candidate must have `source_url`
6. every candidate must have `acquisition_mode`
7. every candidate `confidence` must be a number in the range `[0.0, 1.0]`
8. if `acquisition_mode = materialized_asset`, then `local_asset_path` should normally be non-null
9. if `acquisition_mode = preview_asset`, then at least `preview_path` or `capture_path` should normally be non-null
10. `worker_notes` and `warnings` must always exist

---

## 7. Edge cases

## 7.1 Zero candidates found
This is a valid case.

In that case:
- `candidates = []`
- file must still be written
- `warnings` must explain why no candidates were found or retained

## 7.2 Failed file materialization
If the worker identified a useful candidate but failed to download/materialize the underlying file:
- candidate should still exist in the list if it is useful
- `acquisition_mode` may be downgraded to `reference_only`
  or remain represented via `preview_asset` if a capture/preview exists
- warning should be added
- do not silently drop useful candidates purely because the download failed

## 7.3 Weak candidate quality
Low-confidence or weak-fit candidates may still be included here.
The evaluator is expected to later:
- confirm
- downgrade
- reject

This artifact is meant to preserve discovery output, not to act as final judgment.

---

## 8. Example

```json
{
  "contract_version": "s4.candidate_set.v1",
  "target_id": "rt_001",
  "canonical_label": "Hotel Quitandinha",
  "target_type": "architectural_anchor",
  "scene_ids": ["scene_001", "scene_002"],
  "candidates": [
    {
      "candidate_id": "cand_001",
      "source_url": "https://example.com/quitandinha-photo",
      "page_title": "Historic Photo of Hotel Quitandinha",
      "source_domain": "example.com",
      "preliminary_classification": "factual_evidence",
      "rationale": "Directly depicts the hotel exterior in a historically relevant context.",
      "confidence": 0.86,
      "licensing_note": "Unknown licensing, verify before production use.",
      "acquisition_mode": "preview_asset",
      "local_asset_path": null,
      "preview_path": "C:\\...\\targets\\rt_001_hotel_quitandinha\\previews\\preview_001.jpg",
      "capture_path": "C:\\...\\targets\\rt_001_hotel_quitandinha\\captures\\capture_001.jpg",
      "timestamp": "2026-04-04T18:15:00Z",
      "search_query": "hotel quitandinha historic exterior"
    }
  ],
  "worker_notes": [
    "Most useful findings came from historical/tourism pages rather than generic image search."
  ],
  "warnings": []
}
```
