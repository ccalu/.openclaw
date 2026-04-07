# CONTRACT.md

## Input
Dispatch payload com `operator_name = object_artifact_extractor` e paths de source/output/runtime válidos.

## Output mínimo
JSON com:
- `contract_version = s3.object_artifact.output.v1`
- `operator_name = object_artifact_extractor`
- `job_id`
- `status`
- `entities[]`
- `generated_at`
