# CONTRACT.md

## Input

Dispatch message do sm_s4_asset_research com campos:
- `intake_path` — caminho absoluto para research_intake.json
- `manifest_path` — caminho absoluto para research_batch_manifest.json
- `sector_root` — caminho absoluto para root do sector S4
- `job_id` — identificador do job
- `video_id` — identificador do video
- `account_id` — identificador da conta
- `language` — lingua do video

## Required Reading

- `research_intake.json` (schema: `s4.research_intake.v1`) — targets, scene_index, metadata
- `research_batch_manifest.json` — batch de targets a processar

## Output

Um ficheiro por target no batch:
```
<sector_root>/targets/<sanitized_target_id>/<target_id>_brief.json
```

Cada brief deve conformar com `s4.target_research_brief.v1`.

## Required Brief Fields

- `contract_version` — fixed: `"s4.target_research_brief.v1"`
- `job_id` — do dispatch
- `batch_id` — do manifest ou dispatch
- `target_id` — do intake target
- `canonical_label` — do intake target
- `target_type` — do intake target
- `scene_ids` — array de scene_ids linkados ao target
- `research_modes` — array de modos de research
- `priority` — `critical` | `high` | `medium` | `low`
- `search_goals` — array de strings concretas de search (NAO vagas)
- `research_needs` — array de needs do intake, sharpened
- `source_entity_ids` — array de entity IDs de S3
- `storage_paths` — objecto com paths absolutos:
  - `target_root` — `<sector_root>/targets/<sanitized_target_id>`
  - `candidate_set_path` — `<target_root>/<target_id>_candidate_set.json`
  - `assets_dir` — `<target_root>/assets`
  - `previews_dir` — `<target_root>/previews`
  - `captures_dir` — `<target_root>/captures`
- `output_contract` — fixed: `"s4.candidate_set.v1"`
- `notes` — array (pode ser vazio)
- `warnings` — array (pode ser vazio)

## Path Handling

- Usar paths exactamente como fornecidos no dispatch
- Derivar target paths usando sanitized target_id: lowercase, ASCII only, underscores
- Todos os storage_paths devem ser absolutos

## Success Criteria

- Todos os briefs esperados existem no disco
- Todos os briefs validam contra schema via schema_validator.py

## Boundary

- Planning e framing only
- Sem execucao de search
- Sem avaliacao de candidates
- Sem dispatch de workers
