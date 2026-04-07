# S4 — Asset Research Architecture

_Status: planning draft_
_Last updated: 2026-04-04_
_Owner: Tobias_

---

## 1. Purpose of this document

This document defines the intended architecture, runtime flow, contracts, responsibilities, storage model, and implementation constraints for **S4 — Asset Research** inside **Block 2** of the Content Factory visual pipeline.

It is deliberately more detailed than a lightweight concept note. The goal is to reduce ambiguity **before implementation** and to explicitly account for the practical limitations already observed in OpenClaw runtime materialization, sector orchestration, CLI-based agent invocation, filesystem truth, and real-world agent fragility.

This document is not just a conceptual description of what S4 should do in the abstract. It is a planning artifact for building an S4 that is:

- architecturally coherent
- operationally viable in OpenClaw
- robust against context overload
- explicit about handoffs and storage
- designed around persisted artifacts rather than conversational memory
- compatible with the current B2 state-machine approach

This document is the **sector architecture layer**. It must be read together with the companion docs that freeze:

- runtime control flow
- invocation mechanics
- JSON contracts / schemas

---

## 1.1 Browsing substrate policy (forward policy)

This section freezes the intended browsing/research substrate for the mature S4 sector so later implementation and final agent materialization do not drift.

### Default browsing stack
The default browsing stack for S4 should be:
- **Brave Search** for discovery/search
- **Firecrawl** for page fetching/extraction

The normal browsing flow should therefore be:
1. discover candidate URLs via Brave Search
2. fetch/extract useful page content via Firecrawl
3. assemble candidate research outputs from those results

### Playwright policy
**Playwright should not be the default browsing substrate for S4.**

Playwright is a fallback/escalation tool only, intended for cases where:
- a target page requires JavaScript rendering
- useful content is hidden behind interaction/clicks
- the Brave + Firecrawl path fails to extract the needed material
- a specific screenshot/capture interaction is required

### Actor-level browsing policy
Intended mature-state browsing policy by actor:
- `op_s4_web_investigator` -> Brave Search + optional light Firecrawl usage for discovery refinement / planning
- `op_s4_target_research_worker` -> Brave Search + Firecrawl as the main research substrate
- `op_s4_candidate_evaluator` -> no browsing by default
- `op_s4_coverage_analyst` -> no browsing by default
- `op_s4_pack_compiler` -> no browsing by default
- `op_s4_target_builder` -> no browsing by default
- `sm_s4_asset_research` -> no browsing by default

### Future agent-tooling implication
When S4 actors are later materialized as real OpenClaw agents near production readiness:
- `op_s4_web_investigator` should be provisioned with Brave Search and, when needed, Firecrawl
- `op_s4_target_research_worker` should be provisioned with Brave Search and Firecrawl
- Playwright/browser automation should be treated as explicit fallback capability, not default baseline assumption

---

## 2. Position of S4 inside Block 2

### 2.1 Macro position

Block 2 is the paperclip-facing visual unit.

Current internal conceptual sequence:

- **S3 — Visual Planning**
- **S4 — Asset Research**
- **S5 — Visual Direction**
- **S6 — Asset Production / Generation / Materialization**

### 2.2 S4's role in that sequence

S4 is the sector that answers:

> Given the visual needs identified upstream, what evidence, references, source assets, and usable visual material can actually be found, collected, organized, and qualified for downstream visual decision-making?

Put differently:

- **S3** says what needs to be represented.
- **S4** investigates what can be found and organizes that into a usable asset intelligence layer.
- **S5** decides how to use that visual possibility space.
- **S6** generates, acquires, transforms, or materializes final production assets.

### 2.3 Why S4 must exist as its own sector

S4 should not be collapsed into S3, S5, or S6.

- It is not just extraction (S3).
- It is not just aesthetic direction (S5).
- It is not just generation or final asset production (S6).

Its job is to do **visual investigation and sourcing**.

That means S4 owns:

