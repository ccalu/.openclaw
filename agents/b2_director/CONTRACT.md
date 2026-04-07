# CONTRACT.md

## Input contracts

### 1. Bootstrap contract
Usado para a primeira activação do bloco.

Nesta fase, deves tratar o bootstrap canónico como `b2.bootstrap.v1`.

```json
{
  "kind": "b2_start",
  "contract_version": "b2.bootstrap.v1",
  "job_id": "string",
  "run_root": "string",
  "b2_root": "string",
  "account_id": "string",
  "language": "string",
  "inputs": {},
  "mode": "s3_only"
}
```

### 2. Resume contract
Usado para reentrada após evento sectorial.

Nesta fase, deves tratar o resume canónico como `b2.resume.v1`.

```json
{
  "kind": "b2_resume",
  "contract_version": "b2.resume.v1",
  "run_root": "string",
  "b2_root": "string",
  "reason": "s3_completed | s3_failed | s4_completed | s4_failed | s5_completed | s5_failed | s6_completed | s6_failed",
  "trigger_artifact": "string"
}
```

## Files you must read
Antes de decidir, deves ler pelo menos:
- `{b2_root}/state/b2_state.json` (se existir)
- checkpoint que motivou a activação actual
- artefacto final do sector anterior, quando relevante para validação da progressão

## Sector artifact validation rule
Quando um checkpoint sectorial como `s3_completed.json` apontar explicitamente para artefactos por path (ex.: `compiled_entities_path`, `sector_report_path`), esses paths declarados no checkpoint são a fonte de verdade.

Regras obrigatórias:
- não assumir paths hardcoded alternativos na raiz de `b2/`
- não procurar `compiled_entities.json` ou `s3_sector_report.md` fora dos paths apontados pelo checkpoint sectorial
- se os paths declarados não existirem, falhar explicitamente em vez de procurar ficheiros “parecidos” noutro sítio

## Files you may write
Podes escrever:
- `{b2_root}/state/b2_state.json`
- checkpoints em `{b2_root}/checkpoints/`
- `b2_bootstrap_ready.json`
- `s3_requested.json`
- log leve do director em `{b2_root}/logs/`
- artefacto final do bloco (`b2_completed.json` ou `b2_failed.json`) quando apropriado
- bootstrap do supervisor do S3 e `s3_source_package.json` em `{b2_root}/sectors/s3_visual_planning/`

## Activation outputs
Após decidir, deves ou:
1. activar o supervisor do próximo sector
2. marcar falha do bloco
3. marcar conclusão do bloco

No primeiro teste em `mode = s3_only`, a activação relevante é apenas:
- bootstrap do B2 -> `sm_s3_visual_planning`
- reentrada por `s3_completed` -> `b2_completed.json`
- reentrada por `s3_failed` -> `b2_failed.json`

## Validation scope
A tua validação antes de progredir deve ser estruturalmente mínima:
- verificar existência do artefacto esperado
- verificar validade estrutural mínima

Não deves fazer validação semântica profunda do sector. Isso pertence ao supervisor sectorial.

## Non-goals
Não deves produzir directamente artefactos sectoriais como:
- outputs do S3
- outputs do S4
- outputs do S5
- outputs do S6

Esses pertencem aos respectivos supervisores.
