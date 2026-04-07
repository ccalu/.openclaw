# B2 — Minimal Runtime Contracts (v1)

## Objectivo

Este documento fecha a camada mínima de contracts operacionais do B2 necessária para ligar o `b2_director` ao S3 no primeiro teste S3-only.

---

## 1. Bootstrap contract do B2

### Contract id
- `b2.bootstrap.v1`

### Shape mínima
```json
{
  "kind": "b2_start",
  "contract_version": "b2.bootstrap.v1",
  "job_id": "job_006_pt_001",
  "run_root": "C:/.../run_root",
  "b2_root": "C:/.../run_root/b2",
  "account_id": "006",
  "language": "pt-BR",
  "inputs": {
    "screenplay_analysis_path": "..."
  },
  "mode": "s3_only"
}
```

---

## 2. Resume contract do B2 Director

### Contract id
- `b2.resume.v1`

### Shape mínima
```json
{
  "kind": "b2_resume",
  "contract_version": "b2.resume.v1",
  "run_root": "C:/.../run_root",
  "b2_root": "C:/.../run_root/b2",
  "reason": "s3_completed",
  "trigger_artifact": "C:/.../run_root/b2/checkpoints/s3_completed.json"
}
```

---

## 3. Checkpoint de request do S3

Quando o `b2_director` decide iniciar o S3, ele deve produzir:

```text
{b2_root}/checkpoints/s3_requested.json
```

### Shape mínima
```json
{
  "event": "s3_requested",
  "job_id": "job_006_pt_001",
  "sector": "s3_visual_planning",
  "requested_at": "ISO_TIMESTAMP",
  "supervisor_agent_id": "sm_s3_visual_planning",
  "mode": "s3_only"
}
```

---

## 4. Checkpoint de conclusão do S3

Quando o S3 fechar com sucesso utilizável, o supervisor deve produzir:

```text
{b2_root}/checkpoints/s3_completed.json
```

### Shape mínima
```json
{
  "event": "s3_completed",
  "job_id": "job_006_pt_001",
  "sector": "s3_visual_planning",
  "compiled_entities_path": "C:/.../compiled/compiled_entities.json",
  "sector_report_path": "C:/.../compiled/s3_sector_report.md",
  "completed_at": "ISO_TIMESTAMP",
  "status": "completed"
}
```

---

## 5. Checkpoint de falha do S3

```text
{b2_root}/checkpoints/s3_failed.json
```

### Shape mínima
```json
{
  "event": "s3_failed",
  "job_id": "job_006_pt_001",
  "sector": "s3_visual_planning",
  "failed_at": "ISO_TIMESTAMP",
  "status": "failed",
  "error": "short machine-readable summary"
}
```

---

## 6. Regra do primeiro teste

No primeiro teste S3-only:
- `b2_director` inicia S3
- S3 produz output canónico
- `b2_director` reconhece `s3_completed`
- o B2 escreve `b2_completed.json`
- o bloco pode parar aí
