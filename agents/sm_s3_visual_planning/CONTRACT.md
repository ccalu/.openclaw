# CONTRACT.md

## Bootstrap input
Lês um payload compatível com `s3.supervisor_bootstrap.v1`.

Campos obrigatórios:
- `kind = s3_start`
- `contract_version`
- `job_id`
- `video_id`
- `account_id`
- `language`
- `run_root`
- `sector_root`
- `source_package_path`
- `checkpoints_dir`
- `operators_dir`
- `compiled_dir`
- `logs_dir`
- `dispatch_dir`
- `bootstrap_checkpoint_path`

## Path handling rule
Todos os paths recebidos no bootstrap devem ser tratados como literais e canónicos para aquele run.

Regras obrigatórias:
- não reconstruir paths a partir de fragmentos textuais ou nomes de pasta
- não substituir caracteres Unicode “parecidos” (ex.: `—` por `-`)
- não trocar o root do sector por um root derivado do workspace local do agent
- se um path do bootstrap não existir, falhar explicitamente em vez de improvisar outro path

## Outputs obrigatórios
- artefacto de arranque do supervisor
- `operator_activation_plan.json`
- payloads de dispatch dos operators activos
- tentativa de invoke real por `exec -> openclaw agent --agent <operator_agent_id> --session-id <unique-run-operator-session> --message "..." --json --timeout 1800` ou checkpoint honesto da falha desse launch
- snapshots/artefactos de monitorização e validação
- `compiled/compiled_entities.json`
- `compiled/s3_sector_report.md`
- `checkpoints/s3_sector_completed.json` ou `checkpoints/s3_sector_failed.json`
- espelho macro obrigatório em `b2_root/checkpoints/s3_completed.json` ou `b2_root/checkpoints/s3_failed.json`

## Success rule
Só fechas o sector como concluído quando os artefactos finais existirem e estiverem estruturalmente coerentes.

Além disso, sucesso sectorial só conta como pronto para o bloco quando:
- os operators canónicos do activation plan tiverem sido realmente invocados via CLI
- os outputs canónicos dos operators existirem no disco
- `compiled/compiled_entities.json` existir
- `compiled/s3_sector_report.md` existir
- o checkpoint macro `b2_root/checkpoints/s3_completed.json` tiver sido escrito no root correcto do run

## Canonical operator rule
Para a fase actual do S3, o supervisor só pode tratar estes 4 operators como canónicos:
- `human_subject_extractor`
- `environment_location_extractor`
- `object_artifact_extractor`
- `symbolic_event_extractor`

Outputs ou taxonomias paralelas como `locations`, `artifacts`, `atmosphere`, `era_context` podem existir apenas como derivados auxiliares pós-compile, mas nunca substituem os outputs canónicos dos operators nem provam dispatch correcto.

## Failure rule
Se faltar precondição crítica, falha explicitamente e persiste o checkpoint de falha.

Se o launch real de operators não ocorrer pelo primitive canónico, não mascarar esse problema como sucesso limpo. Se o activation plan previa 4 operators activos, não degradar silenciosamente para subset de 1 sem isso ficar explícito nos checkpoints e no resultado final.

Se o supervisor fizer trabalho de operator internamente em vez de despachar os operators canónicos, isso deve ser tratado como violação do contract actual, não como sucesso do sector.

## Fresh-session rule for operator launches
Cada invoke do supervisor para operator deve usar um `session-id` único por run e por operator.

Objectivo:
- evitar acumulação de contexto entre vídeos
- evitar bleed entre activações de operators diferentes
- reduzir custo inútil de transcripts longas

Exemplo conceptual de naming:
- `s3-<job_id>-human-<run_token>`
- `s3-<job_id>-environment-<run_token>`
- `s3-<job_id>-object-<run_token>`
- `s3-<job_id>-symbolic-<run_token>`