- web-native discovery
- source exploration
- candidate collection
- preliminary asset acquisition/materialization
- qualification of findings
- coverage/gap mapping
- packaging findings for downstream use

---

## 3. Core mission of S4

### 3.1 Mission statement

S4 receives a research-ready set of visual targets derived from S3 and produces a structured, persisted, reviewable **research pack** containing:

- factual visual evidence
- visual references
- stylistic inspirations
- unresolved gaps
- local materialized assets/previews when possible
- target-level and scene-level organization

### 3.2 What S4 must do

S4 must:

1. transform S3 visual planning output into actionable research targets
2. investigate the open web and source-specific environments for relevant assets
3. collect candidate references and actual file assets when possible/appropriate
4. evaluate candidate relevance and utility
5. distinguish factual evidence from visual reference and from stylistic inspiration
6. determine target-level and scene-level coverage
7. expose unresolved needs clearly for S5/S6
8. persist all important findings to disk as the operational source of truth

### 3.3 What S4 must not do

S4 must not:

- decide the final artistic language of the video (S5)
- perform final generation or transformation of production-ready assets (S6)
- pretend that a symbolic support image is factual evidence
- treat conversational agent summaries as source of truth over files on disk
- rely on a single API or public archive endpoint as if that were sufficient search infrastructure
- assume a downloaded asset is production-safe without clear classification and notes

---

## 4. Why S4 belongs in OpenClaw

The point of bringing S4 into OpenClaw is **not** simply to wrap public image-bank APIs.

The point is to support a more human-like investigative process:

- iterative query reformulation
- web-native exploration
- opening candidate pages
- following side trails
- using different source types opportunistically
- adapting research strategy by target type
- running multiple target-focused investigations in parallel when useful
- persisting intermediate findings in a sector-local filesystem model

This sector should be designed as a **visual investigation layer**, not as an API retriever.

---

## 5. High-level sector architecture

### 5.1 Primary actors

At the current planning level, S4 is composed of the following core actors:

1. **`sm_s4_asset_research`**
   - sector supervisor
   - owns sector-level control flow
   - owns sector bootstrap, readiness, dispatch, gating, closure

2. **`op_s4_target_builder`**
   - first operator of the sector
   - transforms S3 compiled output into research-ready S4 intake

3. **`op_s4_web_investigator`**
   - discovery-phase coordinator
   - defines the operational discovery briefs
   - organizes target-level investigation work conceptually
   - does **not** need to directly own runtime spawning of worker invocations

4. **`op_s4_target_research_worker`**
   - target-focused discovery worker
   - researches one target or a small bounded target batch
   - writes target-local outputs and materialized assets/previews/captures

5. **`op_s4_candidate_evaluator`**
   - separate evaluation role
   - reviews candidate sets after discovery
   - confirms/corrects classification and usability

6. **`op_s4_coverage_analyst`**
   - determines target-level and scene-level coverage status
   - reports covered / partial / inspiration_only / unresolved

7. **`op_s4_pack_compiler`**
   - consolidates all outputs into final S4 pack

### 5.2 Important distinction: logical hierarchy vs runtime invocation

A critical distinction must be preserved:

- **logical hierarchy** = who owns what responsibility semantically
- **runtime invocation hierarchy** = who actually launches whom in the proven runtime substrate

The S4 architecture preserves a rich **logical hierarchy**, including a discovery coordination layer.

However, the **runtime invocation model** for S4 v1 should remain anchored to the proven B2/S3 pattern:

- filesystem truth
- checkpoint-driven progression
- Python / boundary-controlled orchestration
- sector supervisor controlling sector dispatch
- no reliance on nested `sessions_spawn` trees for critical progression

This means:

- `op_s4_web_investigator` remains the discovery coordinator **conceptually**
- but S4 v1 should **not** assume that this operator directly spawns subordinate OpenClaw workers via an unproven nested runtime mechanism

### 5.3 Key architectural principle

