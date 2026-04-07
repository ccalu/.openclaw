# S4 — Foundation Plan

_Status: implementation planning draft_
_Last updated: 2026-04-04_
_Owner: Tobias_
_Sector: S4 — Asset Research_

---

## 1. Purpose

This document translates Phase 1 of `S4_IMPLEMENTATION_PLAN.md` into concrete foundation work.

Its job is to define the minimal runtime substrate S4 needs before rich sector behavior is implemented.

This is not yet the phase for proving full S4 intelligence.
This is the phase for making S4 exist safely and coherently as a runtime sector.

---

## 2. Foundation objective

The foundation layer is successful when S4 can:
- create its expected runtime structure on disk
- load bootstrap inputs deterministically
- build and resolve paths deterministically
- read/write artifacts through shared helpers
- validate artifacts against frozen contracts/schemas
- write status/checkpoint state in a consistent way
- be launched by the Block 2 boundary as a real sector entrypoint

If these are not proven first, later implementation will become noisy and fragile.

---

## 3. Foundation scope

Included in this phase:
- directory structure planning/materialization
- schema/contract loading strategy
- common Python utilities
- bootstrap parsing/validation
- checkpoint/status writing substrate
- boundary launch wiring for S4 supervisor
- minimal supervisor shell sufficient for boot + initialization

Not included in this phase:
- rich operator intelligence
- multi-target orchestration
- batch execution realism beyond structural support
- retry sophistication
- production-tuned parallelism

---

## 4. Core foundation principles

## 4.1 One substrate, many actors
The foundation layer should centralize the boring runtime mechanics so each actor does not reinvent:
- path logic
- validation logic
- artifact IO
- checkpoint writes
- status writes

## 4.2 Contracts are executable, not decorative
Schemas and contracts should become runtime-enforced structures, not just planning documents.

### Validation approach decision
For S4 v1, the canonical contract layer should be materialized as **JSON Schema files**.

Python runtime code should validate artifacts against those schemas through a shared helper layer.

This means:
- JSON Schema is the contract source of truth
- Python validation helpers are the enforcement/runtime convenience layer
- ad-hoc dict checks may exist only as lightweight defensive guards, not as the primary contract system
- Pydantic-style models may be introduced later for ergonomics, but should not replace JSON Schema as the canonical cross-actor contract source

## 4.3 Windows-safe path discipline
This environment is Windows-first.
The foundation layer must treat path construction, separators, filename safety, and absolute-path validation as first-class concerns.

## 4.4 Deterministic over clever
Prefer obvious deterministic helpers over elegant but implicit abstractions.

---

## 5. Foundation workstreams

## 5.1 Workstream A — directory structure materialization

### Goal
Freeze how the S4 run root is created on disk.

### Required outputs
A deterministic directory creation routine that produces the expected S4 structure under sector root.

### Minimum directory expectations
The exact structure should align with architecture/runtime docs, but foundation should at least support:
- `dispatch/`
- `runtime/`
- `checkpoints/`
- `logs/`
- `compiled/`
- `intake/`
- `batches/`
- `targets/`

And for each target root when needed:
- `assets/`
- `previews/`
- `captures/`

### Key implementation questions
- where is target root naming normalized?
- what sanitization rule is used for target labels?
- what directories are created eagerly vs lazily?

### Exit criteria
- a test run can create the S4 skeleton cleanly
- rerun behavior is deterministic and safe
- paths match what contracts expect

---

## 5.2 Workstream B — path builder utilities

### Goal
Make path construction explicit and reusable.

### Required helper categories
- sector root helpers
- dispatch path helpers
- compiled artifact path helpers
- target root helpers
- target-local artifact path helpers

### Minimum expectations
Helpers should make it easy to derive:
- intake path
- batch manifest path
- target brief path
- candidate set path
- evaluated candidate set path
- coverage report path
- research pack path
- sector report path
- checkpoint paths
- status paths

### Risk to avoid
Do not scatter path concatenation across operators and supervisor logic.

### Exit criteria
- core S4 paths can be derived from bootstrap + target identifiers alone
- all generated paths are absolute where required

---

## 5.3 Workstream C — artifact IO helpers

### Goal
Create a shared runtime layer for reading and writing JSON/markdown artifacts safely.

### Required helper capabilities
- write JSON atomically enough for sector runtime needs
- read JSON with clear error reporting
- write markdown/text artifacts
- existence checks
- readable error messages when artifacts are malformed or missing

### Important note
This layer should support runtime truth, not vague best-effort writes.

### Exit criteria
- artifacts can be written, re-read, and validated consistently
- malformed JSON is surfaced clearly

---

## 5.4 Workstream D — schema validation substrate

### Goal
Turn frozen docs into runtime validation behavior.

### Required decisions
- how schema definitions are materialized in code/files
- how validators are called
- how validation errors are reported to supervisor/operator runtime

### Minimum validation targets for foundation
At least prove validation for:
- `s4.research_intake.v1`
- `s4.target_research_brief.v1`
- `s4.candidate_set.v1`
- `s4.evaluated_candidate_set.v1`
- `s4.coverage_report.v1`
- `s4.research_pack.v1`
- `s4.research_batch_manifest.v1`

### Exit criteria
- sample artifacts can be validated successfully
- schema mismatch failures are explicit and usable

