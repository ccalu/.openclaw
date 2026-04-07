# MISSION.md

Ler dispatch message, consumir research_intake.json e research_batch_manifest.json do disco, e gerar um target_research_brief.json por target no batch — com search_goals concretos, angles de discovery e storage paths — validado contra schema e persistido em disco.

## Steps

1. Parse dispatch message para extrair: intake_path, manifest_path, sector_root, job_id
2. Ler research_intake.json do disco via `exec cat <intake_path>`
3. Ler research_batch_manifest.json do disco via `exec cat <manifest_path>`
4. Para cada target no batch do manifest:
   a. Gerar target_research_brief.json com planning semantico:
      - search_goals concretos baseados em target_type, canonical_label e research_needs
      - Research angles e source priorities
      - Storage paths para output do worker
   b. Escrever brief em `targets/<sanitized_target_id>/<target_id>_brief.json`
5. Validar cada brief contra schema: `exec python "C:\Users\User-OEM\Desktop\OpenClaw Workspace\content_factory_block2\S4\helpers\schema_validator.py" <brief_path> target_research_brief`
6. Reportar sucesso baseado em briefs persistidos e validados no disco

## Boundaries

- NAO fazer web search
- NAO spawnar workers
- NAO avaliar candidates
- Disco e verdade — briefs existem no filesystem ou nao existem
