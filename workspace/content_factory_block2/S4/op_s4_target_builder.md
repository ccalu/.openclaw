# op_s4_target_builder

**STATUS: DEPRECATED**

_Last updated: 2026-04-06_
_Actor type: operator (DEPRECATED)_
_Sector: S4 — Asset Research_

---

## Deprecation Notice

This OpenClaw actor has been **replaced by helper-direct** invocation of `target_builder.py` from `supervisor_shell.py`.

**Reason for deprecation:** The LLM actor consistently invented its own logic instead of calling the Python helper, leading to unreliable intake generation and schema drift.

**Replacement:** `supervisor_shell.py` calls `target_builder.py` directly as a Python subprocess. The helper uses GPT-5.4-nano (OpenAI API) for the LLM consolidation step and performs all other logic deterministically.

**Current architecture:** See `S4_ARCHITECTURE_V2.md` for the full V3 pipeline.

---

## Original role (for reference)

`op_s4_target_builder` was the first operator of S4, responsible for transforming S3 compiled entities into the canonical S4 intake (`research_intake.json` + `target_builder_report.md`).

This work is now performed by `target_builder.py` with the following improvements:
- Deterministic pre-pass (normalize, detect overlaps)
- LLM consolidation (GPT-5.4-nano) for merging overlapping entities, contextualizing labels, and classifying searchability
- Deterministic validation (provenance, schema enforcement)
- Target consolidation (fewer targets, better labels, non-retrievable entities skipped)

---

## Agent workspace

The agent workspace at `~/.openclaw/agents/op_s4_target_builder/` is retained but not activated. Sessions are cleaned before each S4 run for safety.