---

## 5.5 Workstream E — bootstrap loading and validation

### Goal
Make supervisor activation deterministic and strict.

### Required behavior
Given `s4.supervisor_bootstrap.v1`, the foundation layer should:
- parse it
- validate required fields
- verify critical upstream paths exist
- fail clearly when essentials are missing

### Critical upstream checks
At minimum verify:
- `compiled_entities.json` path exists
- expected sector/runtime roots are resolvable
- required output directories can be created or already exist safely

### Exit criteria
- invalid bootstrap fails early and visibly
- valid bootstrap produces a normalized runtime context object

---

## 5.6 Workstream F — checkpoint and status substrate

### Goal
Standardize runtime state writing before rich orchestration exists.

### Required capabilities
- write operator status files
- write sector status files
- write checkpoint files consistently
- mirror final completion/failure checkpoints to B2-facing locations when needed

### Design principle
The exact runtime control flow remains authoritative, but the foundation layer should make state-writing simple and consistent.

### Questions to settle
- status file naming convention
- checkpoint write helper shape
- overwrite vs append rules
- how to represent phase transitions cleanly

### Exit criteria
- one helper path exists for writing state artifacts
- actor implementations do not each invent their own checkpoint format

---

## 5.7 Workstream G — boundary launch wiring

### Goal
Prove that S4 can be launched by the real Block 2 boundary path.

### Required behavior
- `w3_block2.py` detects `s4_requested.json`
- boundary resolves bootstrap path
- boundary launches `sm_s4_asset_research`
- initial runtime state becomes visible on disk

### Important constraint
This proof matters more than any single operator implementation.
If the launch path is not real, the sector is not real.

### Exit criteria
- one real trigger causes one real supervisor launch
- boot artifacts/checkpoints/status appear as expected

---

## 5.8 Workstream H — minimal supervisor shell

### Goal
Implement the smallest useful version of `sm_s4_asset_research` for foundation.

### Foundation-only supervisor behavior
- accept bootstrap
- validate bootstrap
- create/verify directories
- initialize status/checkpoints
- optionally write a no-op or stub initialization artifact
- stop cleanly

### What it should NOT do yet
- no full operator dispatch graph
- no evaluation semantics
- no coverage semantics
- no final closure semantics beyond boot sanity

### Exit criteria
- supervisor can boot cleanly as a real actor entrypoint
- supervisor initialization is visible and deterministic

---

## 6. Suggested implementation order inside foundation

Recommended sequence:

1. path builder utilities
2. directory materialization routine
3. artifact IO helpers
4. bootstrap loader/validator
5. minimal supervisor shell
6. boundary launch wiring test
7. schema validation substrate
8. checkpoint/status helpers

### Why this order
Because the real sector entry path should be proven earlier in foundation, not left as the last integration surprise.
Local runtime mechanics still need to exist first, but the real boundary-triggered launch should be established before foundation is considered trustworthy.

---

## 7. Foundation deliverables checklist

By the end of foundation, the implementation should have:

- [ ] deterministic S4 directory creation
- [ ] reusable path helper layer
- [ ] reusable JSON/text artifact IO layer
- [ ] runtime schema validation layer using JSON Schema as canonical contract source
- [ ] strict bootstrap loader/validator
- [ ] reusable checkpoint/status writing layer
- [ ] minimal `sm_s4_asset_research` boot path
- [ ] one real boundary-triggered launch proof

---

## 8. Narrow validation plan for foundation

## 8.1 Validation A — path derivation sanity
Input:
- bootstrap data
- one example target id / label

Expected proof:
- all major sector and target-local paths derive deterministically

## 8.2 Validation B — directory creation sanity
Input:
- empty or fresh sector root

Expected proof:
- required directories appear in correct locations

## 8.3 Validation C — schema validation sanity
Input:
- one valid sample artifact per major schema
- one intentionally invalid sample artifact

Expected proof:
- valid artifact passes
- invalid artifact fails clearly

## 8.4 Validation D — bootstrap failure sanity
Input:
- malformed bootstrap or missing upstream path

Expected proof:
- supervisor boot fails early with explicit reason

## 8.5 Validation E — boundary launch sanity
Input:
- real `s4_requested.json`
- real supervisor bootstrap artifact

Expected proof:
- S4 supervisor starts and writes visible initialization state

---

## 9. Common failure modes to avoid during foundation

- embedding path rules ad hoc inside each actor
- allowing schema docs to drift from runtime validators
- starting operator logic before bootstrap/IO/validation substrate exists
- proving the sector only inside conversational/manual flows instead of the real boundary path
- mixing full orchestration work into foundation before boot mechanics are stable

---

## 10. Exit gate for foundation

Foundation is complete when all of the following are true:
- S4 can be launched by the real boundary path
- the supervisor can initialize deterministically from bootstrap
- core runtime directories and paths are stable
- artifact IO and schema validation are real and reusable
- checkpoint/status writing is standardized enough for later actors to reuse

Only after that should the implementation move into:
**single-target prototype work.**

---

## 11. Recommended next doc

After this document, the most useful next planning artifact is:
- `S4_SINGLE_TARGET_PROTOTYPE_PLAN.md`

That document should define the first end-to-end correctness proof of the sector.
