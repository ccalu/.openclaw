# CONTEXT.md

## Sector
S3 — Visual Planning

## Upstream
- workflow/boundary do S3
- `b2_director`

## Downstream
- output canónico do sector em `compiled/compiled_entities.json`
- relatório humano em `compiled/s3_sector_report.md`
- checkpoint final do sector para consumo do B2

## Operators sob teu controlo
- `op_s3_human_subject_extractor`
- `op_s3_environment_location_extractor`
- `op_s3_object_artifact_extractor`
- `op_s3_symbolic_event_extractor`

## Fonte de verdade
- bootstrap contract do S3
- source package no disco
- contracts em `content_factory_block2/S3/contracts/`
- schemas em `content_factory_block2/S3/schemas/`
