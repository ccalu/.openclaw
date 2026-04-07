# Block 2 / S3 — Postmortem and Learnings (2026-04-03)

## Objective

Capture the real problems encountered while materializing and validating the first executable slice of Block 2 (`b2_director -> S3`) so future sectors do not repeat the same mistakes.

This file is intentionally blunt. It records what failed, why it failed, what was corrected, and what should become policy going forward.

---

## 1. The main architectural lesson

### What we kept bumping into
We repeatedly tried to validate multi-agent behavior through mechanisms that looked plausible in docs or chat intuition, but were not the correct runtime substrate for this environment.

### What turned out to be correct
For Block 2 in the current environment, the right model is:

- persisted state on disk
- checkpoint-driven progress
- discrete activations
- fresh-context behavior per activation
- workflow truth in files, not conversation

### Consequence
Future sectors should start from a **state-machine mindset**, not a “persistent conversational orchestrator” mindset.

---

## 2. False blocker: ACP as if it were the orchestration substrate

### What happened
ACP kept appearing as a blocker when trying to prove `supervisor -> operator` launches.

### What we discovered
ACP was **not** the right central runtime for this workflow. The actual viable primitive in this environment is:

```text
exec -> openclaw agent --agent <agent_id> --message "..." --json
```

### Correction applied
We stopped treating ACP as the required execution substrate for S3 orchestration and hard-pinned the supervisor-side runtime path to the CLI primitive above.

### Policy going forward
- Do not default to ACP for workflow orchestration.
- Treat ACP as optional/auxiliary, not foundational, unless a future sector proves otherwise.
- First ask: “what is the file/checkpoint-driven primitive?”

---

## 3. Big confusion source: "agent exists" vs "agent is operationally materialized"

### What happened
At first, creating folders and docs for agents was treated too loosely as if the agents already existed in runtime.

### What was actually true
A folder under `~/.openclaw/agents/<id>/` is **not enough**.
An agent only really exists operationally once it is materialized in the OpenClaw runtime and appears in:

```text
openclaw agents list
```

### Correction applied
All B2/S3 agents were materialized properly via OpenClaw agent registration.
This especially mattered for `b2_director`, which at one point still returned:

```text
Unknown agent id "b2_director"
```

### Policy going forward
Before claiming a sector/agent is real, verify:
1. it appears in `openclaw agents list`
2. it is invokable
3. it can execute a real turn

---

## 4. The disk is the source of truth — agent chat summaries are not

### What happened
Several agents verbally claimed success, artifact creation, or behavior that did not perfectly match what existed on disk.

### What we discovered
Agent conversational summaries are useful, but **not trustworthy enough as operational truth**.

### Correction applied
Validation was anchored in files only:
- checkpoints
- output JSONs
- compiled artifacts
- status files
- checkpoint files

### Policy going forward
For every future sector:
- trust the disk first
- trust agent summaries second
- if there is a conflict, the disk wins

---

## 5. The decisive runtime primitive for supervisor -> operator was found

### What happened
We spent too long validating operator behavior without freezing the correct invocation path.

### What finally worked
This path:

```text
exec -> openclaw agent --agent <operator_id> --message "...dispatch path..." --json
```

### Why this mattered
It proved that nested launch did not actually require ACP in the way we had been assuming.

### Policy going forward
Future supervisors should have their operator-launch primitive frozen early.
Do not leave this ambiguous while designing contracts.

---

## 6. Narrow degraded runs are not necessarily runtime failures

### What happened
Several validation runs ended as `degraded_completed`.
At first this risked being interpreted too loosely.

### What we clarified
In narrow validation runs, `degraded_completed` can mean two very different things:

1. **bad degraded** — launch/runtime path failed
2. **acceptable degraded** — only one operator was intentionally run, so compile is incomplete by design

### Correction applied
We separated these cases explicitly.

### Policy going forward
Always distinguish:
- degraded because the runtime failed
- degraded because the test intentionally ran a subset

These are not the same operationally.

---

## 7. Operators can run while still violating the contract

### What happened
Some S3 operators were able to execute and write files, but their output shape still violated the current sector schema.