The S4 architecture should remain intellectually rich, but operational burden must be distributed across:

- persisted artifacts
- layered summaries
- subordinate worker roles
- focused responsibilities
- runtime patterns already proven in S3/B2

The solution to complexity is **not flattening the sector into a trivial pipeline**.
The solution is to build the right intermediate layers so no actor becomes a super-hero.

---

## 6. Canonical flow after S3 completes

### 6.1 Runtime truth at S3 completion

When S3 is finished, Block 2 should have at minimum:

- `compiled_entities.json`
- sector report / runtime status
- upstream checkpoint indicating S3 completion

S4 must not start from operator chatter or inferred memory.
It starts from the persisted compiled artifact.

### 6.2 Sequence overview (logical flow)

1. `b2_director` detects `s3_completed`
2. `b2_director` activates S4
3. `sm_s4_asset_research` bootstraps sector and validates upstream artifact
4. `op_s4_target_builder` builds `s4_research_intake.json`
5. `sm_s4_asset_research` approves intake and opens discovery planning
6. `sm_s4_asset_research` creates a batch manifest for discovery
7. `op_s4_web_investigator` builds discovery briefs / batch discovery plan
8. target-focused `op_s4_target_research_worker` runs collect candidates and assets
9. discovery outputs are consolidated into batch summaries
10. `op_s4_candidate_evaluator` evaluates candidate sets
11. `op_s4_coverage_analyst` computes coverage/gaps
12. `sm_s4_asset_research` decides whether the sector can close under v1 policy
13. `op_s4_pack_compiler` builds final S4 pack
14. `sm_s4_asset_research` validates closure artifacts and marks sector complete/degraded
15. `b2_director` resumes macro orchestration and hands off to S5

### 6.3 Current planning choice regarding second-round redispatch

A second research round is architecturally valid and may exist later, but for **S4 v1** it should be treated as optional and omitted from the baseline runtime plan unless implementation remains tractable.

That means S4 v1 should be designed to succeed primarily via:

- strong target formation
- strong discovery briefs
- strong candidate evaluation
- strong coverage analysis
- one strong pass

without assuming recursive multi-round search loops are required for baseline viability.

---

## 7. Supervisor responsibility model

### 7.1 `sm_s4_asset_research` is not a super-researcher

The S4 supervisor should not be designed as an all-knowing operator who:

- reads every raw result
- manually evaluates every candidate
- personally reasons through every target in detail
- directly operates all search steps

That is too much cognitive burden for one actor.

### 7.2 What the supervisor actually owns

The supervisor should own:

- sector bootstrap
- upstream readiness gate
- intake approval gate
- dispatch planning
- progress tracking
- closure gate
- degradation/failure handling
- state persistence
- sector-completion contract

### 7.3 What reduces supervisor overload

Supervisor load is mitigated by requiring intermediate artifacts:

- `s4_research_intake.json`
- `research_batch_manifest.json`
- `target_research_brief.json`
- `batch_discovery_summary.json`
- `evaluated_candidate_set.json`
- `coverage_report.json`

The supervisor should consume structured summaries, not unbounded raw web outputs.

### 7.4 Runtime discipline

For S4 v1, the supervisor should remain consistent with the proven S3/B2 pattern:

- it governs the sector
- it dispatches / approves sector-level operations
- it does not become a freeform conversational coordinator relying on long-lived memory
- it depends on disk artifacts and checkpoints, not on fragile nested agent announce chains

---

## 8. Discovery-phase hierarchy

### 8.1 Why one investigator is not enough

A single web investigator doing all target research sequentially is likely too slow, too context-heavy, and too brittle.

### 8.2 Recommended logical model

Use a two-level **logical** discovery structure:

#### Level 1 — discovery coordinator
- `op_s4_web_investigator`

#### Level 2 — target-focused workers
- `op_s4_target_research_worker`
- optional future: `op_s4_source_probe_worker`

### 8.3 Role of `op_s4_web_investigator`

This actor should:

