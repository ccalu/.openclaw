---
name: block2-new-sector
description: Plan and implement a new Block 2 sector (such as S4, S5, S6, or a future visual-production sector) using the validated S3 pattern. Use when opening a new Block 2 sector from scratch, defining its architecture/contracts/schemas/supervisor/operators/runtime layout, materializing the corresponding OpenClaw agents, validating them in runtime real, and preparing the sector for Paperclip/Perseus integration without repeating the failures from S3.
---

# Block 2 New Sector

Follow this skill whenever starting a new Block 2 sector.

This is a **two-phase skill**:
1. **Planning** — define the sector correctly before implementing
2. **Execution** — materialize, validate, and harden the sector in runtime real

Use the validated S3 pattern as the baseline, not as loose inspiration.

---

## Primary references to load when needed

Read these central references before or during the work when relevant:

- `C:\Users\User-OEM\.openclaw\workspace\content_factory_block2\B2_runtime_control_flow.md`
- `C:\Users\User-OEM\.openclaw\workspace\content_factory_block2\POSTMORTEM_AND_LEARNINGS_2026-04-03.md`
- `C:\Users\User-OEM\.openclaw\workspace\content_factory_block2\S3_POSTMORTEM_AND_PATTERNS.md`
- `C:\Users\User-OEM\.openclaw\workspace\content_factory_block2\CONTRACTS_REGISTRY.md`
- `C:\Users\User-OEM\.openclaw\workspace\content_factory_block2\REPLICATION_GUIDE.md`
- `C:\Users\User-OEM\.openclaw\workspace\content_factory_block2\SECTOR_PREFLIGHT_CHECKLIST.md`
- `C:\Users\User-OEM\.openclaw\workspace\content_factory_block2\S3\` docs as the canonical example set

If Claude Code has already produced Paperclip-side integration docs for the same cycle (for example `docs/openclaw_integration.md` in the Auto Content Factory repo), read them too to keep both sides of the boundary aligned.

---

# PHASE 1 — PLANNING THE SECTOR

Do not jump into agent creation before this phase is structurally clear.

## 1. Define the sector architecturally

For the new sector, explicitly define:

- what the sector does
- what the sector does **not** do
- what comes from the previous sector
- what goes to the next sector
- what belongs to the boundary workflow
- what belongs to `b2_director`
- what belongs to the sector supervisor
- what belongs to operators

Use the Block 2 layering explicitly:

```text
boundary workflow -> b2_director -> sector supervisor -> operators
```

Do not blur these layers.

### Planning rule
Prefer **rich taxonomy, stable operators**:
- many semantic families can exist
- the number of operators should remain deliberately small and stable when possible

---

## 2. Define inputs and outputs

Write down the sector’s:

- upstream inputs
- internal substrate artifacts
- operator outputs
- compiled sector outputs
- macro completion checkpoint

Clarify:
- which upstream artifact is the sector source of truth
- which compiled artifact the next stage will consume
- which report/checkpoint artifacts must exist for the director to resume

---

## 3. Define contracts and schemas

Before implementation, freeze the following:

### Required contracts
- supervisor bootstrap contract
- operator dispatch contract
- sector completion checkpoint contract (`{sector}_completed.json`)
- sector failure checkpoint contract (`{sector}_failed.json`)
- any director resume implications

### Required schemas
- one output schema per operator
- one compiled schema for the sector

### Registration rule
Register every validated contract in:
- `content_factory_block2/CONTRACTS_REGISTRY.md`

Do not leave contract shapes floating only inside chat or ad-hoc code.

---

## 4. Design the supervisor

Design the supervisor around the validated 5-phase startup pattern:

1. validate bootstrap
2. assume sector
3. resolve activation plan
4. write plan
5. prepare dispatches

Then define:
- how it invokes operators
- how it validates outputs
- how it compiles the sector
- how it writes the internal checkpoint
- how it mirrors the macro block checkpoint

### Mandatory supervisor rules
For the current environment, the supervisor must treat this as canonical:

```text
exec -> openclaw agent --agent <operator_id> --session-id <unique-run-operator-session> --message "..." --json --timeout 1800
```

Rules:
- do not use ACP/sessions_spawn as primary orchestration path
- do not silently collapse 4 planned operators into 1
- do not absorb operator work internally as a substitute for dispatch
- do not invent parallel taxonomies that replace canonical operator outputs
- use only the paths declared in the bootstrap/dispatch
- write the macro checkpoint into `b2/checkpoints/`

### Success criteria
Define exactly what must exist on disk before the sector counts as completed.
At minimum this usually includes:
- sector compiled artifact
- sector report artifact
- sector internal final checkpoint
- sector macro block checkpoint

---

## 5. Design the operators

For each operator, define:

- role
- semantic scope
- dispatch input
- output schema
- runtime paths used
- error behavior
- validation rule for a successful output

### Operator rule
A successful operator means **both**:
- the operator ran
- its output matches the current canonical schema

A written file alone is not enough.

---

## 6. Design the director integration

Define exactly how the director will interact with this sector.

### Request side
Define:
- `{sector}_requested.json`
- when the director writes it
- which fields it contains

### Completion side
Define:
- `{sector}_completed.json`
- required absolute artifact paths (for example `compiled_entities_path`, `sector_report_path`)
- what the director validates when it resumes

### Resume side
Define how `b2.resume.v1` should be used for:
- `{sector}_completed`
- `{sector}_failed`

### Director rule
The director must validate the paths declared in the sector checkpoint.
It must not assume hardcoded artifact locations in the root of `b2/`.

---

## 7. Define the runtime layout

Create or confirm the sector layout under:

```text
{b2_root}/sectors/{sector_name}/
  inputs/
  dispatch/
  operators/{operator_name}/
  compiled/
  checkpoints/
  logs/
