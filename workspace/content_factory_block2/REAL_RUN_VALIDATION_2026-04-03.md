# Real Run Validation — 2026-04-03

## Goal
Validate the next execution tranche for Block 2 with a real OpenClaw path narrower than the full sector: bootstrap B2/S3 correctly, run at least one real S3 operator agent, validate its output structurally, compile sector artifacts, and observe what still blocks Paperclip/Perseus activation of `b2_director -> S3`.

## What was changed

### 1. `helpers/build_s3_bootstrap_from_b2.py`
Upgraded the generated `s3_source_package.json` so it now mirrors the shape documented in `S3/inputs.md` much more closely:
- reads `screenplay_analysis.json`
- optionally reads `01_script_fetched.json`
- writes `video_context`
- writes `script_overview`
- writes normalized `scenes[]`
- preserves `entity_focus` and upstream input references

### 2. `S3/helpers/build_operator_dispatches.py`
Added narrow-run support:
- can now emit dispatches for all operators
- or for one selected operator only
- writes an activation plan that explicitly marks the inactive operators

### 3. `helpers/real_run_b2_s3_one_operator.py`
Added a mechanical validation runner that:
- creates an isolated run root
- bootstraps B2 in `s3_only`
- builds canonical S3 bootstrap + source package
- generates dispatch for one selected operator
- invokes the real OpenClaw operator agent via `openclaw agent --agent ...`
- validates operator output against schema
- compiles `compiled_entities.json`
- generates `s3_sector_report.md`
- **does not claim block success when the compiled sector status is only `degraded_completed`**
- emits `s3_failed.json` instead in that narrow-run case

## What is now proven

### Proven mechanically
1. The real S3 operator agents exist in OpenClaw and are registered:
   - `op_s3_human_subject_extractor`
   - `op_s3_environment_location_extractor`
   - `op_s3_object_artifact_extractor`
   - `op_s3_symbolic_event_extractor`
   - plus `sm_s3_visual_planning`

2. A real operator invocation works end-to-end through OpenClaw:
   - tested agent: `op_s3_human_subject_extractor`
   - invocation path: `openclaw agent --agent op_s3_human_subject_extractor --message ...`
   - the agent wrote:
     - `output.json`
     - `status.json`
     - `checkpoint.json`

3. The human operator output passed structural validation against the formal schema.

4. The sector can be compiled from real operator output plus missing-operator gaps, producing:
   - `compiled/compiled_entities.json`
   - `compiled/s3_sector_report.md`

5. The system can correctly distinguish:
   - real operator success
   - sector compile still being incomplete/degraded
   - therefore block not actually ready for success closure

### Proven artefact example
Narrow real run:
- `runtime_realcheck/run_004/`

Key outputs:
- `b2/sectors/s3_visual_planning/inputs/s3_source_package.json`
- `b2/sectors/s3_visual_planning/checkpoints/operator_activation_plan.json`
- `b2/sectors/s3_visual_planning/dispatch/human_subject_extractor_job.json`
- `b2/sectors/s3_visual_planning/operators/human_subject_extractor/output.json`
- `b2/sectors/s3_visual_planning/compiled/compiled_entities.json`
- `b2/checkpoints/s3_failed.json`

## What is still not proven

1. **`b2_director` itself is not yet proven as a real invoked agent turn.**
   The current validation used helpers to simulate the director’s mechanical responsibilities instead of invoking a real `b2_director` agent turn and observing it make the transition itself.

2. **`sm_s3_visual_planning` itself is not yet proven as a real invoked supervisor turn.**
   The current narrow run used helper scripts to prepare dispatch, then invoked one real operator directly.

3. **The full S3 happy path with all required operators is not yet proven.**
   The compile status for the narrow run is `degraded_completed`, not `completed`.

4. **Resume semantics back into the director are not yet proven with a real agent turn.**
   We have the checkpoints and helper logic, but not an observed real re-entry of `b2_director` on `s3_completed` / `s3_failed`.

5. **Paperclip -> Perseus -> b2_director activation is not yet proven operationally.**
   No live Paperclip-facing trigger was exercised here.

## Current blocker statement for Perseus
Paperclip should **not** yet assume that creating Perseus is enough to activate a coherent `b2_director -> S3` runtime.

Why:
- the real operator layer is partially proven
- the source-package + dispatch substrate is stronger now
- but the actual control-plane agents (`b2_director`, `sm_s3_visual_planning`) are still not proven in a live turn-to-turn runtime loop
- and the full-S3 success condition is still unproven

## Addendum — real control-plane probe executed after this note

### Probe A — real `sm_s3_visual_planning` turn (`runtime_realcheck/run_005/`)
What was observed:
- the supervisor **was invoked for real** through `openclaw agent --agent sm_s3_visual_planning`
- it successfully read the real bootstrap from disk
- it wrote its own control-plane artefacts:
  - `checkpoints/s3_supervisor_started.json`
  - `checkpoints/operator_activation_plan.json`
  - `dispatch/human_subject_extractor_job.json`
  - `checkpoints/s3_final_checkpoint.json`
- it also produced compiled sector artefacts under `compiled/`

What was **not** observed:
- the supervisor did **not** successfully launch a real subordinate operator under its own control
- its own final checkpoint explicitly states:
  - `status = degraded_completed`
  - reason: `ACP runtime backend unavailable; real op_s3_human_subject_extractor session could not be launched.`

Interpretation:
- this proves a **partial real supervisor turn** (bootstrap ingestion + checkpoint/dispatch ownership)
- this does **not** prove the decisive control-plane hop `supervisor -> real operator`
- therefore the supervisor control-plane path is still **not fully proven**

### Probe B — real `b2_director` invocation attempt (`runtime_realcheck/run_006/`)
What was observed:
- invoking `openclaw agent --agent b2_director ...` failed immediately
- CLI error: `Unknown agent id "b2_director"`
- `openclaw agents list` confirms that `b2_director` is **not registered** in the local OpenClaw agent registry, even though a folder exists at `.openclaw/agents/b2_director/`

Interpretation:
- the director is not just unproven — it is currently **not invokable as an OpenClaw agent** in this environment
- bootstrap behavior and resume behavior therefore remain entirely unproven as live director turns

## Recommended next validation tranche
1. Fix the runtime registration gap for `b2_director` so it appears in `openclaw agents list`.
2. Understand why nested real agent launches from `sm_s3_visual_planning` report `ACP runtime backend unavailable`, despite direct top-level operator invocations working from the shell.
3. Re-run the supervisor probe and require one **actually launched** subordinate operator, not supervisor-authored fallback output.
4. After `b2_director` is registered, run two real director turns:
   - bootstrap on `b2.bootstrap.v1`
   - resume on `b2.resume.v1` from an actual `s3_completed.json` or `s3_failed.json`
5. Only after those two control-plane links are proven should Paperclip create Perseus to drive this path.
