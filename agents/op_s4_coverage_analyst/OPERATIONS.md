# OPERATIONS.md

## Sequencia de execucao

1. Parse activation message para extrair: `intake_path`, `sector_root`
2. Validar que intake_path existe no disco
3. Executar helper:
   ```
   exec python "C:\Users\User-OEM\Desktop\OpenClaw Workspace\content_factory_block2\S4\helpers\coverage_analyst.py" <intake_path> <sector_root>
   ```
4. Validar que `<sector_root>/compiled/coverage_report.json` existe no disco
5. Validar schema:
   ```
   exec python "C:\Users\User-OEM\Desktop\OpenClaw Workspace\content_factory_block2\S4\helpers\schema_validator.py" <sector_root>/compiled/coverage_report.json coverage_report
   ```
6. Reportar resultado (sucesso ou falha) baseado em artifacts no disco

## Input format — V3

O helper le dois formatos de input:

### Formato V3 (primario): `{tid}_asset_materialization_report.json`
- Producido pelo `s4_visual_evaluator.py` via `s4_asset_pipeline.py`
- Contem: `approved_assets[]`, `rejected_count`, `total_evaluated`, `evaluation_notes`
- Cada asset tem: `filename`, `source_url`, `relevance_score`, `rationale`

### Formato legacy (fallback): `evaluated_candidate_set.json`
- Producido pelo antigo `op_s4_candidate_evaluator` (DEPRECATED)
- O helper verifica formato V3 primeiro. Se nao encontrado, faz fallback para legacy.

## Regras

- Materialization reports / evaluated sets sao verdade. Nao reclassificar candidates.
- Coverage states devem ser explicaveis a partir dos inputs (intake + reports).
- Se helper falhar, reportar erro com stdout/stderr. Nao tentar corrigir manualmente.
- Nao compilar pack. Nao fazer discovery. Nao dispatchar outros operadores.
- Este e um dos 2 actors activos no S4 V3. Os outros 4 foram substituidos por helper-direct.
