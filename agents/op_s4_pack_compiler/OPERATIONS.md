# OPERATIONS.md

## Sequencia de execucao

1. Parse activation message para extrair: `intake_path`, `sector_root`, `job_id`, `video_id`, `account_id`, `language`
2. Executar helper:
   ```
   exec python "C:\Users\User-OEM\Desktop\OpenClaw Workspace\content_factory_block2\S4\helpers\pack_compiler.py" <intake_path> <sector_root> <job_id> <video_id> <account_id> <language>
   ```
3. Validar que `<sector_root>/compiled/s4_research_pack.json` existe no disco
4. Validar que `<sector_root>/compiled/s4_sector_report.md` existe no disco
5. Validar schema:
   ```
   exec python "C:\Users\User-OEM\Desktop\OpenClaw Workspace\content_factory_block2\S4\helpers\schema_validator.py" <sector_root>/compiled/s4_research_pack.json research_pack
   ```
6. Reportar resultado (sucesso ou falha) baseado em artifacts no disco

## Input format — V3

O helper le dois formatos de input:

### Formato V3 (primario): `{tid}_asset_materialization_report.json`
- Producido pelo `s4_visual_evaluator.py` via `s4_asset_pipeline.py`
- Contem: `approved_assets[]` com `filename`, `source_url`, `relevance_score`, `rationale`

### Formato legacy (fallback): `evaluated_candidate_set.json`
- Producido pelo antigo `op_s4_candidate_evaluator` (DEPRECATED)
- O helper verifica formato V3 primeiro. Se nao encontrado, faz fallback para legacy.

## Regras

- Compiler nao esconde gaps. Unresolved gaps do coverage report devem aparecer no pack.
- Compiler nao reescreve verdade. Warnings sao preservadas tal como estao.
- Compiler nao reclassifica. Reports/evaluated sets sao inputs imutaveis.
- Se helper falhar, reportar erro com stdout/stderr. Nao tentar corrigir manualmente.
- Nao refazer coverage analysis. Nao fazer discovery. Nao dispatchar outros operadores.
- Este e um dos 2 actors activos no S4 V3. Os outros 4 foram substituidos por helper-direct.
