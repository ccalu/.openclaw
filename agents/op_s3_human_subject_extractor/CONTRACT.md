# CONTRACT.md

## Input
Dispatch payload com:
- `contract_version = s3.operator_dispatch.v1`
- `operator_name = human_subject_extractor`
- `source_package.path`
- `output.output_path`
- `runtime.checkpoint_path`
- `runtime.status_path`
- `runtime.log_path`
- `operator_payload`

## Output mínimo
JSON com:
- `contract_version = s3.human_subject.output.v1`
- `operator_name = human_subject_extractor`
- `job_id`
- `status`
- `entities[]`
- `generated_at`

## Success rule
O job só está concluído quando o ficheiro final existir no path pedido.
