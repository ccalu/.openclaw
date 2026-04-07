# S3 Contract — Supervisor Bootstrap Contract

## Objectivo

Este documento formaliza o contract canónico usado para activar o `sm_s3_visual_planning`.

Ele define o que a boundary/workflow do S3 precisa entregar ao supervisor antes do sector começar.

---

## Contract ID

- **name:** `s3.supervisor_bootstrap.v1`
- **producer:** workflow / boundary do S3
- **consumer:** `sm_s3_visual_planning`

---

## Função do contract

Este contract existe para garantir que o supervisor arranca com:

- identidade do job
- paths centrais do sector
- referência explícita ao source package
- estrutura mínima de runtime já criada
- contexto suficiente para validar o bootstrap sem depender de conversa residual

---

## Shape canónica

```json
{
  "kind": "s3_start",
  "contract_version": "s3.supervisor_bootstrap.v1",
  "job_id": "job_006_pt_guinle_001",
  "video_id": "video_abc123",
  "account_id": "006",
  "language": "pt-BR",
  "run_root": "C:/.../video_dir",
  "sector_root": "C:/.../video_dir/b2_s3_visual_planning",
  "source_package_path": "C:/.../video_dir/b2_s3_visual_planning/inputs/s3_source_package.json",
  "checkpoints_dir": "C:/.../video_dir/b2_s3_visual_planning/checkpoints",
  "operators_dir": "C:/.../video_dir/b2_s3_visual_planning/operators",
  "compiled_dir": "C:/.../video_dir/b2_s3_visual_planning/compiled",
  "logs_dir": "C:/.../video_dir/b2_s3_visual_planning/logs",
  "dispatch_dir": "C:/.../video_dir/b2_s3_visual_planning/dispatch",
  "bootstrap_checkpoint_path": "C:/.../video_dir/b2_s3_visual_planning/checkpoints/s3_bootstrap_ready.json"
}
```

---

## Required fields

### Job identity

- `kind` = `s3_start`
- `contract_version`
- `job_id`
- `video_id`
- `account_id`
- `language`

### Runtime roots

- `run_root`
- `sector_root`

### Core source

- `source_package_path`

### Sector directories

- `checkpoints_dir`
- `operators_dir`
- `compiled_dir`
- `logs_dir`
- `dispatch_dir`

### Bootstrap artifact

- `bootstrap_checkpoint_path`

---

## Preconditions guaranteed by producer

Antes de activar o supervisor, o producer deste contract deve garantir que:

1. `run_root` existe
2. `sector_root` existe
3. a estrutura mínima do sector foi criada
4. `source_package_path` existe
5. `source_package_path` abre como JSON válido
6. `bootstrap_checkpoint_path` foi escrito

---

## Bootstrap validation expected from supervisor

Ao acordar, o supervisor deve validar pelo menos:

1. `kind` correcto
2. `contract_version` suportada
3. todos os paths obrigatórios presentes
4. `source_package_path` legível
5. `checkpoints_dir`, `operators_dir`, `compiled_dir`, `logs_dir`, `dispatch_dir` utilizáveis

Se alguma destas condições falhar, o supervisor deve falhar limpo e não despachar operators.

---

## Success handoff to supervisor control plane

Depois de validar este contract, o supervisor deve:

1. assumir formalmente o sector
2. escrever artefacto de arranque do supervisor
3. resolver activation plan
4. preparar payloads de dispatch
5. invocar os operators activos

---

## Invariants

### 1. Boundary != supervisor
A boundary prepara e entrega o arranque. O supervisor assume o controlo interno do sector só depois de validar o bootstrap.

### 2. Estado no disco > estado conversacional
Todos os elementos críticos para o arranque do supervisor devem existir como artefactos/p paths persistidos.

### 3. Falha explícita no arranque
Se o bootstrap estiver incompleto ou inconsistente, o supervisor deve falhar explicitamente.

---

## Out of scope

Este contract não define:

- o contract de dispatch dos operators
- o registry dos operators
- a política de retry do S3
- a shape final de `compiled_entities.json`