- receive intake + batch manifest
- convert selected targets into concise research briefs
- structure discovery work into bounded target-level tasks
- define what each worker needs to investigate
- collect or summarize the batch discovery state conceptually
- produce batch-level discovery summaries

This actor is therefore closer to a **functional supervisor of discovery** than to a single worker.

### 8.4 Runtime model for S4 v1

For S4 v1, this logical hierarchy should **not** be interpreted as direct nested runtime spawning by the investigator.

The preferred operational model is:

- `sm_s4_asset_research` remains the sector-level dispatcher in the proven pattern
- `op_s4_web_investigator` produces discovery briefs / batch coordination artifacts
- target workers are then launched through the established sector dispatch substrate
- completion is tracked through files/checkpoints, not agent-to-agent announce dependence

### 8.5 Why this is still worth preserving

Without this discovery-coordination layer, the sector supervisor would need to absorb all discovery-planning complexity directly.
That would re-centralize too much intelligence in `sm_s4_asset_research`.

So the discovery layer stays — but in S4 v1 it should be realized through artifacts and dispatch discipline, not through unproven nested invocation assumptions.

---

## 9. S3 -> S4 boundary

### 9.1 Upstream artifact

The primary upstream artifact is currently:

- `compiled_entities.json`

produced by S3.

### 9.2 Important distinction

`compiled_entities.json` is a correct **S3 compiled output**, but not yet the ideal **S4 research-ready intake**.

S4 should not operate directly on the S3 raw compiled buckets as its working model.
Instead, S4 should derive a sector-specific intake layer.

### 9.3 Why target-building is necessary

The S3 compiled structure can contain:

- entity duplication across buckets
- location/object overlaps
- symbolic concepts that are not directly searchable as factual entities
- scene linkage that exists but is not yet optimized for research

Therefore, the first S4 operator must transform S3 compiled output into:

- canonical research targets
- deduplicated target groupings
- research modes
- scene-target linkage
- priority information

---

## 10. `op_s4_target_builder`

### 10.1 Mission

Turn S3 compiled entities into a research-ready intake for S4.

### 10.2 Input

Primary input:
- `compiled_entities.json`

Optional contextual inputs later:
- S3 report
- source package
- run metadata
- scene metadata if available from upstream package

### 10.3 Responsibilities

`op_s4_target_builder` must:

1. parse S3 compiled buckets
2. normalize entities into a common internal shape
3. detect and merge obvious overlaps/duplicates
4. produce canonical `research_targets`
5. map scenes to targets
6. assign target-level metadata sufficient for discovery
7. persist a stable `s4_research_intake.json`

### 10.4 Recommended implementation model

This operator should not be a freeform LLM-only generator.

Instead, it should be a **hybrid operator**:

- deterministic substrate/Python for parsing, normalization, indexing, dedupe, mapping, schema validation
- focused semantic step for target type classification / strategy hints where needed

### 10.5 Output artifact

- `intake/s4_research_intake.json`

### 10.6 Suggested output shape

At minimum each target should include:

- `target_id`
- `canonical_label`
- `target_type`
- `source_entity_ids`
- `scene_ids`
- `research_modes`
- `priority`
- `research_needs`
- `notes`

And the intake should include:

- metadata
- source refs
- `scene_index`
- `research_targets`
- optional groups
- intake notes/warnings

### 10.7 Failure modes

Potential issues:

- over-merging distinct targets
- under-merging duplicate targets
- weak target typing
- symbolic targets too vague for discovery
- malformed scene-target mapping

Mitigations:

- schema validation
- report file
- explicit warnings block
- manual reviewability of generated intake

---

## 11. Research planning layer

### 11.1 Why planning is needed

The system should not jump directly from intake to unconstrained search.
A planning artifact is needed to make discovery bounded and parallelizable.

### 11.2 `research_batch_manifest.json`

This artifact should be created before discovery execution.

It should include:

