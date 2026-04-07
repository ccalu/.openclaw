# CONTRACT.md

## Input
Dispatch message com:
- `compiled_entities_path` — path para compiled_entities.json do S3
- `sector_root` — path raiz do sector S4
- `job_id`
- `video_id`
- `account_id`
- `language`

## Output minimo
- `<sector_root>/intake/research_intake.json` (contract_version: s4.research_intake.v1)
- `<sector_root>/intake/target_builder_report.md`

## Path handling
Usar paths exactamente como recebidos. Nunca reconstruir.

## Success
Ambos os ficheiros existem no disco e research_intake.json e non-empty.

## Failure
Explicita, com razao. Nunca sucesso ambiguo.
