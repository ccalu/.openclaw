# Sector Preflight Checklist

Use this before opening any new Block 2 sector (S4, S5, S6, or future sub-sectors).

The goal is to prevent repeating the exact class of mistakes we hit during the first B2/S3 runtime validation cycle.

---

## A. Runtime materialization

- [ ] Every required agent is **really** materialized in OpenClaw runtime
- [ ] Every required agent appears in `openclaw agents list`
- [ ] Every required agent can execute at least one real turn
- [ ] No sector is considered "real" based only on folders/docs existing

---

## B. Contract freezing

- [ ] Canonical input contract exists
- [ ] Canonical output contract exists
- [ ] Dispatch contract exists
- [ ] Resume/reentry contract exists where applicable
- [ ] Schema files exist for all outputs that matter
- [ ] Version names are aligned (`v1` vs `v2`, etc.)

---

## C. Invocation primitive

- [ ] The exact supervisor -> operator invocation primitive is frozen
- [ ] The primitive is proven in this environment
- [ ] No ambiguous fallback path remains as the default
- [ ] If ACP is mentioned, its role is explicit and non-assumed

### Current B2 default lesson
For the current environment, do **not** assume ACP as the default orchestration primitive.
Prefer the proven path:

```text
exec -> openclaw agent --agent <agent_id> --message "..." --json
```

---

## D. Dispatch integrity

- [ ] Every operator dispatch file is generated
- [ ] Every dispatch path matches the operator expectation
- [ ] `operator_name` matches the actual target operator
- [ ] `output.output_path` matches the intended runtime location
- [ ] Schema id / expected schema matches the operator contract

---

## E. Operator validation

- [ ] Each operator has been run at least once for real
- [ ] Runtime success is proven by files, not by conversation alone
- [ ] Each operator output was validated against the current canonical schema
- [ ] Any legacy output shapes have been normalized or explicitly forbidden
- [ ] `status.json` and `checkpoint.json` are written honestly

---

## F. Supervisor validation

- [ ] Supervisor reads bootstrap from disk correctly
- [ ] Supervisor writes activation plan correctly
- [ ] Supervisor writes dispatches correctly
- [ ] Supervisor validates operator artifacts on disk
- [ ] Supervisor compile/report/checkpoints are based on real files
- [ ] Disk artifacts match what the supervisor claims in chat

---

## G. Director / block control-plane validation

- [ ] Block director active bootstrap is proven
- [ ] Block director idempotent/no-op bootstrap is proven
- [ ] Block director resume-success path is proven
- [ ] Block director resume-failure path is proven (or explicitly deferred)
- [ ] `state.json` mutations are verified on disk
- [ ] Macro completion/failure checkpoints are verified on disk

---

## H. Truth model

- [ ] Disk is treated as source of truth
- [ ] Agent conversational summaries are treated as secondary evidence only
- [ ] No completion is accepted without actual persisted artifacts
- [ ] `degraded_completed` meaning is explicitly classified:
  - [ ] degraded because runtime failed
  - [ ] degraded because test scope intentionally ran a subset

---

## I. Production-mode realism

- [ ] Tests are not relying on residual session memory as hidden glue
- [ ] Activations are contract-complete and file-driven
- [ ] The sector can tolerate fresh activation behavior
- [ ] The sector does not depend on thread-bound session mythology

---

## J. Paperclip / Perseus readiness gate

Do **not** let Paperclip rely on a new sector until all of the following are true:

- [ ] Director path proven enough for the intended scope
- [ ] Supervisor path proven enough for the intended scope
- [ ] Required operators proven enough for the intended scope
- [ ] Remaining degradation is test-scope only, not infra/runtime failure
- [ ] Checkpoint/reentry loop is clear and operational

---

## Exit question

Before opening the next sector, answer this honestly:

> If this sector fails tomorrow, will we know whether it failed because of runtime, dispatch, contract, state transition, or model behavior?

If the answer is **no**, the sector is not preflighted yet.
