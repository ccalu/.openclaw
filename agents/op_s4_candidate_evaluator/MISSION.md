# MISSION.md

Ler dispatch message para obter candidate_set_path, brief_path, sector_root e target_id. Validar que ambos os ficheiros existem no disco.

Ler candidate_set.json e target_research_brief.json do disco:

```
exec cat <candidate_set_path>
exec cat <brief_path>
```

Avaliar TODOS os candidates em UM unico pass:
- Para cada candidate, determinar: final_classification (factual_evidence / visual_reference / stylistic_inspiration / reject)
- Escrever target_fitness_note, downstream_usefulness_note, asset_usability_note
- Decidir is_best_candidate
- Selecionar best_candidate_ids

Escrever evaluated_candidate_set.json completo no disco em:
`<sector_root>/targets/<target_id>/<target_id>_evaluated_set.json`

O evaluated set e um OVERLAY sobre candidate_set — usa candidate_id como join key.

Validar schema:

```
exec python "C:\Users\User-OEM\Desktop\OpenClaw Workspace\content_factory_block2\S4\helpers\schema_validator.py" <evaluated_set_path> evaluated_candidate_set
```

Sucesso = ficheiro existe no disco + schema valida.

## Limites estritos

- IMPORTANTE: NAO copiar preliminary_classification do worker. Fazer julgamento semantico independente.
- IMPORTANTE: Avaliar TODOS os candidates em UMA unica execucao, nao um de cada vez.
- NAO fazer discovery — isso e papel do worker
- NAO decidir coverage — isso e papel do coverage_analyst
- NAO compilar pack — isso e papel do pack_compiler
- NAO sobrescrever o raw candidate_set — output e overlay, nao replacement
