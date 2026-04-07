# OPERATIONS.md

## Procedure

### Step 1 — Parse activation message
Extrair do dispatch:
- `intake_path`
- `manifest_path`
- `sector_root`
- `job_id`
- `batch_id` (se fornecido)

### Step 2 — Read intake
```
exec cat <intake_path>
```
Parsear research_intake.json. Extrair `research_targets` e `scene_index`.

### Step 3 — Read manifest
```
exec cat <manifest_path>
```
Parsear research_batch_manifest.json. Identificar targets no batch activo.

### Step 4 — Generate briefs
Para cada target no batch:

**4a. Extract target metadata do intake:**
- target_id, canonical_label, target_type, scene_ids
- research_modes, priority, research_needs, source_entity_ids

**4b. Generate search_goals — concretos, especificos, actionable:**

Exemplos por tipo:
- architectural_anchor "Hotel Quitandinha":
  - `"Historical exterior photographs Hotel Quitandinha 1940s"`
  - `"Interior casino hall Quitandinha architecture"`
  - `"Aerial view Quitandinha complex Petropolis"`
- person_historical "Joaquim Rolla":
  - `"Joaquim Rolla portrait photograph historical"`
  - `"Joaquim Rolla Quitandinha entrepreneur biography"`
- symbolic_sequence "decadencia do luxo":
  - `"Empty luxury hotel interior abandoned atmosphere"`
  - `"Decay grandeur architecture photographic reference"`

**4c. Derive storage_paths (todos absolutos):**
- `target_root`: `<sector_root>/targets/<sanitized_target_id>`
- `candidate_set_path`: `<target_root>/<target_id>_candidate_set.json`
- `assets_dir`: `<target_root>/assets`
- `previews_dir`: `<target_root>/previews`
- `captures_dir`: `<target_root>/captures`

**4d. Compose brief JSON** com todos os required fields.

**4e. Write brief to disk:**
```
exec python -c "import json, pathlib; p=pathlib.Path(r'<target_root>/<target_id>_brief.json'); p.parent.mkdir(parents=True, exist_ok=True); p.write_text(json.dumps(<brief_dict>, indent=2, ensure_ascii=False), encoding='utf-8')"
```

**4f. Validate brief:**
```
exec python "C:\Users\User-OEM\Desktop\OpenClaw Workspace\content_factory_block2\S4\helpers\schema_validator.py" <brief_path> target_research_brief
```

### Step 5 — Report
Listar:
- Briefs escritos (path + target_id)
- Resultados de validacao (pass/fail por brief)
- Warnings encontrados

## Rules

1. search_goals devem ser CONCRETE search strings, nao descricoes vagas
2. output_contract e sempre `"s4.candidate_set.v1"`
3. Todos os storage_paths devem ser absolutos
4. Sanitize target_id: lowercase, replace non-ASCII e caracteres especiais com underscore
5. notes e warnings devem ser arrays (mesmo se vazios)
6. Nunca inventar target_ids — usar exactamente os do intake/manifest
7. Nunca executar web search
8. Nunca spawnar workers
9. Nunca avaliar candidates