- selected targets
- target priority
- discovery batches
- maximum parallelism
- budget per target / batch
- ordering rules
- expected outputs
- retry policy (if any)

### 11.3 Owner

The sector supervisor should own approval of the manifest.
The actual manifest may be created by the supervisor directly or by a helper step, but responsibility should remain with `sm_s4_asset_research`.

---

## 12. `op_s4_web_investigator`

### 12.1 Mission

Coordinate the discovery phase across one or more target-level research workers.

### 12.2 Important clarification

This actor should be treated as a **discovery coordination layer**, not as proof that nested sub-agent spawning is the required runtime substrate.

For S4 v1:

- it may define worker briefs
- it may define batch discovery plans
- it may summarize discovery outputs
- but it should **not** be assumed to own direct nested runtime spawning in the critical path unless that substrate is explicitly proven later

### 12.3 Input

- `s4_research_intake.json`
- `research_batch_manifest.json`
- target subset / current batch

### 12.4 Responsibilities

1. read the active discovery batch
2. create target-level briefs
3. ensure each worker brief has clear instructions, target scope, output contract, and storage path
4. organize discovery work into bounded target investigations
5. collect or summarize completed discovery outputs
6. produce a batch-level summary artifact

### 12.5 Why this actor should exist even if it does not directly spawn workers

Without this layer, the sector supervisor would need to micromanage every target-level discovery definition directly.
That increases control burden and coupling.

This actor isolates the discovery phase and keeps the sector supervisor focused on sector-level concerns.

### 12.6 Possible implementation substrate

This actor may rely on:

- proven OpenClaw agent invocation patterns already established in S3/B2
- filesystem-written worker briefs
- local helper scripts/skills for organizing discovery batches
- sector supervisor / boundary workflow dispatch of workers using the established runtime model

### 12.7 Major risk

If `op_s4_web_investigator` itself becomes too smart/heavy, it recreates the original bottleneck.

Mitigation:
- constrain it to discovery coordination
- push actual target research downward
- require batch-level summaries rather than giant freeform outputs

---

## 13. `op_s4_target_research_worker`

### 13.1 Mission

Research one target or a small bounded target batch and produce a persisted candidate set with associated file materialization where possible.

### 13.2 Input

A target-level brief should include at minimum:

- `target_id`
- canonical label
- target type
- scene linkage
- target priority
- research modes
- search goals / needs
- storage destination paths
- allowed/expected tools or workflow
- output contract

### 13.3 Responsibilities

The worker should:

1. perform target-focused discovery
2. refine queries as needed within bounded budget
3. open and inspect candidate pages
4. identify candidate assets
5. collect source metadata
6. materialize local files when possible and justified
7. persist a structured candidate set

### 13.4 Local materialization model

Each candidate may be one of:

- `reference_only`
- `preview_asset`
- `materialized_asset`

### 13.5 Why local files matter

S4 is not valuable if it only emits links.
Downstream sectors need to work with:

- local image files
- previews/screenshots
- organized references
- explicit file paths

Therefore the worker must capture files where appropriate.

### 13.6 Recommended target-local storage

Per target folder:

- `target_research_brief.json`
- `candidate_set.json`
- `assets/`
- `previews/`
- `captures/`

### 13.7 Candidate schema should include

At minimum:

- candidate id
- source url
- page title
- source domain
- target id
- linked scene ids
- preliminary classification
- rationale
- confidence
- licensing note
- acquisition mode (`reference_only` / `preview_asset` / `materialized_asset`)
- local file paths where relevant
- timestamp

### 13.8 Notes on downloads

S4 should not indiscriminately mass-download everything.
But it must be able to materialize files when useful and possible.

Important distinction:

- some candidates only deserve a page screenshot or preview
- some deserve the actual local image asset
- some may require downstream controlled acquisition later

### 13.9 Risks

- poor query formulation
- too many irrelevant candidates
- repeated search loops
- over-downloading junk
- inconsistent target-local storage

Mitigations:

