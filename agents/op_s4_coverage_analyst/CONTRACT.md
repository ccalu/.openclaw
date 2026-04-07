# CONTRACT.md

## Input

- **intake_path**: Caminho absoluto para `s4_research_intake.json` (schema `s4.research_intake.v1`)
- **sector_root**: Caminho absoluto para root do sector S4

O helper le internamente:
- intake (research_targets + scene_index)
- evaluated_candidate_set.json de cada target em `<sector_root>/targets/<target_id>/`

## Output

- `<sector_root>/compiled/coverage_report.json` conforming to `s4.coverage_report.v1`

## Coverage states

| State | Significado |
|-------|-------------|
| `covered` | factual_evidence + visual_reference presentes |
| `partially_covered` | apenas factual_evidence ou visual_reference |
| `inspiration_only` | apenas stylistic_inspiration |
| `unresolved` | nenhum candidate aprovado ou evaluated set ausente |

## Success criteria

1. `coverage_report.json` existe em `<sector_root>/compiled/`
2. Schema valida via schema_validator.py com tipo `coverage_report`
3. Target coverage entries existem para todos os targets do intake
4. Scene coverage entries existem para todas as cenas do scene_index

## Boundary

Este operador faz APENAS determinacao de cobertura. Nao reclassifica, nao descobre, nao compila.
