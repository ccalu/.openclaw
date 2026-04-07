# CONTRACT.md

## Input

Dispatch message com:
- candidate_set_path
- brief_path
- sector_root
- target_id

## Leitura

- candidate_set.json (raw candidates do worker)
- target_research_brief.json (contexto do target)

## Output

evaluated_candidate_set.json conformando a `s4.evaluated_candidate_set.v1`

### Required output shape

```json
{
  "contract_version": "s4.evaluated_candidate_set.v1",
  "target_id": "...",
  "canonical_label": "...",
  "target_type": "...",
  "scene_ids": ["..."],
  "evaluated_candidates": [
    {
      "candidate_id": "c001",
      "final_classification": "factual_evidence|visual_reference|stylistic_inspiration|reject",
      "target_fitness_note": "...",
      "downstream_usefulness_note": "...",
      "asset_usability_note": "...",
      "is_best_candidate": true
    }
  ],
  "best_candidate_ids": ["c001"],
  "evaluator_notes": ["..."],
  "warnings": ["..."]
}
```

### Campos required por evaluated_candidate

- candidate_id — string
- final_classification — string (enum: factual_evidence, visual_reference, stylistic_inspiration, reject)
- target_fitness_note — string
- downstream_usefulness_note — string
- asset_usability_note — string
- is_best_candidate — boolean

### Campos opcionais por evaluated_candidate

- confidence_adjustment_note — string
- quality_note — string
- provenance_note — string
- local_asset_path — string ou null
- preview_path — string ou null
- capture_path — string ou null

## Semantica overlay

Este set NAO substitui candidate_set. Downstream faz join por candidate_id.
O raw candidate_set permanece preservado como artifact de discovery.

## Criterio de sucesso

- Ficheiro existe no disco
- Schema valida via schema_validator.py

## Criterio de falha

- Explicito, com razao documentada
