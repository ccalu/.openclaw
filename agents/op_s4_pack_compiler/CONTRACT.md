# CONTRACT.md

## Input

- **intake_path**: Caminho absoluto para `s4_research_intake.json` (schema `s4.research_intake.v1`)
- **sector_root**: Caminho absoluto para root do sector S4
- **job_id**: Identificador do job
- **video_id**: Identificador do video
- **account_id**: Identificador da conta
- **language**: Codigo de lingua (e.g. `pt`, `en`)

O helper le internamente:
- intake (research_targets + scene_index)
- evaluated_candidate_set.json de cada target em `<sector_root>/targets/<target_id>/`
- coverage_report.json em `<sector_root>/compiled/`
- candidate_set.json (raw) de cada target para asset/preview/capture paths

## Output

- `<sector_root>/compiled/s4_research_pack.json` conforming to `s4.research_pack.v1`
- `<sector_root>/compiled/s4_sector_report.md`

## Pack structure

O research pack deve conter:
- **metadata**: job_id, video_id, account_id, language, sector, generated_at, status
- **target_results**: best_factual_evidence_ids, best_visual_reference_ids, best_stylistic_inspiration_ids, coverage_state, notes — por target
- **scene_results**: linked_target_ids, recommended_candidate_ids, coverage_state, notes — por cena
- **asset_manifest**: candidate_id, target_id, local_asset_path
- **preview_manifest**: candidate_id, target_id, preview_path
- **capture_manifest**: candidate_id, target_id, capture_path
- **unresolved_gaps**: lista preservada do coverage report
- **warnings**: lista acumulada de warnings

## Success criteria

1. `s4_research_pack.json` existe em `<sector_root>/compiled/`
2. `s4_sector_report.md` existe em `<sector_root>/compiled/`
3. Schema valida via schema_validator.py com tipo `research_pack`

## Boundary

Este operador faz APENAS compilacao. Nao julga qualidade. Nao reclassifica candidates. Nao esconde gaps para parecer mais limpo.
