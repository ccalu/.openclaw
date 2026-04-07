# Branch 1 (Pre-Production) Research Summary

**Research Date:** 2026-03-26  
**Researcher:** Haiku Subagent  
**Scope:** OpenClaw skills, tools, integrations, and cheap-model workflows for B1  
**Status:** Complete

---

## What We Found

### Local Documentation Read ✅
- **Architectural docs:** Context, pipeline map, branch architecture, hierarchy, model strategy, OpenClaw braindump
- **Code inspection:** script_processor.py, parallel_screenplay.py (v3 existing implementation)
- **Skipped:** Knowledge-base course content (already digested; not tool-specific)

**Key finding:** B1 currently exists as monolithic Python code in v3. For OpenClaw, it needs to be decomposed into modular agents + reusable skills.

### 1. Concrete Tools & Skills to Build ✅

**Tier 1 (Critical):**
1. **scene-bible-generator** — Accepts raw script, outputs structured scene_bible.json
2. **script-validator** — Pre-division quality gate (encoding, placeholders, sanity checks)
3. **continuity-extractor** — Pulls entity registry (characters, locations, props) for downstream branches

**Tier 2 (Nice-to-have):**
4. narrative-arc-analyzer — Validates pacing and emotional coherence
5. scene-rebalancer — Auto-fix uneven scene lengths
6. language-formatter — TTS-specific text optimization

**Not as skills (keep in agent prompts):**
- screenplay-divider (too account-specific, variable prompts)
- scene-formatter (TTS-specific, owned by B2)

**Recommended tools (not skills):**
- KMS Client Wrapper (async key management for GPT-4.1-mini calls)
- Script Source Adapter (abstract fetching from Google Sheets, queue, etc.)
- Validation Report Formatter (normalize output across branches)

---

### 2. Structured Artifacts & Contracts ✅

**Three core artifacts defined:**

1. **scene_bible.json** (20-30 KB per video)
   - Complete scene list with full metadata (entities, narrative beats, timings)
   - Schema v1.0 with version control
   - Immutable after handoff; read by all downstream branches (B2-B9)

2. **continuity_extract.json** (5-10 KB per video)
   - Lightweight entity registry (characters, locations, props)
   - Cross-references per scene
   - Optimized for B3/B4 queries ("all locations in scene 5?")

3. **script_validation_report.json**
   - Pre-division quality gate
   - Checks: encoding, placeholders, language detection, narrative structure
   - Used by B1 to decide whether to proceed or halt

**Storage:** `auto_content_factory/shared/scene_bible/{video_id}/`

**Governance:** B1 is schema owner; backward compatibility first; versioning required for evolution.

---

### 3. Cheap Model Workflow ✅

**Recommended model routing:**

| Task | Model | Cost | Why |
|------|-------|------|-----|
| Script validation | Haiku 4.5 | $0.005 | Lightweight checks |
| Screenplay division | GPT-4.1-mini (KMS) | $0.10 | Proven, balanced |
| Continuity extraction | Haiku 4.5 or Ollama | $0.008 (or $0) | Rule-based extraction |
| Quality check | Haiku 4.5 | $0.005 | Scoring |
| Arc validation (conditional) | GPT-4.1-mini | $0.03 | Only if score < 0.85 |

**Total per video:** $0.118 (happy path) to $0.148 (with optional arc check)

**Monthly budget (160 videos):** ~$20-23 for B1 tasks alone (excluding 5% KMS overhead)

**Scaling:** Cost scales linearly; no bottlenecks below 500+ videos/week

**Optimization strategies:**
- Batch validation (10 scripts at once) = 40% cost savings
- Skip arc validation for high-confidence accounts = $0.03 savings per video
- Use local Ollama for extraction = $0.008 savings (if failures < 1%)
- Implement prompt caching after system stabilizes = $0.05 savings per video long-term

---

### 4. Implementation Roadmap ✅

**4-6 week timeline (19 days effort, 25 calendar days)**

**Phase breakdown:**
- **Week 0:** Directory setup (0.5d)
- **Week 1:** JSON schemas + Pydantic models (2.5d)
- **Week 1-2:** Implement 3 skills (4.5d)
- **Week 2-3:** Create 5 OpenClaw agents (4.5d)
- **Week 2:** KMS integration + testing (2d)
- **Week 3:** End-to-end testing (2d)
- **Week 4:** Production readiness (2.5d)
- **Week 4:** Handoff & training (1d)

**Owner:** Claude Code (implementation) + Tobias (oversight)

**Success criteria:**
- 100% of valid scripts → schema-compliant scene_bible.json
- Invalid scripts fail gracefully
- continuity_extract.json 95%+ accurate
- Cost < $0.20/video
- Latency < 2 min/script
- Production Manager can invoke B1

---

## File Structure Created