```

Keep file naming explicit and stable.

---

# PHASE 2 — EXECUTION / IMPLEMENTATION

Do not skip runtime materialization and real validation.

## 8. Create the OpenClaw agents

For the sector supervisor and all operators:

- create the agent directory in `.openclaw/agents/{agent_id}/`
- ensure agent bootstrap files exist as needed
- write/update at least:
  - `IDENTITY.md`
  - `SOUL.md`
  - `AGENTS.md`
  - `TOOLS.md`
  - `CONTRACT.md`
  - `OPERATIONS.md`
  - `MISSION.md`

### Mandatory content rules for those docs
The docs must make explicit where relevant:
- CLI is the invocation primitive, not ACP/sessions_spawn for this hop
- `--session-id` is unique per run/operator
- `--timeout 1800` is explicit for operator launches
- agents write only to bootstrap/dispatch-declared paths
- no references to `auto_content_factory_legacy`
- macro checkpoint must be mirrored in `b2/checkpoints/`

Do not turn these docs into giant system-wide troubleshooting dumps. Keep them scoped to the agent’s actual role.

---

## 9. Materialize the agents in runtime real

Do not stop at folders/docs.

The agents only count as real when:
- they appear in `openclaw agents list`
- they execute a real turn

This is mandatory.

---

## 10. Apply the S3 lessons before testing

These are **not optional**. Apply them by default.

### Lesson: ACP/sessions_spawn is not the default orchestration primitive
Use CLI.

### Lesson: session accumulation is real
Use unique `--session-id` per run and per operator.
Boundary workflows should clean/re-segment sessions before each run when needed.
Agents must not rely on prior session context.

### Lesson: supervisors may try to do operator work internally
Explicitly forbid this in the supervisor docs.

### Lesson: path drift is fatal
Use only bootstrap/dispatch-declared paths.
Do not derive paths heuristically or normalize Unicode lookalikes.

### Lesson: operator output shape can drift
Define precise schemas and validate them before compile.

### Lesson: macro checkpoints are mandatory
Do not let a sector close without mirroring `{sector}_completed.json` or `{sector}_failed.json` in `b2/checkpoints/`.

### Lesson: compiled artifact paths must live in the completion checkpoint
The director should resume from checkpoint-declared paths, not from guessed root-level filenames.

### Lesson: sector report is mandatory
The sector does not count as completed without the required report artifact.

### Lesson: timeout cascades are real
Use `--timeout 1800` explicitly for supervisor -> operator CLI launches.
Boundary workflows should prefer fire-and-forget launch + checkpoint polling instead of blocking kill-prone subprocess waits.

### Lesson: `degraded_completed` is not acceptable as the target state for validated sector closure
For real closure, prefer:
- `completed`
- or `failed`

Only use degraded semantics when the test scope explicitly and intentionally ran a subset, and document that fact clearly.

---

## 11. Run the validation ladder

Before calling the sector ready for E2E, validate in this order:

### A. Agent registration
- every agent exists in runtime

### B. Operator isolated tests
- each operator runs once by manual CLI invoke
- each output validates against schema

### C. Supervisor isolated test
- supervisor reads bootstrap
- writes activation plan and dispatches
- launches operators correctly
- validates artifacts
- compiles sector outputs
- writes macro checkpoint

### D. Director integration test
- director writes `{sector}_requested.json`
- director resume validates `{sector}_completed.json`

### E. Narrow E2E test
- boundary -> director -> supervisor -> operators -> macro checkpoint -> director resume -> block checkpoint

---

## 12. Use the pre-deploy gate

Before declaring a new sector ready for E2E, ensure at least:

- [ ] all agents exist in `openclaw agents list`
- [ ] all required docs exist
- [ ] no docs reference `auto_content_factory_legacy`
- [ ] CLI dispatch pattern is explicit with `--session-id` and `--timeout 1800`
- [ ] output schemas exist
- [ ] macro checkpoint shape includes absolute artifact paths
- [ ] sector report is mandatory and documented
- [ ] supervisor is explicitly forbidden from replacing operator dispatch with internal semantic work
- [ ] supervisor is explicitly restricted to bootstrap paths
- [ ] each operator was tested in isolation
- [ ] supervisor was tested in isolation
- [ ] narrow E2E was tested

Also use:
- `content_factory_block2/SECTOR_PREFLIGHT_CHECKLIST.md`

---

## 13. Handoff to Claude Code / Paperclip

When the sector is ready for integration, provide:
- list of real `agent_id`s
- bootstrap shape
- dispatch shape
- completion checkpoint shape
- expected artifact paths
- any special runtime constraints

Make the handoff explicit and concrete. Do not force the boundary to reverse-engineer the sector contract from agent behavior.

---

## 14. Quality bar

Document and implement the sector so that someone who never saw the S3 calvary can:
1. understand the role of the sector
2. understand what contracts exist
3. understand how it runs
4. understand how it signals completion/failure
5. replicate the pattern without rediscovering the same runtime mistakes

If that is not true, the sector is not ready.
