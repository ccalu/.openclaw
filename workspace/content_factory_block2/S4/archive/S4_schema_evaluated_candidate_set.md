# S4 Schema — Evaluated Candidate Set

_Status: planning draft_
_Last updated: 2026-04-04_
_Contract id: `s4.evaluated_candidate_set.v1`_

---

## 1. Purpose

This schema defines the evaluated target-level output produced by `op_s4_candidate_evaluator`.

It transforms the raw `candidate_set` into a reviewed artifact where candidates are:

- reclassified if needed
- ranked/selected qualitatively
- annotated for downstream usability
- filtered from discovery noise into a more stable target-level evaluation output

This artifact is the bridge between:
- discovery output
- coverage analysis
- final pack compilation

It should be interpreted as an **evaluation overlay** on top of the raw `candidate_set`, not as a destructive replacement of the raw artifact.

That means:
- `candidate_set.json` remains the source of raw discovery output
- `evaluated_candidate_set.json` references the same `candidate_id`s
- evaluator adds judgment, final classification, and usability semantics
- downstream joins evaluated data with raw data by `candidate_id`

---

## 2. Producer and consumers

### Producer
- `op_s4_candidate_evaluator`

### Primary consumers
- `sm_s4_asset_research`
- `op_s4_coverage_analyst`
- `op_s4_pack_compiler`

### Secondary consumers
- humans
- debugging/review flows

---

## 3. Required top-level shape

```json
{
  "contract_version": "s4.evaluated_candidate_set.v1",
  "target_id": "string",
  "canonical_label": "string",
  "target_type": "string",
  "scene_ids": [],
  "evaluated_candidates": [],
  "best_candidate_ids": [],
  "evaluator_notes": [],
  "warnings": []
}
```

---

## 4. Field specification

## 4.1 `contract_version`
- required
- type: string
- fixed value: `s4.evaluated_candidate_set.v1`

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

## 4.6 `evaluated_candidates`
- required
- type: array
- may be empty in valid no-result cases

### Required fields for each evaluated candidate
- `candidate_id` — string
- `final_classification` — string
- `target_fitness_note` — string
- `downstream_usefulness_note` — string
- `asset_usability_note` — string
- `is_best_candidate` — boolean

### Optional fields for each evaluated candidate
- `confidence_adjustment_note` — string
- `quality_note` — string
- `provenance_note` — string
- `local_asset_path` — string or null
- `preview_path` — string or null
- `capture_path` — string or null

## 4.7 `best_candidate_ids`
- required
- type: array of strings
- may be empty
- must reference candidate IDs present in `evaluated_candidates`

## 4.8 `evaluator_notes`
- required
- type: array of strings
- may be empty

## 4.9 `warnings`
- required
- type: array of strings
- may be empty

---

## 5. Enums

## 5.1 `final_classification`
Allowed values:
- `factual_evidence`
- `visual_reference`
- `stylistic_inspiration`
- `reject`

---

## 6. Validation rules

1. `contract_version` must match exactly
2. every `best_candidate_ids[*]` must reference an `evaluated_candidates[*].candidate_id`
3. every `evaluated_candidate` must have `candidate_id`
4. every `evaluated_candidate` must have `final_classification`
5. `is_best_candidate = true` should normally imply presence in `best_candidate_ids`
6. `warnings` and `evaluator_notes` must always exist

---

## 7. Edge cases

## 7.1 No usable candidates
If discovery produced only weak/noisy results or zero candidates:
- `evaluated_candidates` may be empty
- `best_candidate_ids` may be empty
- `warnings` must explain that the target remains weakly covered or unresolved

## 7.2 All candidates rejected
Valid case.

In that case:
- keep the evaluated items if useful for auditability
- mark all with `final_classification = reject`
- leave `best_candidate_ids = []`
- coverage analyst must later interpret this accordingly

## 7.3 Evaluator uncertainty
If the evaluator cannot confidently distinguish between `factual_evidence` and `visual_reference`:
- it must still choose one final classification
- use notes/warnings to surface uncertainty
- avoid leaving classification implicit or blank

---

## 8. Example

```json
{
  "contract_version": "s4.evaluated_candidate_set.v1",
  "target_id": "rt_001",
  "canonical_label": "Hotel Quitandinha",
  "target_type": "architectural_anchor",
  "scene_ids": ["scene_001", "scene_002"],
  "evaluated_candidates": [
    {
      "candidate_id": "cand_001",
      "final_classification": "factual_evidence",
      "target_fitness_note": "Strong direct match for the hotel exterior.",
      "downstream_usefulness_note": "Useful for both factual grounding and S5/S6 visual selection.",
      "asset_usability_note": "Preview available locally; source asset not yet materialized.",
      "is_best_candidate": true,
      "preview_path": "C:\\...\\targets\\rt_001_hotel_quitandinha\\previews\\preview_001.jpg",
      "capture_path": "C:\\...\\targets\\rt_001_hotel_quitandinha\\captures\\capture_001.jpg"
    }
  ],
  "best_candidate_ids": ["cand_001"],
  "evaluator_notes": [
    "Most candidates were tourism-oriented, but this one remains useful as factual reference."
  ],
  "warnings": []
}
```
