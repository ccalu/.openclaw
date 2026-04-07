# MEMORY.md — op_s3_symbolic_event_extractor

## Runtime learnings

- This operator initially wrote a non-canonical shape and needed explicit reinforcement to emit `entities[]` plus the canonical top-level fields.
- As with the environment operator, runtime success is not enough; schema conformance is mandatory.
- Keep auxiliary structures like `symbolic_events` only as optional extras, never as the primary replacement for canonical `entities[]`.
- Contract alignment was corrected and revalidated successfully on 2026-04-03.
