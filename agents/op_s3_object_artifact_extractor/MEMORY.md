# MEMORY.md — op_s3_object_artifact_extractor

## Runtime learnings

- The first failure was not extraction logic; it was missing dispatch generation.
- If `object_artifact_extractor_job.json` is absent, the operator fails explicitly and correctly.
- Dispatch existence and path correctness must be validated before blaming the operator itself.
- After regenerating the dispatch correctly, the operator completed and validated successfully.
