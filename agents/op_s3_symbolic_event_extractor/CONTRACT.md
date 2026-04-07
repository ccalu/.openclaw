# CONTRACT.md

## Input
Dispatch payload com `operator_name = symbolic_event_extractor` e paths de source/output/runtime válidos.

## Output mínimo
JSON com:
- `contract_version = s3.symbolic_event.output.v1`
- `operator_name = symbolic_event_extractor`
- `job_id`
- `status`
- `entities[]`
- `generated_at`
