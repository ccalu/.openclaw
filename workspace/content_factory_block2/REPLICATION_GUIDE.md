# Replication Guide for Future Block 2 Sectors

## Purpose

Use this document to replicate the validated S3 pattern in future sectors (S4, S5, S6) without re-living the same weeks of debugging.

---

## Canonical control pattern

```text
boundary workflow
  -> b2_director
    -> {sector}_requested.json
  -> boundary observes requested checkpoint
    -> builds sector bootstrap + sector source package
    -> invokes sector supervisor
  -> sector supervisor
    -> activation plan
    -> dispatches
    -> operator launches via CLI
    -> output validation
    -> compile/report
    -> sector macro checkpoint
  -> boundary observes sector macro checkpoint
    -> builds b2.resume.v1
    -> reinvokes b2_director
```

---

## Mandatory rules for a new sector

### 1. Runtime materialization
- Every agent must appear in `openclaw agents list`
- Every agent must execute at least one real turn

### 2. Contracts first
Before real tests:
- bootstrap contract
- resume contract (when applicable)
- supervisor bootstrap contract
- operator dispatch contract
- output schemas
- macro checkpoint shape

### 3. Invocation primitive
For the current environment, default to:

```text
exec -> openclaw agent --agent <id> --session-id <unique-run-session> --message "..." --json --timeout 1800
```

Do not assume ACP as default orchestration substrate.

### 4. Session hygiene
- unique `--session-id` per run/stage
- unique `--session-id` per operator launch
- do not rely on default CLI session reuse

### 5. Truth model
- disk artifacts are source of truth
- chat summaries are secondary

### 6. Path handling
- paths from bootstrap are literal and canonical
- no Unicode-normalization heuristics
- no alternate root discovery

### 7. Macro checkpointing
A sector must mirror macro status into:

```text
{b2_root}/checkpoints/{sector}_completed.json
{b2_root}/checkpoints/{sector}_failed.json
```

### 8. Director validation
The director must validate the paths declared by the sector checkpoint, not assume root-level hardcoded artifacts.

---

## Checklist before opening a new sector

- [ ] director contract for this sector exists
- [ ] supervisor contract exists
- [ ] operator registry is closed and explicit
- [ ] output schemas exist
- [ ] every operator can run once in runtime real
- [ ] supervisor can launch operators via CLI
- [ ] sector compile/report exists
- [ ] sector macro checkpoint exists
- [ ] director resume path for this sector is proven

---

## What not to do again

- do not treat ACP as the default answer
- do not call folder-only agents “ready”
- do not trust chat summaries over disk
- do not allow the supervisor to absorb operator semantic work internally
- do not accept legacy/non-canonical output shapes as “good enough”
- do not let boundary code work around a broken agent contract if the contract can be fixed at the source
