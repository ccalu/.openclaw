# MEMORY.md — op_s3_human_subject_extractor

## Runtime learnings

- This operator was the first S3 operator to be proven with a real canonical output shape.
- Success means both: the agent ran and the final `output.json` matched the canonical schema.
- Do not rely on conversational summaries as proof; rely on `output.json`, `status.json`, and `checkpoint.json`.
- Fresh activation should still succeed using only dispatch + source package + runtime file paths.
