# MEMORY.md — op_s3_environment_location_extractor

## Runtime learnings

- This operator initially executed but wrote an older output shape (`locations`, `environments`, `settings`) instead of the canonical `entities[]`-first schema.
- Runtime success is not enough; output must be normalized to `s3.environment_location.output.v1`.
- Auxiliary structures may remain, but they cannot replace:
  - `operator_name`
  - `entities[]`
  - `generated_at`
  - canonical `status`
- Contract alignment was corrected on 2026-04-03 and revalidated successfully.
