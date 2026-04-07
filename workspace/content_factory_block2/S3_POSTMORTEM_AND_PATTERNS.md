# S3 Postmortem and Patterns

## Objective

Capture the exact troubleshooting path that took S3 from architecture-on-paper to a real end-to-end S3-only B2 run through Paperclip + OpenClaw.

This document exists to make S4/S5/S6 dramatically cheaper to open.

---

## Final validated pattern

The validated narrow pattern is now:

```text
Paperclip / w3_block2.py
  -> b2_director (bootstrap)
    -> writes b2_bootstrap_ready.json + s3_requested.json
  -> w3_block2.py observes s3_requested.json
    -> builds s3_source_package.json + s3_supervisor_bootstrap.json
    -> invokes sm_s3_visual_planning
  -> sm_s3_visual_planning
    -> generates activation plan
    -> writes dispatches
    -> invokes 4 canonical operators via CLI
    -> validates operator outputs on disk
    -> compiles compiled_entities.json
    -> generates s3_sector_report.md
    -> writes s3_completed.json in b2/checkpoints/
  -> w3_block2.py observes s3_completed.json
    -> builds b2.resume.v1
    -> invokes b2_director
  -> b2_director validates sector artifacts from the checkpoint paths
    -> writes b2_completed.json
```

---

## What failed and how it was resolved

### 1. ACP / sessions_spawn as if they were the sector runtime substrate

**Problem**
We repeatedly treated ACP or sessions_spawn-like paths as if they were the correct core substrate for `supervisor -> operator` orchestration.

**Reality**
For this environment, the working primitive is:

```text
exec -> openclaw agent --agent <operator_id> --session-id <...> --message "..." --json --timeout 1800
```

**Resolution**
Supervisor docs and contracts were hardened to treat CLI launch as canonical and ACP as non-primary for this hop.

---

### 2. Agent folder != real agent

**Problem**
At first, agent folders/docs were treated too loosely as if they already meant runtime-ready agents.

**Reality**
An agent only counts as materialized when:
- it appears in `openclaw agents list`
- it executes a real turn

**Resolution**
All B2/S3 agents were properly materialized and then validated in runtime real.

---

### 3. Chat summaries were over-trusted

**Problem**
Agents sometimes claimed files or progress that did not exactly match the filesystem.

**Reality**
Disk is the source of truth. Chat summaries are secondary.

**Resolution**
Validation shifted fully to checkpoints, output files, compiled files, and macro block checkpoints.

---

### 4. Operators could run while still violating the contract

**Problem**
Some operators executed but wrote legacy/non-canonical output shapes.

**Examples**
- environment operator initially wrote `locations/environments/settings`
- symbolic operator initially wrote non-canonical shapes
- object operator initially failed because dispatch did not exist

**Resolution**
Operators were re-instructed to normalize outputs to canonical schemas, and dispatch generation became a first-class validation target.

---

### 5. Session accumulation / context bleed

**Problem**
Repeated `openclaw agent --agent ...` calls reuse sessions by default, which risks context accumulation across videos and unnecessary token burn.

**Resolution**
The pattern now requires unique `--session-id` per run/stage and per operator launch.

---

### 6. Boundary subprocess timeouts killed the chain

**Problem**
Blocking subprocess patterns in the Paperclip boundary risked killing the whole chain by timeout.

**Resolution**
Boundary behavior must be:
- fire-and-forget launch
- checkpoint polling
- no blocking wait that kills child work by timeout

---

### 7. Supervisor path drift and checkpoint drift

**Problems**
- supervisor regressed to ACP / subset execution
- supervisor failed to mirror macro checkpoint to `b2/checkpoints/`
- supervisor drifted on path handling (`—` vs `-`)
- supervisor absorbed operator work internally instead of dispatching all canonical operators

**Resolution**
Supervisor was hardened to:
- use CLI with `--session-id` and `--timeout 1800`
- obey a closed 4-operator registry
- avoid silent subset fallback
- avoid internal semantic substitution for operator work
- write macro block checkpoints
- treat bootstrap paths as literal/canonical

---

### 8. Director resume path initially assumed wrong artifact locations

**Problem**
The director was at risk of assuming compiled artifacts at the root of `b2/` instead of validating paths declared in `s3_completed.json`.

**Resolution**
The correct contract is now explicit:
- sector artifacts live in `b2/sectors/s3_visual_planning/compiled/`
- the macro checkpoint points to them
- the director must validate the paths declared in `s3_completed.json`

---

## Final rules extracted from this cycle

### Rule 1
State machine + checkpoints is the correct control model.

### Rule 2
Disk > chat.

### Rule 3
CLI > ACP for current supervisor -> operator orchestration.

### Rule 4
Fresh run hygiene matters. Use unique session ids per run/stage/operator.

### Rule 5
Do not accept internal semantic substitution in place of operator dispatch.

### Rule 6
Do not let Paperclip work around broken OpenClaw contracts. Fix the contract at the source.

---

## What future sectors must inherit

Every future sector (S4/S5/S6) should inherit:
- closed operator registry
- canonical dispatch contract
- canonical output schemas
- CLI launch primitive with session-id and timeout
- macro block checkpoints
- sector-local compiled artifacts + checkpoint-declared paths
- no internal semantic shortcutting by the supervisor
