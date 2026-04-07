# CONTRACT.md

## Input
Dispatch payload com `operator_name = environment_location_extractor` e paths de source/output/runtime válidos.

## Output mínimo
JSON com:
- `contract_version = s3.environment_location.output.v1`
- `operator_name = environment_location_extractor`
- `job_id`
- `status`
- `entities[]`
- `generated_at`
