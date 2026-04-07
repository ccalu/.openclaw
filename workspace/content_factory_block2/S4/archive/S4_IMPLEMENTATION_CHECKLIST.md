# S4 — Implementation Checklist

_Status: implementation planning draft_
_Last updated: 2026-04-04_
_Owner: Tobias_
_Sector: S4 — Asset Research_

---

## 1. Purpose

This checklist converts the S4 implementation planning layer into an execution-oriented sequence.

It is not a replacement for the implementation plan, foundation plan, or single-target prototype plan.
It is the operational bridge between them.

Its purpose is to make it obvious:
- what to do first
- what depends on what
- what counts as done
- what must be proven before moving forward

---

## 2. Execution posture

Follow this checklist with the following discipline:
- do not skip gates
- do not mark items done based on conversational confidence
- prefer narrow proof over broad progress claims
- keep artifact/schema truth ahead of implementation speed

---

## 3. Phase 0 — pre-flight alignment

### 3.1 Documentation hygiene
- [x] R4 fix pass applied
- [x] pack compiler input explicitly includes raw `candidate_set`
- [x] coverage report path aligned to `compiled/coverage_report.json`
- [x] supervisor failure decision table added
- [x] `s4.research_batch_manifest.v1` documented
- [x] schema validation approach decided: JSON Schema as canonical contract source
- [x] boundary launch moved earlier in foundation order
- [x] `candidate_set_paths` added to `s4.pack_compiler_dispatch.v1`
- [x] `batches/` added to foundation directory expectations

### 3.2 Planning docs
- [x] `S4_IMPLEMENTATION_PLAN.md` created
- [x] `S4_FOUNDATION_PLAN.md` created
- [x] `S4_SINGLE_TARGET_PROTOTYPE_PLAN.md` created
- [x] `S4_IMPLEMENTATION_CHECKLIST.md` created

### Exit gate
- [ ] planning layer judged sufficient for implementation start

---

## 4. Phase 1 — foundation implementation

## 4.1 Path and directory substrate
- [ ] define sector-root path derivation rules
- [ ] define target-root naming/sanitization rules
- [ ] implement reusable path builder helpers
- [ ] implement S4 directory creation routine
- [ ] verify expected directories are created deterministically

### Done criteria
- [ ] intake/dispatch/runtime/checkpoints/logs/compiled/targets paths derive cleanly
- [ ] target-local assets/previews/captures paths derive cleanly
- [ ] reruns do not create ambiguous layout drift

## 4.2 Artifact IO substrate
- [ ] implement JSON read helper
- [ ] implement JSON write helper
- [ ] implement markdown/text write helper
- [ ] implement explicit existence/error helpers

### Done criteria
- [ ] artifacts can be written and re-read reliably
- [ ] malformed/missing artifacts fail clearly

## 4.3 Schema validation substrate
- [ ] materialize JSON Schema files as canonical contract artifacts
- [ ] implement validation helper for S4 artifacts
- [ ] prove validation against sample valid artifacts
- [ ] prove validation against sample invalid artifacts

### Required schema coverage
- [ ] `s4.research_intake.v1`
- [ ] `s4.research_batch_manifest.v1`
- [ ] `s4.target_research_brief.v1`
- [ ] `s4.candidate_set.v1`
- [ ] `s4.evaluated_candidate_set.v1`
- [ ] `s4.coverage_report.v1`
- [ ] `s4.research_pack.v1`

## 4.4 Bootstrap + state substrate
- [ ] implement bootstrap loader for `s4.supervisor_bootstrap.v1`
- [ ] validate required bootstrap fields
- [ ] validate critical upstream artifact paths
- [ ] implement sector status writer
- [ ] implement checkpoint writer helpers

### Done criteria
- [ ] invalid bootstrap fails early and clearly
- [ ] valid bootstrap produces normalized runtime context
- [ ] state artifacts can be written consistently

## 4.5 Minimal supervisor shell
- [ ] create minimal `sm_s4_asset_research` runtime entrypoint
- [ ] load bootstrap
- [ ] initialize directories
- [ ] initialize runtime status/checkpoints
- [ ] stop cleanly after initialization proof if needed

### Done criteria
- [ ] supervisor can boot as a real actor entrypoint
- [ ] initialization is visible on disk

## 4.6 Boundary launch proof
- [ ] wire `w3_block2.py` to detect `s4_requested.json`
- [ ] resolve bootstrap path correctly
- [ ] launch `sm_s4_asset_research`
- [ ] verify initialization artifacts appear

### Exit gate
- [ ] S4 can be launched by the real boundary path
- [ ] supervisor boot path is real and deterministic

---

## 5. Phase 2 — single-target prototype implementation

