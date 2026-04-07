# S4 Contract — Supervisor Bootstrap Contract

## Objectivo

Este documento formaliza o contract canonico usado para activar o `sm_s4_asset_research`.

Ele define o que a boundary/workflow do S4 precisa entregar ao supervisor antes do sector comecar.

---

## Contract ID

- **name:** `s4.supervisor_bootstrap.v1`
- **producer:** boundary / `w3_block2.py`
- **consumer:** `sm_s4_asset_research`

---

## Funcao do contract

Este contract existe para garantir que o supervisor arranca com:

- identidade do job
- paths centrais do sector
- referencia explicita aos artefactos upstream (S3 compiled entities, sector report)
- estrutura minima de runtime ja criada
- contexto suficiente para validar o bootstrap sem depender de conversa residual

---

## Shape canonica

```json
{
  "kind": "s4_start",
  "contract_version": "s4.supervisor_bootstrap.v1",
  "job_id": "job_006_pt_guinle_001",
  "video_id": "video_abc123",
  "account_id": "006",
  "language": "pt-BR",
  "run_root": "C:/.../video_dir",
  "b2_root": "C:/.../video_dir/b2",
  "sector_root": "C:/.../video_dir/b2/sectors/s4_asset_research",
  "upstream": {
    "compiled_entities_path": "C:/.../video_dir/b2/sectors/s3_visual_planning/compiled/compiled_entities.json",
    "sector_report_path": "C:/.../video_dir/b2/sectors/s3_visual_planning/compiled/s3_sector_report.md"
  },
  "checkpoints_dir": "C:/.../video_dir/b2/sectors/s4_asset_research/checkpoints",
  "dispatch_dir": "C:/.../video_dir/b2/sectors/s4_asset_research/dispatch",
  "intake_dir": "C:/.../video_dir/b2/sectors/s4_asset_research/intake",
  "targets_dir": "C:/.../video_dir/b2/sectors/s4_asset_research/targets",
  "compiled_dir": "C:/.../video_dir/b2/sectors/s4_asset_research/compiled",
  "logs_dir": "C:/.../video_dir/b2/sectors/s4_asset_research/logs",
  "runtime_dir": "C:/.../video_dir/b2/sectors/s4_asset_research/runtime"
}
```

---

## Required fields

### Job identity

- `kind` = `s4_start`
- `contract_version`
- `job_id`
- `video_id`
- `account_id`
- `language`

### Runtime roots

- `run_root`
- `b2_root`
- `sector_root`

### Upstream references

- `upstream.compiled_entities_path`
- `upstream.sector_report_path`

### Sector directories

- `checkpoints_dir`
- `dispatch_dir`
- `intake_dir`
- `targets_dir`
- `compiled_dir`
- `logs_dir`
- `runtime_dir`

---

## Preconditions guaranteed by producer

Antes de activar o supervisor, o producer deste contract deve garantir que:

1. `run_root` existe
2. `b2_root` existe
3. `sector_root` existe
4. a estrutura minima do sector foi criada
5. `upstream.compiled_entities_path` existe e abre como JSON valido
6. `upstream.sector_report_path` existe (se presente)

---

## Bootstrap validation expected from supervisor

Ao acordar, o supervisor deve validar pelo menos:

1. `kind` correcto (`s4_start`)
2. `contract_version` suportada
3. todos os paths obrigatorios presentes
4. `upstream.compiled_entities_path` legivel
5. `checkpoints_dir`, `dispatch_dir`, `intake_dir`, `targets_dir`, `compiled_dir`, `logs_dir`, `runtime_dir` utilizaveis

Se alguma destas condicoes falhar, o supervisor deve falhar limpo e nao despachar operators.

---

## Success handoff to supervisor control plane

Depois de validar este contract, o supervisor deve:

1. assumir formalmente o sector
2. escrever artefacto de arranque do supervisor
3. criar directoria de targets
4. resolver batch manifest
5. preparar payloads de dispatch
6. invocar os operators activos

---

## Invariants

### 1. Boundary != supervisor
A boundary prepara e entrega o arranque. O supervisor assume o controlo interno do sector so depois de validar o bootstrap.

### 2. Estado no disco > estado conversacional
Todos os elementos criticos para o arranque do supervisor devem existir como artefactos/paths persistidos.

### 3. Falha explicita no arranque
Se o bootstrap estiver incompleto ou inconsistente, o supervisor deve falhar explicitamente.

---

## Out of scope

Este contract nao define:

- o contract de dispatch dos operators
- o registry dos operators
- a politica de retry do S4
- a shape final de `research_pack.json`
