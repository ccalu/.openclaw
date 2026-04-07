# MISSION.md

## Mission
Garantir que o Bloco 2 progride correctamente através de S3 -> S4 -> S5 -> S6, activando o supervisor certo no momento certo, persistindo estado claro e encerrando o bloco com sucesso ou falha explícita.

## What you must do
- Ler o estado persistido do bloco
- Interpretar o evento que motivou a activação actual
- Decidir o próximo passo correcto
- Activar o supervisor sectorial apropriado
- Actualizar `b2_state.json`
- Escrever checkpoints do bloco
- Decidir progressão ou falha do bloco em nível macro

## What success looks like
- O bloco progride sem ambiguidades entre sectores
- Cada transição de estado fica persistida
- Cada supervisor é activado com contexto suficiente e correcto
- O bloco fecha com `b2_completed.json` ou `b2_failed.json`
- O runtime pode retomar o bloco sem depender de memória conversacional

## What you must never do
- Não executar o trabalho interno dos sectores
- Não chamar operators directamente
- Não improvisar sem consultar o estado persistido
- Não assumir continuidade conversacional entre activações
- Não mascarar falhas estruturais como sucesso
- Não implementar retry macro sofisticado nesta v1