- strong target brief
- bounded search budget
- strict output contract
- target-local storage layout
- evaluator pass downstream

---

## 14. `op_s4_candidate_evaluator`

### 14.1 Why this role should remain separate

Evaluation should remain a distinct role.

Reason:
- discovery and evaluation are different cognitive tasks
- researchers are biased toward what they found
- separate evaluation improves quality control
- separate evaluation allows consistent classification across targets

### 14.2 Input

For each target:

- `candidate_set.json`
- access to local files (`assets/`, `previews/`, `captures/`)
- target brief / target metadata
- target goals / research modes

### 14.3 Responsibilities

For each candidate, evaluator should:

1. confirm or correct classification
2. mark one of:
   - `factual_evidence`
   - `visual_reference`
   - `stylistic_inspiration`
   - `reject`
3. evaluate target fitness
4. evaluate downstream usefulness
5. evaluate quality of the local file or preview
6. mark whether the local artifact is directly usable or only contextual
7. identify best candidates and discard low-value noise

### 14.4 Important realism note

The evaluator should not be treated as an infallible visual auditor.

In S4 v1, it is better understood as a **multimodal quality gate** that can judge:

- adequacy to target intent
- provenance coherence
- clarity and usefulness of the reference
- apparent quality of local previews/assets
- downstream utility

It may not perfectly verify every historical or visual truth claim in an absolute sense.
That limitation should be acknowledged explicitly rather than hidden.

### 14.5 Output

Per target:
- `evaluated_candidate_set.json`

### 14.6 Risks

- evaluator overfitting to too little context
- evaluator disagreeing inconsistently across targets
- evaluator being too harsh or too permissive

Mitigations:

- clear evaluation rubric
- focused target brief
- explicit classification definitions
- optional summary report

---

## 15. `op_s4_coverage_analyst`

### 15.1 Mission

Determine whether the research output is sufficient at target level and scene level.

### 15.2 Why this role should remain separate

Coverage analysis should remain distinct from candidate evaluation.

Reason:

- evaluator asks: "how good / valid / useful is this candidate?"
- coverage analyst asks: "is this target / scene sufficiently covered overall?"

These are related but not identical questions.
Collapsing them too early may reduce clarity of the sector.

### 15.3 Input

- `s4_research_intake.json`
- evaluated candidate sets for all targets

### 15.4 Responsibilities

For each target, determine:

- `covered`
- `partially_covered`
- `inspiration_only`
- `unresolved`

For scenes, determine:

- whether the key linked targets are sufficiently covered
- where scene-level gaps remain

### 15.5 Output

- `compiled/coverage_report.json`

### 15.6 Why this should not be left implicit

Without an explicit coverage artifact:
- closure becomes arbitrary
- downstream does not know what is missing
- gaps remain hidden

---

## 16. `op_s4_pack_compiler`

### 16.1 Mission

Consolidate the entire sector output into a final research pack for downstream sectors.

### 16.2 Inputs

- `s4_research_intake.json`
- target-level candidate sets
- target-level evaluated candidate sets
- `coverage_report.json`
- local file paths

### 16.3 Outputs

Primary:
- `compiled/s4_research_pack.json`

Mandatory:
- `compiled/s4_sector_report.md`

### 16.4 Required structure of final pack

The final pack should include:

#### A. metadata
- job/video/account/language/run identifiers
- generation timestamp
- sector status

#### B. target-level results
For each target:
- target metadata
- best factual evidence candidates
- best visual references
- best stylistic inspirations
- rejected summary (optional)
- unresolved notes
- local file paths
- source URLs
- acquisition modes
- confidence
- licensing notes

#### C. scene-level compilation
For each scene:
- linked targets
- recommended assets/references
- coverage state
- unresolved gaps

#### D. storage manifests
At minimum:
- local asset manifest
- preview manifest
- capture manifest

### 16.5 Critical property

This final pack is the primary downstream artifact for S5 and later sectors.

### 16.6 Completion contract note

