# B2 — S3-Only Runtime Wiring (v1)

## Objectivo

Este documento fecha o wiring operativo mínimo para o primeiro teste real do Bloco 2 em modo `s3_only`.

O foco aqui não é resolver o bloco inteiro, mas sim deixar claro:
- como o `b2_director` arranca
- como o S3 é activado
- como o S3 fecha
- como o B2 reconhece isso
- como o bloco termina no primeiro teste

---

## Regra do teste v1

No primeiro teste:
- o B2 arranca em `mode = s3_only`
- o `b2_director` inicializa o bloco
- o `b2_director` activa apenas o `sm_s3_visual_planning`
- o supervisor do S3 produz `compiled_entities.json` e `s3_sector_report.md`
- o supervisor fecha `s3_completed.json` ou `s3_failed.json`
- o `b2_director` reentra
- em caso de sucesso, o B2 fecha em `b2_completed.json`
- em caso de falha, o B2 fecha em `b2_failed.json`

---

## Layout mínimo do runtime

```text
{run_root}/b2/
  state/
    b2_state.json
  checkpoints/
    b2_bootstrap_ready.json
    s3_requested.json
    s3_completed.json | s3_failed.json
    b2_completed.json | b2_failed.json
  logs/
    b2_director_log.md
  sectors/
    s3_visual_planning/
      inputs/
      operators/
      compiled/
      checkpoints/
      logs/
      dispatch/
```

---

## Turno 1 — Bootstrap do B2

Input do director:
- contract `b2.bootstrap.v1`
- `mode = s3_only`

O director deve:
1. validar bootstrap
2. garantir estrutura mínima de `b2/`
3. escrever `b2_bootstrap_ready.json`
4. inicializar `state/b2_state.json`
5. escrever `checkpoints/s3_requested.json`
6. montar bootstrap do S3
7. activar `sm_s3_visual_planning`
8. terminar

---

## Shape mínima inicial de `b2_state.json`

```json
{
  "block": "b2",
  "mode": "s3_only",
  "status": "running",
  "current_stage": "s3",
  "completed_stages": [],
  "failed_stages": [],
  "next_stage": null,
  "last_event": "s3_requested",
  "last_updated_at": "ISO_TIMESTAMP"
}
```

---

## Bootstrap que o director entrega ao supervisor do S3

O director deve preparar um payload compatível com `s3.supervisor_bootstrap.v1`.

### Paths recomendados

- `sector_root = {run_root}/b2/sectors/s3_visual_planning`
- `source_package_path = {sector_root}/inputs/s3_source_package.json`
- `checkpoints_dir = {sector_root}/checkpoints`
- `operators_dir = {sector_root}/operators`
- `compiled_dir = {sector_root}/compiled`
- `logs_dir = {sector_root}/logs`
- `dispatch_dir = {sector_root}/dispatch`

---

## Fecho do S3

O supervisor do S3 deve:
1. validar bootstrap
2. despachar operators
3. validar outputs
4. compilar `compiled/compiled_entities.json`
5. gerar `compiled/s3_sector_report.md`
6. escrever checkpoint de sector

### Sucesso

```text
{b2_root}/checkpoints/s3_completed.json
```

### Falha

```text
{b2_root}/checkpoints/s3_failed.json
```

---

## Reentrada do director

Quando surgir `s3_completed.json` ou `s3_failed.json`, o director deve ser reactivado com `b2.resume.v1`.

### Se `reason = s3_completed`

O director deve:
1. ler `s3_completed.json`
2. validar existência de:
   - `compiled_entities.json`
   - `s3_sector_report.md`
3. actualizar `b2_state.json` com `completed_stages = ["s3"]`
4. como `mode = s3_only`, escrever `b2_completed.json`
5. marcar `status = completed`
6. terminar

### Se `reason = s3_failed`

O director deve:
1. ler `s3_failed.json`
2. actualizar `b2_state.json`
3. escrever `b2_failed.json`
4. marcar `status = failed`
5. terminar

---

## Simplificação explícita desta v1

Neste teste:
- o director não activa S4
- `next_stage` pode ficar `null`
- não há retry macro no bloco
- sucesso do bloco = sucesso utilizável do S3

---

## Critério de done desta etapa

Esta etapa está bem fechada quando já for possível dizer, sem ambiguidade:
- que ficheiros o director escreve no arranque
- que bootstrap o director entrega ao supervisor
- que checkpoint o supervisor devolve ao B2
- como o director fecha o bloco em `s3_only`
