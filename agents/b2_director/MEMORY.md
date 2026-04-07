# MEMORY.md — b2_director

## Runtime learnings

- The director must treat the disk as source of truth. Bootstrap/resume decisions depend on persisted files, not conversational context.
- `b2.bootstrap.v1` active bootstrap was proven in runtime real on 2026-04-03.
- Idempotent bootstrap/no-op behavior was also proven: if state is already correctly initialized, do not duplicate transitions.
- `b2.resume.v1` with `reason = s3_completed` was proven in runtime real: validate sector artifacts, update `b2_state.json`, and write `b2_completed.json` only after the files exist.
- Never invent completion just because a resume payload says `s3_completed`; always validate `compiled_entities.json` and `s3_sector_report.md` on disk.
- In `mode = s3_only`, correct success closure is macro block completion after validated S3 success.

## Operational checklist

1. Validate input contract.
2. Validate the relevant checkpoint files.
3. Read/write `b2_state.json` on disk.
4. Treat state transitions as explicit file-backed transitions.
5. Prefer no-op/idempotence over duplicate bootstrap.
