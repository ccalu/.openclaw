# CONTRACT.md

## Bootstrap input
Les um payload compativel com `s4.supervisor_bootstrap.v1`.

Campos obrigatorios:
- `kind = s4_start`
- `contract_version = s4.supervisor_bootstrap.v1`
- `job_id`
- `video_id`
- `account_id`
- `language`
- `run_root`
- `b2_root`
- `sector_root`
- `upstream.compiled_entities_path`
- `upstream.sector_report_path`
- `checkpoints_dir`
- `dispatch_dir`
- `intake_dir`
- `targets_dir`
- `compiled_dir`
- `logs_dir`
- `runtime_dir`

## Path handling rule
Todos os paths recebidos no bootstrap devem ser tratados como literais e canonicos para aquele run.

Regras obrigatorias:
- nao reconstruir paths a partir de fragmentos textuais ou nomes de pasta
- nao substituir caracteres Unicode "parecidos" (ex.: `---` por `-`)
- nao trocar o root do sector por um root derivado do workspace local do agent
- se um path do bootstrap nao existir, falhar explicitamente em vez de improvisar outro path

## Outputs obrigatorios
- artefacto de arranque do supervisor
- dispatch artifacts por operator
- checkpoint files por fase
- `compiled/s4_research_pack.json`
- `compiled/s4_sector_report.md`
- `checkpoints/s4_sector_completed.json` ou `checkpoints/s4_sector_failed.json`
- espelho macro obrigatorio em `b2_root/checkpoints/s4_completed.json` ou `b2_root/checkpoints/s4_failed.json`

## Success rule
So fechas o sector como concluido quando os artefactos finais existirem e estiverem estruturalmente coerentes.

Sucesso sectorial so conta como pronto para o bloco quando:
- `s4_research_pack.json` existir no disco
- `s4_sector_report.md` existir no disco
- schema validation passar em ambos
- o checkpoint macro `b2_root/checkpoints/s4_completed.json` tiver sido escrito no root correcto do run

## Canonical operator list
Para a fase actual do S4, o supervisor so pode tratar estes 6 operators como canonicos:
- `op_s4_target_builder`
- `op_s4_web_investigator`
- `op_s4_target_research_worker`
- `op_s4_candidate_evaluator`
- `op_s4_coverage_analyst`
- `op_s4_pack_compiler`

## Failure rule
Se faltar precondicao critica, falha explicitamente e persiste o checkpoint de falha.

Tabela de decisao V1:
- `op_s4_target_builder` falha -> sector falha
- `op_s4_web_investigator` falha -> sector falha
- um ou mais `op_s4_target_research_worker` runs falham -> continuar com outputs disponiveis; coverage e final pack devem reflectir os gaps explicitamente
- `op_s4_candidate_evaluator` falha -> sector falha
- `op_s4_coverage_analyst` falha -> sector falha
- `op_s4_pack_compiler` falha -> sector falha

Se o supervisor fizer trabalho de operator internamente em vez de despachar os operators canonicos, isso deve ser tratado como violacao do contract actual, nao como sucesso do sector.

## Fresh-session rule for operator launches
Cada invoke do supervisor para operator deve usar um `session-id` unico por run e por operator.

Objectivo:
- evitar acumulacao de contexto entre videos
- evitar bleed entre activacoes de operators diferentes
- reduzir custo inutil de transcripts longas

Exemplo conceptual de naming:
- `s4-<job_id>-target_builder-<run_token>`
- `s4-<job_id>-web_investigator-<run_token>`
- `s4-<job_id>-research_worker-<target_id>-<run_token>`
- `s4-<job_id>-evaluator-<run_token>`
- `s4-<job_id>-coverage-<run_token>`
- `s4-<job_id>-pack_compiler-<run_token>`