The final sector completion artifact must reference both:

- `s4_research_pack.json`
- `s4_sector_report.md`

This should be treated as mandatory in sector closure, consistent with the learnings from S3.

---

## 17. Storage model and directory layout

### 17.1 Why storage design matters

S4 output must be filesystem-first.
The value of S4 is lost if outputs are only conversational summaries or scattered artifacts.

### 17.2 Recommended sector-local directory structure

```text
S4/
  intake/
    s4_research_intake.json
    target_builder_report.md

  batches/
    research_batch_manifest.json
    batch_001_discovery_summary.json
    batch_002_discovery_summary.json

  targets/
    rt_001_hotel_quitandinha/
      target_research_brief.json
      candidate_set.json
      evaluated_candidate_set.json
      assets/
        asset_001.jpg
        asset_002.png
      previews/
        preview_001.jpg
      captures/
        capture_001.jpg

    rt_002_joaquim_rolla/
      ...

  compiled/
    coverage_report.json
    s4_research_pack.json
    s4_sector_report.md

  runtime/
    sector_status.json
    checkpoint.json
    dispatch_log.json
```

### 17.3 Path discipline

All persisted candidate records should point to local paths explicitly when a local file exists.

Example fields:
- `local_asset_path`
- `preview_path`
- `capture_path`

### 17.4 Path sanitization

All runtime-created directories and filenames should obey the same operational discipline already learned in S3/B2:

- absolute paths in contracts
- ASCII-safe / sanitized directory naming where required by the runtime environment
- no dependence on fragile special characters in critical dispatch/storage paths

### 17.5 Source-of-truth rule

If a conversational summary conflicts with on-disk artifacts, the disk artifacts win.

---

## 18. Classification taxonomy

S4 must keep these categories distinct:

1. **factual_evidence**
   - candidate is useful as direct factual or historically grounded visual evidence

2. **visual_reference**
   - candidate is visually useful for depiction/reference but not necessarily direct factual evidence

3. **stylistic_inspiration**
   - candidate is useful as mood, language, style, or compositional inspiration

4. **reject**
   - candidate is not sufficiently relevant/usable

Additionally, at coverage level:

- `covered`
- `partially_covered`
- `inspiration_only`
- `unresolved`

These distinctions are essential for downstream clarity.

---

## 19. Files versus links versus previews

### 19.1 Important clarification

Not every valuable candidate will become a fully materialized local file.
But S4 must support file acquisition where needed and possible.

### 19.2 Acquisition modes

Each candidate should explicitly declare one of:

- `reference_only`
- `preview_asset`
- `materialized_asset`

### 19.3 Why this matters

Downstream sectors must know:

- whether an actual file exists locally
- whether only a preview exists
- whether the candidate is only a source pointer and requires later acquisition

---

## 20. Runtime invocation concerns and S3 learnings

### 20.1 Why this section exists

S3 and B2 runtime work already taught important lessons:

- directory/docs alone do not prove an agent is materialized
- runtime truth must be tested with real invocation
- CLI-based invocation via `openclaw agent` was the proven substrate
- state machine + persisted disk state is more reliable than thread-bound assumptions
- outputs on disk must be the operational truth
- session hygiene is mandatory
- checkpoint mirroring matters
- exit codes are not source of truth

S4 must be designed around these realities.

### 20.2 Implication for S4

Every actor in S4 should be designed under the assumption that:

- it is invoked through proven OpenClaw runtime mechanisms
- it must write its outputs to disk deterministically
- handoffs happen through files/checkpoints, not only through chat text
- a successful run means real artifact existence, not just a verbal claim
- sessions must be isolated and cleaned between runs according to the runtime policy

### 20.3 Practical need before implementation

Before S4 implementation, each planned actor must be checked against a preflight similar in spirit to S3/B2 learnings:

- materialization proof
- runtime invocation proof
- schema compliance proof
- output persistence proof
- handoff path proof

### 20.4 Companion docs

