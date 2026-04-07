# Contracts Registry — Block 2 / S3-only validated set

## Purpose

Single place for the contracts that were actually validated in the first working S3-only E2E.

---

## 1. `b2.bootstrap.v1`

### Purpose
Activate the B2 director for block bootstrap.

### Required shape
```json
{
  "kind": "b2_start",
  "contract_version": "b2.bootstrap.v1",
  "job_id": "string",
  "run_root": "string",
  "b2_root": "string",
  "account_id": "string",
  "language": "string",
  "inputs": {
    "screenplay_analysis_path": "string"
  },
  "mode": "s3_only"
}
```

---

## 2. `b2.resume.v1`

### Purpose
Reactivate the B2 director after a sector event.

### Required shape
```json
{
  "kind": "b2_resume",
  "contract_version": "b2.resume.v1",
  "run_root": "string",
  "b2_root": "string",
  "reason": "s3_completed | s3_failed",
  "trigger_artifact": "string"
}
```

---

## 3. `s3.supervisor_bootstrap.v1`

### Purpose
Activate the S3 supervisor with all sector-local runtime roots.

### Required fields
- `kind = s3_start`
- `contract_version`
- `job_id`
- `video_id`
- `account_id`
- `language`
- `run_root`
- `sector_root`
- `source_package_path`
- `checkpoints_dir`
- `operators_dir`
- `compiled_dir`
- `logs_dir`
- `dispatch_dir`
- `bootstrap_checkpoint_path`

---

## 4. `s3.operator_dispatch.v1`

### Purpose
Give one operator its run-specific execution envelope.

### Required top-level areas
- execution identity
- business/job identity
- semantic context
- source package path
- output path + expected schema
- runtime paths
- execution policy
- operator-specific payload

---

## 5. `s3_completed.json`

### Purpose
Macro block checkpoint signaling that S3 finished successfully enough for the director to resume.

### Required shape
```json
{
  "event": "s3_completed",
  "job_id": "string",
  "sector": "s3_visual_planning",
  "compiled_entities_path": "string",
  "sector_report_path": "string",
  "completed_at": "ISO_TIMESTAMP",
  "status": "completed"
}
```

### Important rule
The paths declared here are the source of truth for the director resume validation.

---

## 6. `b2_completed.json`

### Purpose
Macro block completion artifact for the first S3-only narrow proof.

### Required shape
```json
{
  "event": "b2_completed",
  "job_id": "string",
  "mode": "s3_only",
  "completed_at": "ISO_TIMESTAMP",
  "compiled_entities_path": "string",
  "sector_report_path": "string"
}
```

---

## Practical note
These contracts are the validated baseline for future sectors. Extend carefully; do not fork them casually by improvisation in prompts or chat summaries.
