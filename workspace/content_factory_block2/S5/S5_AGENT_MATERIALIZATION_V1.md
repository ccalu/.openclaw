# S5 Agent Materialization V1

_Status: runtime materialization draft_
_Last updated: 2026-04-07_
_Owner: Tobias_

---

## 1. Purpose of this document

This document defines how the S5 actors should be treated as **real OpenClaw agents**, rather than as folder placeholders or conceptual entities.

Its purpose is to close a critical implementation-adjacent distinction:

> creating a workspace folder is not the same thing as materially creating an agent.

This document therefore defines:
- which S5 agents must exist as real agents
- what local workspace files each agent must have
- what belongs in central S5 docs vs local agent docs
- what counts as real materialization
- how agent materialization should be proven before the sector is treated as operationally real

This is not yet the final implementation plan.
It is the materialization standard that must be obeyed before implementation is considered complete.

---

## 2. Core materialization rule

An S5 agent must **not** be treated as materially created just because:
- its folder exists
- markdown files were written into that folder

The correct materialization rule is:

> an agent only counts as materially created when it exists locally, is recognized by the runtime, and executes a real turn.

This standard follows an already learned Block 2 lesson:
- local agent folders and docs are not enough by themselves
- runtime recognition and a real execution turn are required

---

## 3. Which S5 agents must be materially created

The preferred V1 S5 OpenClaw actor set is now:

### Supervisor
- `sm_s5_scene_kit_design`

### Operator
- `op_s5_scene_kit_designer`

The following S5 phases are no longer preferred as OpenClaw agents and should instead be treated as helper-direct runtime phases:
- `input_assembly.py`
- `direction_frame_builder.py`

These two OpenClaw actors should be treated as the real S5 agent set for V1.
No additional S5 OpenClaw agents should be materialized unless a later explicit decision changes the actor map.

---

## 4. Local workspace standard per agent

Each of the two real S5 OpenClaw agents should have the same standard local workspace file set:

- `IDENTITY.md`
- `MISSION.md`
- `CONTEXT.md`
- `CONTRACT.md`
- `OPERATIONS.md`

This standardization is preferred even if some of those files remain short for certain operators.

The reason is:
- consistency
- easier review
- easier replication to other sectors
- lower chance of hidden contract gaps

---

## 5. What each file should contain

### 5.1 `IDENTITY.md`
Answers:
- who the agent is
- what role it plays in S5
- where it sits hierarchically

Should contain:
- agent name
- role in sector
- supervisor/operator identity
- short function statement

Should not contain:
- full runtime theory of S5
- long implementation details

---

### 5.2 `MISSION.md`
Answers:
- what this agent is trying to accomplish operationally

Should contain:
- central mission
- what successful execution means for this actor
- what output or progression it exists to enable

---

### 5.3 `CONTEXT.md`
Answers:
- what system context this actor needs to remember locally

Should contain:
- relation to B2 and S5
- who activates it
- what upstream artifacts matter to it
- what downstream artifacts or handoffs it supports

Should not contain:
- the full S5 design corpus copied from central docs

---

### 5.4 `CONTRACT.md`
Answers:
- what the actor receives
- what it reads
- what it writes
- what success/failure means

Should contain:
- activation contract
- input artifacts
- output artifacts
- required validations
- completion/failure conditions
- invariants where useful

This is one of the most important local files.

---

### 5.5 `OPERATIONS.md`
Answers:
- how the actor should behave in practice

Should contain:
- operational sequence
- validation priorities
- what to never do
- when to fail explicitly
- filesystem-first truth rules
- context cleanliness rules

This is where practical runtime behaviour should be made explicit.

---

## 6. Central docs vs local docs

A strict separation should be preserved.

### 6.1 Central S5 docs should own
The central docs under:
- `content_factory_block2/S5/`

should remain the source of truth for:
- sector architecture
- boundary philosophy
- object model
- runtime architecture
- S5 -> S6 output posture
- B2 ↔ S5 integration contract

### 6.2 Local agent docs should own
The local docs under:
- `.openclaw/agents/<agent_id>/`

should only own:
- local actor identity
- local mission
- local contract
- local operating rules

### 6.3 Rule
The agent workspace should not become a duplicate of the central S5 docs.
The central docs remain the systemic truth.
The local docs exist to make the actor executable and operationally coherent.

---

## 7. Agent-by-agent materialization intent

## 7.1 `sm_s5_scene_kit_design`

### Role
External S5 face for Block 2.

### Mission
- receive sector bootstrap
- validate upstream
- control the runtime flow of S5
- dispatch operators
- write `s5_completed.json` / `s5_failed.json`
- ensure S5 produces valid downstream handoff artifacts

### Local docs should especially emphasize
- this agent owns sector flow
- it must not absorb all semantic work itself
- it must not replace the operators
- it must not improvise hidden paths or hidden truth
- completion/failure must be artifact-backed

---

## 7.2 Helper-direct phases that should not be materialized as agents

### `input_assembly.py`
Should remain helper-direct because it is mostly:
- file reading
- deterministic linkage
- deterministic policy application
- narrow semantic derivation under Python control

### `direction_frame_builder.py`
Should remain helper-direct because it is mostly:
- context gathering
- one semantic generation call
- validation + write on disk

The current preferred rule is:
- keep these phases explicit in runtime docs and implementation layout
- do not materialize them as OpenClaw agents in V1 unless implementation evidence later proves a real need

---

## 7.3 `op_s5_scene_kit_designer`

### Role
The semantic core of the sector.

### Mission
- read normalized scene package + global frame
- generate `scene_kit_spec`
- produce asset-family structure usable by S6

### Local docs should especially emphasize
- `family_type + family_intent`
- scene kit = asset space, not final edit
- preserve factual grounding where required
- allow controlled creative freedom where appropriate
- do not collapse the scene into a single-image verdict

---

## 8. Materialization checklist

An S5 agent should only count as materially created when all of the following are true:

### 8.1 Local workspace exists
- agent folder exists
- the 5 standard local docs exist

### 8.2 Runtime recognition exists
- the agent appears as a real agent in the runtime
- it is invocable as an actual agent

### 8.3 Real execution exists
- the agent executes a real turn
- the turn is coherent with its local contract
- the turn proves that the agent is not just a folder placeholder

Only after these three conditions are met should the agent be treated as operationally materialized.

---

## 9. Recommended materialization sequence

The recommended order is:

1. central S5 docs are strong enough
2. create local workspaces for the 2 real S5 OpenClaw agents
3. create the real agents in OpenClaw, not just folders
4. validate runtime recognition
5. run a real narrow turn for each one
6. only then treat S5 as materially agentized

This sequence is important because it reduces the risk of false confidence from nice-looking folders that have not yet been proven in runtime.

---

## 10. What this document deliberately does not decide yet

This document does not yet freeze:
- the final implementation topology under the supervisor
- whether the supervisor uses a shell/orchestrator helper exactly like S4
- the final probe-turn strategy for each agent
- the exact implementation phase plan

Those belong to the next layer of design.

---

## 11. Summary

The S5 agent materialization standard is now:
- there are 2 real S5 OpenClaw agents in V1
- each one should use the same 5 local workspace files
- `input_assembly.py` and `direction_frame_builder.py` should remain helper-direct in V1
- central docs remain the systemic source of truth
- local docs remain local operational truth
- a folder alone does not count as a real agent
- runtime recognition + real execution are required before an agent counts as materially created

This is now the preferred baseline for treating S5 actors as real OpenClaw agents.