All research notes saved to: `C:\Users\User-OEM\.openclaw\workspace\research-haiku\b1-tools-skills\`

1. **01_LOCAL_DOCS_READ.md**
   - What docs were read, what was skipped, why
   - Current B1 state in v3
   - Missing pieces + opportunities
   - Data contracts currently in v3

2. **02_CONCRETE_TOOLS_SKILLS.md**
   - 6 skills (3 critical + 3 optional)
   - Why certain things shouldn't be skills
   - 3 recommended tools
   - All 4 core schemas (Pydantic/JSON)
   - Implementation priority (weeks 1-4)

3. **03_STRUCTURED_ARTIFACTS.md**
   - Complete scene_bible.json schema (20KB example)
   - continuity_extract.json schema with examples
   - validation_report.json schema
   - Artifact versioning & governance rules
   - Storage location + access patterns
   - Downstream dependency contracts (B2-B9)

4. **04_CHEAP_MODEL_WORKFLOW.md**
   - Model selection matrix per task
   - Cost breakdown: $0.118-0.148 per video
   - Monthly budget: $20-47 (160-320 videos)
   - Optimization strategies (4 specific techniques)
   - Cost monitoring via B10
   - Emergency cost controls
   - Long-term paths (fine-tuning, hybrid extraction, prompt caching)

5. **05_IMPLEMENTATION_ROADMAP.md**
   - 7 phases with specific tasks + effort estimates
   - Phase 0-1: Setup + schemas (2.5d)
   - Phase 2-3: Skills + agents (9d)
   - Phase 4-5: KMS + testing (4d)
   - Phase 6-7: Production + handoff (3.5d)
   - Success criteria checklist
   - Risk mitigation table
   - Next steps post-Phase 7

6. **RESEARCH_SUMMARY.md** (this file)
   - High-level overview
   - What was found + why it matters
   - Files created + structure
   - Immediate recommendations for Tobias

---

## Key Insights

### 1. B1 is the Gateway
Everything downstream depends on B1 output. **Investment in clean schemas + validation now saves debugging downstream later.**

### 2. Current v3 Implementation is Monolithic
`parallel_screenplay.py` mixes KMS rotation, batch orchestration, and GPT calls. **Decomposition into OpenClaw skills is essential for reusability and testability.**

### 3. Continuity Extraction is Missing
B3 (Visual Planning) will need character/location/prop lists per scene. **B1 must own this as a core output.**

### 4. Model Routing is Practical
- Haiku for validation/extraction ($0.005-0.008)
- GPT-4.1-mini for screenplay ($0.10)
- Ollama fallback for extraction ($0 local)

**Result: $0.13-0.15 per video is achievable without compromise.**

### 5. Schemas Must Be Versioned
As the system evolves, downstream branches will depend on specific schema versions. **Start with v1.0 and plan for v1.1, v2.0 updates.**

---

## Immediate Recommendations for Tobias

### 1. Greenlight & Prioritize
✅ Approve the 4-6 week timeline  
✅ Assign Claude Code to implement  
✅ Allocate KMS resources for testing  

### 2. Define Account-Specific Overrides
- Currently, screenplay prompts are generic
- Different accounts (WWII vs dark history) may need different scene constraints
- **Decision needed:** Store in `accounts/{code}/screenplay_config.json`?

### 3. Plan for Production Manager Integration
- B1 will exist; Production Manager needs to invoke it
- **Decision needed:** REST API? Function call? Telegram topic?
- Recommend: Production Manager has method `invoke_b1(video_id, account_code, language)` → returns scene_bible.json path

### 4. Validate with Real Scripts
- Once Phase 5 (testing) is done, run B1 on 3-5 existing scripts
- Check that scene_bible.json + continuity_extract.json make sense
- Manual spot check: Are aliases correct? Are emotional tones appropriate?

### 5. Plan for B2/B3 Integration
- B2 (Audio) will read scene_bible.json and validate
- B3 (Visual Planning) will read continuity_extract.json
- **Coordination needed:** Who owns the handoff? What's the SLA for scene_bible.json availability?

---

## Questions to Answer Before Starting Implementation

1. **Script sources:** Where does B1 fetch scripts from? (Google Sheets? Queue? Webhook?)
2. **Account config:** How are per-account overrides stored? (accounts/{code}/*.yaml?)
3. **KMS access:** Can we add OpenClaw agents to KMS whitelist?
4. **Storage:** Use `auto_content_factory/shared/` or centralized storage (Google Drive, S3)?
5. **Approval gates:** Does scene_bible.json need human approval before B2 processing?
6. **SLA:** Max time from script fetch to scene_bible.json available?
7. **Fallback:** If B1 fails, should production halt or continue with v3 fallback?

---

## Conclusion

**B1 Pre-Production is buildable, modular, and cost-effective.** The research provides:
- ✅ Clear skill definitions (scene-bible-generator, script-validator, continuity-extractor)
- ✅ Formal schemas (scene_bible.json, continuity_extract.json, validation_report.json)
- ✅ Cheap model workflow ($0.13-0.148/video)
- ✅ 4-6 week implementation roadmap with success criteria

**Next step:** Claude Code begins Phase 0-1 (directory setup + schemas). Target completion: Week 4 with full handoff to Production Manager.

---

**Research completed:** 2026-03-26 14:37 GMT-3  
**Files created:** 6 markdown files, ~75 KB total
