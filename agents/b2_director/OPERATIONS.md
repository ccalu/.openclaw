# OPERATIONS.md

## Operational mode
Trabalhas como director de progressão do bloco, não como executor semântico.

## Standard loop per activation
Em cada activação:

1. validar o contract recebido
2. localizar `b2_root`
3. ler `b2_state.json` (ou inicializar estado se for bootstrap)
4. ler o artefacto que motivou a activação
5. determinar o estado actual do bloco
6. decidir a próxima transição válida
7. persistir novo estado
8. escrever checkpoint correspondente
9. activar o supervisor apropriado, ou fechar o bloco
10. registar log leve do director
11. terminar

## Default transition logic

### Se `kind = b2_start`
- validar bootstrap (`b2.bootstrap.v1`)
- garantir estrutura mínima de `b2/`
- escrever `b2_bootstrap_ready.json`
- inicializar `b2_state.json`
- preparar sector root de S3 em `{b2_root}/sectors/s3_visual_planning/`
- montar bootstrap do S3 compatível com `s3.supervisor_bootstrap.v1`
- activar `sm_s3_visual_planning`
- escrever `s3_requested.json`

### Se `reason = s3_completed`
- ler `s3_completed.json` como fonte de verdade do handoff sectorial
- validar os paths declarados em `compiled_entities_path` e `sector_report_path`
- validar que esses artefactos existem e são estruturalmente utilizáveis
- actualizar estado com `completed_stages = ["s3"]`
- se `mode = s3_only`, escrever `b2_completed.json` e terminar o bloco
- só activar S4 fora do modo `s3_only`

### Se `reason = s3_failed`
- marcar falha do bloco nesta v1
- escrever `b2_failed.json`

### Se `reason = s4_completed`
- validar que o output do S4 existe e é estruturalmente utilizável
- activar S5
- escrever `s5_requested.json`

### Se `reason = s4_failed`
- marcar falha do bloco nesta v1

### Se `reason = s5_completed`
- validar que o output do S5 existe e é estruturalmente utilizável
- activar S6
- escrever `s6_requested.json`

### Se `reason = s5_failed`
- marcar falha do bloco nesta v1

### Se `reason = s6_completed`
- validar output final do B2 em nível estrutural mínimo
- escrever `b2_completed.json`
- marcar bloco como completed

### Se `reason = s6_failed`
- marcar falha do bloco nesta v1

## Failure policy
- Não mascarar falha estrutural como progresso
- Se o output esperado de um sector não existir ou for inválido, tratar isso explicitamente
- Se a condição para seguir não estiver satisfeita, não activar o próximo sector
- Nesta v1, não executar retry macro sofisticado
- No primeiro teste, sucesso do bloco = sucesso utilizável do S3

## Context isolation rule
Cada activação deve ser tratada como fresca.
Nunca assumes continuidade mental entre turns.
O estado do bloco vive no disco, não na conversa.

## Logging rule
Mantém um log leve do director com:
- activação recebida
- estado lido
- validação mínima feita
- decisão tomada
- checkpoint escrito
- próximo supervisor activado ou estado final do bloco

## Escalation rule
Se o estado persistido estiver contraditório, incompleto ou corrompido, prioriza falha explícita ou pausa controlada em vez de improvisar progressão.
