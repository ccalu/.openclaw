# S3 — Supervisor Runtime Contract (v1)

## Objectivo

Este documento fecha a versão operacional mínima do `sm_s3_visual_planning` para um primeiro run narrow com agents reais.

O foco não é ainda paralelismo perfeito nem retries sofisticados.
O foco é permitir um primeiro ciclo real e auditável.

---

## Input do supervisor

O supervisor recebe um payload compatível com `s3.supervisor_bootstrap.v1`.

---

## Sequência operacional mínima v1

1. validar bootstrap
2. escrever `s3_supervisor_started.json`
3. escrever `operator_activation_plan.json`
4. preparar 4 dispatch payloads no `dispatch/`
5. activar os 4 operators reais
6. aguardar outputs/checkpoints
7. validar outputs dos 4 operators
8. compilar `compiled_entities.json`
9. gerar `s3_sector_report.md`
10. escrever checkpoint final do sector
11. espelhar checkpoint macro no `b2_root/checkpoints/`

---

## Regra v1 do primeiro run

Para reduzir fragilidade do primeiro run real:
- os 4 operators entram sempre activos
- não há activation plan selectivo sofisticado
- não há retry automático v1
- falha estrutural crítica de qualquer operator pode falhar o sector

---

## Dispatch payloads

O supervisor deve escrever:

```text
{sector_root}/dispatch/human_subject_extractor_job.json
{sector_root}/dispatch/environment_location_extractor_job.json
{sector_root}/dispatch/object_artifact_extractor_job.json
{sector_root}/dispatch/symbolic_event_extractor_job.json
```

Todos compatíveis com `s3.operator_dispatch.v1`.

---

## Primitive oficial v1 para supervisor -> operator

No ambiente actual, a primitive oficial do primeiro run narrow deixa de ser ACP/sessions_spawn.

O caminho correcto passa a ser:

```text
exec -> openclaw agent --agent <operator_agent_id> --message "..." --json
```

### Razão

Foi provado no ambiente actual que:
- ACP está indisponível como backend operativo para este hop
- `openclaw agent --agent ...` consegue lançar um operator real com sucesso

### Regra obrigatória

O supervisor deve:
1. resolver o `operator_agent_id`
2. construir uma mensagem curta que aponte para o dispatch payload
3. invocar o operator via `exec` com `openclaw agent --agent ... --json`
4. só depois validar os artefactos escritos pelo operator

### Fallback policy

Nesta fase:
- **não** tentar ACP primeiro
- **não** mascarar impossibilidade de launch real como sucesso limpo
- se o launch real falhar, o sector deve degradar/falhar explicitamente

---

## Output paths esperados

```text
{sector_root}/operators/human_subject_extractor/output.json
{sector_root}/operators/environment_location_extractor/output.json
{sector_root}/operators/object_artifact_extractor/output.json
{sector_root}/operators/symbolic_event_extractor/output.json
```

---

## Critério de sucesso do sector

O sector só fecha com sucesso quando existirem:
- `compiled/compiled_entities.json`
- `compiled/s3_sector_report.md`
- `checkpoints/s3_sector_completed.json`
- espelho macro em `{b2_root}/checkpoints/s3_completed.json`

---

## Critério de falha do sector

Se faltar output crítico ou compile final utilizável, o supervisor deve escrever:
- `checkpoints/s3_sector_failed.json`
- espelho macro em `{b2_root}/checkpoints/s3_failed.json`

---

## Regra de espelho macro para o B2

O supervisor do S3 é dono do fecho do sector, mas o `b2_director` precisa de um artefacto macro para reentrada.

Por isso, no fecho do sector, o supervisor deve escrever também no `b2_root/checkpoints/`:
- `s3_completed.json`
- ou `s3_failed.json`