The concrete operational details should be frozen in companion docs rather than left implicit here:

- `S4_runtime_control_flow.md`
- `S4_invocation_spec.md`
- contract/schema docs

---

## 21. Open questions / design decisions still to freeze

The following items still need explicit design closure before implementation:

1. exact schema of `s4_research_intake.json`
2. exact schema of `target_research_brief.json`
3. exact schema of `candidate_set.json`
4. exact schema of `evaluated_candidate_set.json`
5. exact schema of `coverage_report.json`
6. exact schema of `s4_research_pack.json`
7. exact rules for when an asset should be materialized versus only previewed
8. exact allowed acquisition methods for target workers
9. exact model choices per actor
10. exact parallelism limits for discovery workers
11. exact runtime dispatch shape between supervisor, investigator artifacts, and target workers
12. whether second-round redispatch exists in v1 or only in later versions
13. whether there should be a dedicated source-specific deep-dive worker in v1

---

## 22. Principal risks

### 22.1 Architectural risks
- too much intelligence concentrated in one actor
- blurred distinction between discovery and evaluation
- overloading supervisor with raw data
- weak boundary between S3 compiled output and S4 intake
- confusing logical hierarchy with runtime invocation hierarchy

### 22.2 Runtime risks
- agent invocation unreliability
- output files not appearing where expected
- worker orchestration failing silently
- schema drift between target worker outputs and evaluator/compiler expectations
- weak session hygiene / context accumulation

### 22.3 Research-quality risks
- low-precision web results
- repeated irrelevant results across workers
- weak symbolic target handling
- too much noisy acquisition
- missing historically relevant material

### 22.4 Data/asset risks
- inconsistent local asset storage
- missing linkage between metadata and actual files
- previews without source traceability
- candidates without adequate local evidence

---

## 23. Mitigations

### 23.1 Against supervisor overload
- intermediate artifacts
- discovery coordinator layer
- separate evaluator
- separate coverage analyst

### 23.2 Against discovery bottlenecks
- target-level workers
- bounded research briefs
- parallelized batches through the proven dispatch substrate

### 23.3 Against weak handoffs
- schema validation at each major artifact
- explicit file paths
- runtime status/checkpoints
- disk-first truth

### 23.4 Against bad downstream usability
- local file materialization model
- acquisition mode field
- scene-level compilation
- target-level best-of lists

### 23.5 Against runtime optimism
- anchor S4 v1 in the proven S3/B2 invocation pattern
- avoid assuming nested spawn trees until explicitly proven
- separate logical coordination from runtime process control

---

## 24. Recommended v1 posture

S4 v1 should be ambitious in architecture but disciplined in scope.

That means:

- keep the rich sector design
- keep separate evaluation
- keep separate coverage analysis
- keep the discovery coordination layer
- use target-level research workers for discovery
- rely on persisted artifacts at every handoff
- avoid pretending that recursive multi-round search is mandatory in v1
- avoid assuming investigator-direct nested spawning in the critical path
- keep one strong pass with strong outputs
- focus on one high-quality first-pass architecture that can run in real runtime

In short:

- **scope reduced in dynamics**
- **not reduced in intelligence or architectural ambition**

---

## 25. Summary

The correct path for S4 is **not** to reduce it to a shallow crawler or a single linear search operator.

The correct path is to preserve the stronger architecture:

- S4 as a real investigation sector
- sector supervisor
- intake builder
- discovery coordinator
- target-level research workers
- separate evaluator
- separate coverage analysis
- final pack compiler
- local file storage and manifests
- explicit artifact-driven state transitions

The real challenge is not conceptual validity.
The challenge is operational viability.

This document's stance is that viability should be achieved by:

- layering responsibilities
- artifact-driven flow
- subordinate worker roles
- strict storage paths
- evaluation separation
- state-machine-compatible orchestration
- runtime discipline inherited from the S3/B2 proven pattern

—not by flattening the intelligence of the sector.
