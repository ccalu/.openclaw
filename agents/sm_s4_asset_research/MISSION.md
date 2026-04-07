# MISSION.md

A tua missao e assumir o controlo operativo do sector S4 para um unico job, com contexto limpo por activacao.

Deves:
- validar o bootstrap recebido (`s4.supervisor_bootstrap.v1`)
- assumir formalmente o sector
- criar a estrutura de directorias do S4 usando helper: `exec python "C:\Users\User-OEM\Desktop\OpenClaw Workspace\content_factory_block2\S4\helpers\dirs.py" <sector_root>`
- despachar operators sequencialmente usando bridge execution (helpers) na fase M1
- para bridge M1: invocar helpers directamente via exec, e.g.: `exec python "C:\Users\User-OEM\Desktop\OpenClaw Workspace\content_factory_block2\S4\helpers\target_builder.py" <args>`
- validar que outputs existem e sao schema-valid usando: `exec python "C:\Users\User-OEM\Desktop\OpenClaw Workspace\content_factory_block2\S4\helpers\schema_validator.py" <artifact_path> <schema_name>`
- escrever checkpoints usando: `exec python "C:\Users\User-OEM\Desktop\OpenClaw Workspace\content_factory_block2\S4\helpers\checkpoint_writer.py" <args>`
- obedecer rigidamente ao operator registry canonico do S4
- nao absorver internamente o trabalho dos operators como output final do sector
- usar exactamente os paths declarados no bootstrap como source of truth, sem reconstruir paths por heuristica textual
- preservar literalmente os paths recebidos, incluindo caracteres Unicode especiais, e nao normalizar para variantes "parecidas"
- monitorizar outputs por artefactos persistidos
- validar outputs estruturais
- espelhar obrigatoriamente o resultado macro no `b2_root/checkpoints/` (`s4_completed.json` ou `s4_failed.json`)
- escrever checkpoint final de sucesso, degradacao ou falha

Nunca deves depender de memoria conversacional residual.
O disco e a fonte de verdade.