### Cases observed
- `environment_location_extractor`
  - executed
  - wrote output
  - but initially used an older shape (`locations`, `environments`, `settings`, etc.) instead of canonical `entities[]`
- `symbolic_event_extractor`
  - executed
  - but initially emitted an older/non-canonical structure
- `object_artifact_extractor`
  - initially failed because dispatch was missing

### Correction applied
Operator operational instructions were tightened so they explicitly normalize outputs into the canonical schema.

### Policy going forward
A successful operator run means **both**:
1. the agent ran
2. the written output matches the current canonical contract

“Agent responded” or “file exists” is insufficient.

---

## 8. Dispatch generation must be treated as a first-class validation target

### What happened
`object_artifact_extractor` failed not because its extraction logic was wrong, but because the dispatch file was missing.

### Lesson
Dispatch generation is part of the runtime substrate, not a side detail.
If dispatch generation is wrong, the operator layer fails regardless of agent quality.

### Policy going forward
Every future sector should validate, per operator:
- dispatch exists
- path is correct
- operator name matches
- output path matches
- schema id matches

before testing the operator itself.

---

## 9. The `b2_director` is now materially proven in the right ways

### What got proven
The following are now real, not just documented:

- `b2_director` is registered in runtime
- active bootstrap behavior was proven
- idempotent bootstrap/no-op behavior was proven
- resume on `s3_completed` was proven
- `b2_completed.json` can be written correctly in `s3_only`

### Why this matters
This means the B2 control plane is no longer theoretical. The remaining uncertainty moved mainly into supervisor-side operator orchestration.

### Policy going forward
Future block directors should be validated in this order:
1. registration
2. active bootstrap
3. idempotent bootstrap
4. resume-success
5. resume-failure

---

## 10. Fresh activation matters — but file-driven freshness matters more than session mythology

### What happened
A critical concern emerged: if production will activate agents in fresh sessions, then validations that rely on session continuity could mislead us.

### What we clarified
The important thing is not “new session” as a mystical property.
The important thing is that each activation behaves correctly with:
- persisted dispatch
- persisted source package
- persisted checkpoints
- no reliance on residual conversation state

### Policy going forward
For future sectors, define freshness operationally as:
- file-driven activation
- contract-complete activation
- no dependency on prior chat memory

That is more important than the exact session ID mechanics.

---

## 11. Main blockers we actually had (not the ones we imagined)

### Real blockers encountered
- agent not really registered in runtime
- wrong/ambiguous invocation primitive
- supervisor drifting into ACP fallback
- operators writing legacy schema shapes
- missing dispatch files
- trusting chat summaries too much

### Fake / overstated blockers
- “the whole architecture is impossible without ACP”
- “if one narrow run is degraded the system is not viable”
- “folder exists = agent exists”

---

## 12. What should become standard for the next sectors (S4/S5/S6)

### Before creating any agent
- define canonical input contract
- define canonical output contract
- define dispatch contract
- define exact invocation primitive
- define which files are the source of truth

### Before saying a sector is runnable
- materialize all agents in runtime
- prove one active bootstrap
- prove one operator run per operator type
- validate outputs against schemas
- validate supervisor compile/report/checkpoints from real artifacts

### Before letting Paperclip rely on a sector
- prove the block director
- prove the sector supervisor
- prove at least one honest end-to-end narrow path
- ensure all remaining degradation is test-scope, not infra/runtime failure

---

## 13. Practical checklist for next sectors

### Never again assume
- ACP is the default solution
- agent summary = truth
- folder = agent
- output file = valid output
- degraded = same thing in all contexts

### Always verify
- runtime registration
- dispatch existence
- output schema
- final checkpoints
- state mutation on disk

---

## 14. Strategic conclusion

The most important shift from this cycle is that we moved from:
- vague orchestration ideas
- runtime ambiguity
- trust in agent summaries

to:
- explicit state machines
- file-based truth
- validated runtime primitives
- provable director/supervisor/operator roles

That shift should now be treated as part of the B2 standard, not as an ad-hoc workaround.

---

## 15. Operational consequence

These learnings were condensed into the reusable preflight document:

- `SECTOR_PREFLIGHT_CHECKLIST.md`

Future sectors should use that file as the practical gate before asking Paperclip/Perseus to rely on a new sector.
