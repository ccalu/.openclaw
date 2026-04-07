# Recommended structure for the video editing department org

## Executive recommendation

Keep the 4-layer hierarchy already envisioned, but make it stricter:

1. **CEO / Tobias** = strategy, escalation, human interface, org evolution
2. **Production Manager** = portfolio router, scheduler, dependency manager, exception owner
3. **Branch Managers (10)** = branch-local planner + reviewer + dispatcher
4. **Specialist agents (~43)** = single-purpose workers with narrow inputs/outputs

Do **not** collapse Tobias and Production Manager into one agent.
Do **not** let specialist agents talk laterally to each other.
Do **not** let lower agents own global context.

## Recommended responsibilities by layer

### Layer 1 — CEO / Tobias
Owns:
- conversation with Lucca
- high-level editorial policy and architecture
- approvals for major org changes, quality standards, and unusual escalations
- deciding when to trigger PM

Should not own:
- per-video operational scheduling
- branch-by-branch execution loops
- detailed worker retries

Recommended cadence:
- event-driven, not cron-heavy
- receives compressed reports from PM and Monitoring

### Layer 2 — Production Manager
Owns:
- reading the incoming production queue
- choosing account/video priority
- deciding which branches run and in what dependency order
- handling blocked jobs, retries, SLA logic, and escalation to Tobias
- consolidating branch status into one portfolio view

Should be the only agent that sees:
- full job state across branches
- branch readiness/dependency graph
- capacity information across machines

Recommended PM outputs:
- `job_manifest.json`
- `run_plan.json`
- `branch_dispatches/`
- `portfolio_status.md`
- `escalations.md`

### Layer 3 — Branch Managers
Each BM should combine three roles:
1. branch planner
2. branch dispatcher
3. branch reviewer

That means a BM should:
- accept a PM dispatch
- decompose work into specialist tasks
- run independent workers in parallel when possible
- validate that branch outputs meet contract before releasing them upstream
- request retry/escalation only through PM

Each BM should **not**:
- directly schedule other branches
- rewrite upstream artefacts casually
- chat with another BM except through PM-owned artefacts

Suggested BM internal pattern:
- intake -> task split -> parallel workers -> branch review -> publish branch artefact

### Layer 4 — Specialist agents
Rules:
- one task only
- no awareness of org topology
- no cross-branch writes
- no freeform memory beyond task-local scratchpad
- must emit structured outputs with confidence/flags when relevant

Examples:
- `people_finder` finds candidates only
- `asset_judge` scores candidates only
- `music_planner` proposes soundtrack plan only
- `tsx_validator` validates only

## Routing model

Use a **hub-and-spoke** routing model:
- Lucca <-> Tobias
- Tobias -> PM
- PM -> BM
- BM -> specialists
- specialists -> BM
- BM -> PM
- PM -> Tobias

Optional direct human access to BMs is fine for debugging, but operationally the canonical route should remain through PM.

## Workspace and context isolation

Recommended isolation rules:

### Per-layer context
- Tobias loads only his own strategic docs + compressed reports.
- PM loads only PM docs + current manifests/statuses.
- Each BM loads only branch docs + current branch input artefacts.
- Each specialist loads only prompt/instructions + exact task payload.

### Per-job filesystem pattern
Use per-video run folders to avoid collisions:

`runs/{account_id}/{video_id}/`
- `00_pm/`
- `01_pre_production/`
- `02_audio/`
- ...
- `09_quality_assurance/`
- `10_monitoring/`

Within each branch folder:
- `in/`
- `work/`
- `out/`
- `review/`
- `logs/`

This is better than having all agents writing directly into one shared global area.

### Shared global registries
Keep these append-mostly / reference-oriented:
- `shared/character_bible/`
- `shared/asset_registry/`
- `shared/style_registry/`

Only designated agents should update each shared registry, ideally through BM-reviewed writes.

## Artefact contracts

Use explicit stage contracts. Example flow:
- B1 publishes `scene_bible.json`
- B2 publishes `audio_package.json`
- B3 publishes `visual_plan.json`
- B4 publishes `asset_candidates.json`
- B5 publishes `generated_assets.json`
- B6 publishes `scene_timeline.json`
- B7 publishes `post_plan.json`
- B8 publishes `render_package.json`
- B9 publishes `qa_report.json`
- B10 publishes `ops_report.json`

Each artefact should include:
- `job_id`
- `account_id`
- `source_stage`
- `version`
- `inputs_used`
- `status`
- `confidence` or `quality_score` where relevant
- `blocking_issues[]`
- `next_expected_stage`

## Cheap-model decomposition policy

### Default by layer
- Tobias: premium model only
- PM: medium model by default, premium on escalation
- BMs: cheap-medium by default, premium only for difficult creative synthesis or failed reviews
- specialists: cheapest capable model first; prefer local models for extraction, classification, templating, formatting, routing, and first-pass QA

### Escalation triggers
Escalate model only if:
- output fails schema twice
- confidence below threshold
- branch review rejects twice
- task is explicitly creative/high-impact
- user/human requested gold-standard pass

## Recommended additional org rules

1. **Branch managers own quality before QA sees it**  
   QA should be independent, but BMs should not ship obviously weak outputs downstream.

2. **Monitoring is cross-cutting, not just another branch**  
   Keep B10 separate, but let it observe every branch and every machine.

3. **Approval boundaries must be explicit**  
   Define what specialists/BMs can auto-retry, what PM can auto-reroute, and what must escalate to Tobias/Lucca.

4. **Use parallelism only where artefacts are independent**  
   Avoid creative incoherence from uncontrolled parallel generation.

5. **Preserve deterministic spine where possible**  
   Use agents for judgment and generation; use code for file movement, validation, rendering, and state transitions.

## Minimal implementation order

Recommended order:
1. Tobias
2. Production Manager
3. B1, B2, B3, B9, B10 managers
4. only the minimum specialists needed to produce one end-to-end pilot
5. then B4/B5/B6/B7/B8 harden incrementally

Reason:
- B1-B3 define planning truth
- B9/B10 create feedback and observability early
- without QA/monitoring early, the org will look like it works while silently degrading