## 5.1 Supervisor prototype flow
- [ ] implement minimal prototype phase sequencing in supervisor
- [ ] implement per-step validation gates
- [ ] keep scope constrained to exactly one target

## 5.2 Target builder
- [ ] implement `op_s4_target_builder`
- [ ] read S3 upstream artifacts
- [ ] emit `s4_research_intake.json`
- [ ] emit target builder report if required by dispatch
- [ ] validate intake against schema

## 5.3 Batch manifest generation
- [ ] have supervisor generate simplest valid one-target `research_batch_manifest.json`
- [ ] validate batch manifest against schema

## 5.4 Web investigator
- [ ] implement `op_s4_web_investigator`
- [ ] consume intake + batch manifest
- [ ] emit one `target_research_brief.json`
- [ ] validate brief against schema

## 5.5 Research worker
- [ ] implement one-target `op_s4_target_research_worker`
- [ ] consume one brief
- [ ] emit one `candidate_set.json`
- [ ] validate candidate set against schema

## 5.6 Candidate evaluator
- [ ] implement `op_s4_candidate_evaluator`
- [ ] consume raw candidate set
- [ ] emit one `evaluated_candidate_set.json`
- [ ] validate evaluated set against schema

## 5.7 Coverage analyst
- [ ] implement `op_s4_coverage_analyst`
- [ ] consume intake + evaluated set
- [ ] emit `compiled/coverage_report.json`
- [ ] validate coverage report against schema

## 5.8 Pack compiler
- [ ] implement `op_s4_pack_compiler`
- [ ] consume intake + raw set + evaluated set + coverage report
- [ ] emit `compiled/s4_research_pack.json`
- [ ] emit `compiled/s4_sector_report.md`
- [ ] validate research pack against schema

## 5.9 Supervisor closure
- [ ] validate final artifact set
- [ ] write `s4_completed.json`
- [ ] verify B2-facing resume path can trust completion artifact

### Exit gate
- [ ] one target runs end-to-end
- [ ] all mandatory artifacts exist
- [ ] all major JSON artifacts validate
- [ ] sector closes from disk truth, not manual interpretation

---

## 6. Phase 3 — supervisor orchestration hardening

- [ ] replace prototype-only sequencing with fuller supervisor phase management
- [ ] formalize phase transitions/checkpoint progression
- [ ] enforce failure table behavior
- [ ] improve validation error propagation
- [ ] verify failure semantics for critical operators

### Suggested focused tests
- [ ] target builder failure -> sector fails
- [ ] web investigator failure -> sector fails
- [ ] worker failure -> sector continues with explicit gaps
- [ ] evaluator failure -> sector fails
- [ ] coverage failure -> sector fails
- [ ] pack compiler failure -> sector fails

### Exit gate
- [ ] supervisor behavior matches planned v1 control posture
- [ ] checkpoint flow is inspectable and stable

---

## 7. Phase 4 — multi-target scaling

- [ ] extend supervisor to multiple targets
- [ ] generate multi-target batch manifests
- [ ] dispatch multiple worker runs
- [ ] aggregate multiple candidate/evaluated outputs
- [ ] preserve target/scene coherence in coverage report
- [ ] preserve target/scene coherence in final pack
- [ ] apply bounded parallelism intentionally

### Exit gate
- [ ] multi-target run succeeds without breaking artifact coherence
- [ ] batch manifest acts as a real control artifact
- [ ] aggregated outputs remain trustworthy

---

## 8. Phase 5 — hardening / operational maturity

- [ ] improve observability/debug artifacts
- [ ] improve status/report quality
- [ ] tune timeout posture if needed
- [ ] add optional checkpoint/report cross-links if useful
- [ ] evaluate whether degraded completion needs formalization

### Exit gate
- [ ] S4 is not only correct, but operationally usable and debuggable

---

## 9. Non-negotiable proof requirements

These are never optional:
- [ ] artifact truth on disk
- [ ] schema-validated major outputs
- [ ] deterministic supervisor closure semantics
- [ ] no hidden reliance on chat summaries as runtime truth
- [ ] no premature scale claims before one-target proof

---

## 10. Stop conditions

Pause and reassess if any of these happen:
- [ ] multiple docs/schemas need reinterpretation during coding
- [ ] actor responsibilities start drifting materially
- [ ] supervisor only works through manual hand-holding
- [ ] output schemas become too awkward to validate in runtime
- [ ] prototype cannot close without bypassing planned contracts

If one of these occurs, implementation should pause and the docs/runtime assumptions should be reviewed before continuing.

---

## 11. Final execution recommendation

The first serious implementation success condition is not:
- "most actors exist"

It is:
- **"one real S4 target completed end-to-end under supervisor control with schema-validated disk artifacts."**

That is the milestone the implementation should optimize for first.
