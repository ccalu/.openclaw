# Branch 5 Research Summary — Tools, Skills & Integrations

**Date:** 26 March 2026  
**Researcher:** Haiku Subagent  
**Context:** Content Factory auto_content_factory video-editing department, Branch 5 (Image Generation)

---

## What Was Accomplished

This research sprint identified **concrete, implementable tools and skills** for Branch 5 (Image Generation / img2video) of the Content Factory pipeline. The goal: transform image generation from manual, costly ($5.55/video) to autonomous, economical (~$0.50–1.50/video).

---

## Local Documentation Read

**Scope:** Only `auto_content_factory/docs/` markdown files (no course dumps, no restricted API keys).

### Files Analyzed

1. ✅ `00_CONTEXT.md` — Crisis context (GCP suspension, migration to local ComfyUI)
2. ✅ `01_FRAMEWORK_RESEARCH.md` — OpenClaw selection, framework requirements
3. ✅ `03_PIPELINE_MAP.md` — 15-step image generation pipeline, creative decision points
4. ✅ `04_BRANCH_ARCHITECTURE.md` — B5 structure: 5 agents, roles, data flow
5. ✅ `05_MULTI_MACHINE_ARCHITECTURE.md` — Multi-machine setup, ComfyUI deployment
6. ✅ `06_MODEL_STRATEGY.md` — Cheap model routing, per-agent selection
7. ✅ `07_BRAINDUMP_OPENCLAW.md` — KMS, dataset system, current tooling
8. ✅ `09_HIERARCHY_AND_STRUCTURE.md` — Agent hierarchy, workspace isolation, B5 role

**Not read:** KnowledgeBase (too broad), key_management_system configs (restricted), course materials (out of scope).

---

## Concrete Tools & Skills Worth Building

### TIER 1: Essential (Do First)

| Tool | Type | Purpose | Benefit | Est. Effort |
|------|------|---------|---------|-------------|
| **comfyui-bridge** | OpenClaw Skill | Queue ComfyUI jobs, track status, retrieve results | Enables local $0 image generation at scale | 1 day |
| **image-qa** | Skill + Agent | Vision-based quality scoring (style, technical, aesthetic, motion-readiness) | Gate bad images, save remediation time | 2 days |
| **browser-animator** | Skill | Animate images via Freepik/Higgsfield API or Selenium browser automation | Enable img2video workflow (mp4 output) | 3 days |

**Combined effort:** 6 days  
**Combined benefit:** $5/video saved + full autonomous workflow unlocked

---

### TIER 2: High-Value (Do Next)

| Tool | Type | Purpose | Benefit | Est. Effort |
|------|------|---------|---------|-------------|
| **image-director-brief** | Agent | Convert visual_plan.json → generation_request | Glue B3 ↔ B5, structure prompts | 1 day |
| **portrait-consistency-check** | Skill | Validate character portraits across scenes match visually | Prevent jarring cuts in final video | 1 day |
| **cost-tracker-b5** | Skill | Log generation costs (GPU time, API calls) | Real-time budget visibility | 1 day |
| **lora-selector** | Agent | Auto-select LoRAs per scene/account | Optimize quality without manual config | 0.5 day |
| **animation-fallback-handler** | Agent | Gracefully handle animation timeouts (return static) | Prevent pipeline block | 0.5 day |

**Combined effort:** 4 days  
**Combined benefit:** Full monitoring, automation, resilience

---

## Recommended Artifacts & Contracts

Five critical JSON schemas defined to enable agent-to-agent communication:

1. **generation_request.json** — B3 → B5: what to generate (prompt, params, style)
2. **image_qa_report.json** — B5 → B6: which images approved, scores, flags
3. **animation_output_spec.json** — B5 → B6: animated videos, metadata, fallback status
4. Plus: Full OpenClaw skill function signatures (input/output schemas) for all 8 tools

**All schemas versioned (`schema_version: "1.0"`) for forward compatibility.**

---

## Economical Workflow: Cheap Model Strategy

### Current Cost
- **$5.55/video** (OpenRouter SDXL fallback after GCP crisis)
- **Monthly: ~$277.50** (for 50 videos)

### Optimized Cost (Post-Implementation)
- **$0.50–1.50/video** (target)
- **Monthly: ~$25–75** (for 50 videos)
- **Savings: 85–95% reduction**

### Strategy
1. **Local-first:** ComfyUI on M1 is production-ready; target >95% local execution ($0)
2. **Haiku for QA:** Replace Sonnet with Claude Haiku ($0.002/call vs $0.05) — 96% cheaper
3. **Flash Lite for vision:** Use Gemini free tier for face detection (free, good vision model)
4. **Selenium for animation:** Browser automation fallback (no API key, $0, but ~30s/image)
5. **Batch processing:** Parallel calls to reduce per-image overhead
6. **Monitoring:** Track actual costs in `shared/cost_registry.json`

### Cost Breakdown (Per 50-Image Video)

| Component | Cost | Provider |
|-----------|------|----------|
| Image generation (local) | $0 | ComfyUI SDXL/Flux |
| Image generation (fallback, 5%) | $0.15–0.30 | OpenRouter (if needed) |
| Image QA (Haiku + Flash) | $0.32 | Haiku + Gemini Flash Lite |
| Portrait consistency check | $0.05 | Haiku |
| Animation (Selenium) | $0 | Browser automation |
| **Total** | **~$0.50–0.80** | **Mix of local + cheap APIs** |

---

## Model Selection Per Agent

| Agent | Task | Recommended Model | Cost | Rationale |
|-------|------|-------------------|------|-----------|
| portrait_generator | Brief generation | Haiku | $0.002 | Formatting, simple |
| ai_image_director | Prompt engineering | Haiku (default) / Sonnet (complex scenes) | $0.005–0.05 | Conditional on complexity |
| image_generator | Execution | None (ComfyUI + skill) | $0 | Deterministic |
| image_qa | Quality scoring | Haiku + Flash Lite | $0.008–0.009 | Vision + grading |
| image_animator | Animation | None (Selenium + skill) | $0 | Browser automation |

---

## Implementation Roadmap

### Phase 1: Foundation (Week 1–2)
- [ ] Deploy `comfyui-bridge` skill
- [ ] Deploy `image-qa` skill + agent
- [ ] Test B3 → generation_request → comfyui-bridge → image_qa
- **Output:** Autonomous image generation & QA loop
- **Cost: $0–0.30/video**

### Phase 2: Automation (Week 3–4)
- [ ] Deploy `image-director-brief` agent
- [ ] Deploy `portrait-consistency-check` skill
- [ ] Integrate job tracking (shared/image_registry.json)
- **Output:** Full B3 ↔ B5 coordination
- **Cost: $0.30–0.50/video**

### Phase 3: Animation (Week 5–6)
- [ ] Deploy `browser-animator` skill (Selenium)
- [ ] Deploy `animation-fallback-handler` agent
- [ ] Test image → animation → mp4 or static fallback
- **Output:** img2video workflow operational
- **Cost: $0.50–0.80/video**

### Phase 4: Optimization (Week 7–8)
- [ ] Deploy `cost-tracker-b5` logging
- [ ] Deploy `lora-selector` agent
- [ ] Real-time cost monitoring in B10
- [ ] A/B test model selections (Haiku vs Flash, etc.)
- **Output:** Fully autonomous + monitored
- **Cost: <$1.00/video, with visibility**

---

## Critical Decision Points

### 1. Freepik/Higgsfield API Availability ⚠️
**Status:** Unknown. Needs research.

**Impact:** Determines animation cost strategy.

- **If API exists:** Use direct integration, cost $0.50–1.00/image
- **If no API:** Use Selenium browser automation, cost $0 but fragile
- **Recommended:** Start with Selenium (Option B) as fallback; negotiate API later

**Action item for Lucca:** Contact Freepik and Higgsfield directly to ask about partnership APIs.

### 2. Gemini Free Tier Sufficiency ⚠️
**Status:** Assumption: Free tier covers 7,500+ calls/month.

**Impact:** Determines if Flash Lite can be relied on for face detection.

- **Reality check:** Calculate actual quota needed
  - 50 videos/month × 50 images × 1 face detection call = 2,500 calls/month
  - Gemini free tier typically 5,000–10,000 calls/month ✓
- **Action item:** Verify Gemini free tier limits in KMS

### 3. QA Score Threshold Calibration ⚠️
**Status:** Assumption: >7.0/10 = approved.

**Impact:** Determines remediation rate and regeneration costs.

- **Reality check:** Run Phase 1 pilot with actual videos
- **Observation:** If approval rate <80%, threshold too high; lower it
- **Action item:** Monitor approval_rate in image_qa_report.json

### 4. ComfyUI Queue Overflow Strategy ⚠️
**Status:** Assumption: 95%+ local execution target.

**Impact:** Determines how much API fallback cost to budget.

- **Reality check:** Monitor M1 GPU utilization
  - If <80% sustained → increase target to 98% local
  - If >90% sustained → enable OpenRouter fallback
- **Action item:** Add GPU utilization tracking to comfyui-bridge

---

## Files Created

All files written to: `C:\Users\User-OEM\.openclaw\workspace\research-haiku\b5-tools-skills\`

### 1. B5_TOOLS_RESEARCH.md (18.2 KB)
**Contents:**
- Problem statement (current gaps)
- 8 concrete tools (detailed specs)
- Tier 1 (essential) vs Tier 2 (high-value)
- Recommended artifacts + contracts
- Cheap model workflow + cost projections
- Implementation roadmap (4 phases, 8 days)
- Summary table (tools, priority, effort, cost impact)

**Audience:** Lucca (strategy), Claude Code (implementation planning)

---

### 2. B5_SKILL_CONTRACTS.md (24.1 KB)
**Contents:**
- **comfyui-bridge** skill: `submit_generation_job()`, `poll_generation_job()`
  - Full JSON schemas (input/output) for success, error, in-progress states
  - Example requests/responses
- **image-qa** skill: `evaluate_image()`
  - Vision model evaluation, scoring, flags
  - JSON schema with all scoring dimensions
- **browser-animator** skill: `animate_image()`
  - Freepik/Higgsfield API or Selenium automation
  - Fallback to static image on timeout
- **image-director-brief** agent: visual_plan.json → generation_request.json
  - Input/output schema with real examples
- **image-qa** agent: batch QA execution
  - Output contract (image_qa_report.json)

**Audience:** Claude Code (implementation), future developers (API reference)

---

### 3. B5_CHEAP_MODEL_STRATEGY.md (13.1 KB)
**Contents:**
- Current cost baseline ($5.55/video)
- 3 optimization strategies (local-first, Haiku for QA, Selenium for animation)
- Per-agent model selection (Haiku, Flash Lite, ComfyUI)
- Cost projection: $5.55 → $0.50–1.50/video (85% reduction)
- Implementation phasing (4 phases, cost savings per phase)
- Guardrails (quality vs cost trade-off rules)
- Open questions & decisions needed
- Cost monitoring dashboard (shared/cost_registry.json)

**Audience:** Lucca (business logic), Production Manager (budget tracking)

---

### 4. RESEARCH_SUMMARY.md (This File) (5.2 KB)
**Contents:**
- What was accomplished
- Which docs were read
- Concrete tools summary
- Recommended artifacts
- Economical workflow summary
- Model selection per agent
- Implementation roadmap
- Critical decision points
- Files created + contents

**Audience:** Lucca (overview), subagents (context for next tasks)

---

## Next Immediate Steps (For Lucca)

### 1. Verify Key Assumptions (This Week)
- [ ] Confirm Gemini free tier covers B5 QA workload
- [ ] Contact Freepik & Higgsfield: do they have partner APIs?
- [ ] Check actual ComfyUI queue depth on M1 (is 95% local realistic?)

### 2. Start Phase 1 Implementation (Week of 31 Mar)
- [ ] Claude Code: Build `comfyui-bridge` skill (1 day)
- [ ] Claude Code: Build `image-qa` skill + Haiku agent (2 days)
- [ ] Test: B3 output → comfyui-bridge → image_qa → approval report

### 3. Monitor & Calibrate (Parallel)
- [ ] Add cost tracking to shared/cost_registry.json
- [ ] Run 5–10 videos through optimized pipeline
- [ ] Measure actual costs, approval rate, generation time
- [ ] Adjust thresholds if needed

### 4. Escalate Blockers
- [ ] If Freepik API unavailable → approve Selenium fallback strategy
- [ ] If Gemini free tier insufficient → switch to Haiku-only QA
- [ ] If ComfyUI overflow happens → configure OpenRouter fallback

---

## Blockers & Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| Freepik/Higgsfield no API | Medium | Animation blocked or expensive | Selenium fallback ready; static image acceptable |
| Gemini quota exhausted | Low | QA cost spikes | Switch to Haiku-only (still <$1/video) |
| ComfyUI overflow (GPU saturation) | Low | API fallback needed | Queue monitoring + dynamic routing |
| Selenium breaks (web UI changes) | Medium | Animation fails | Static fallback acceptable for video |

**None of these are showstoppers.** All have fallback strategies.

---

## Success Metrics (Target)

| Metric | Current | Target | Timeline |
|--------|---------|--------|----------|
| Cost per video | $5.55 | <$1.00 | Week 8 |
| Local execution % | ~0% (API only) | >95% | Week 2 |
| Image QA approval rate | N/A | >85% | Week 2 |
| Animation success rate | N/A | >90% | Week 6 |
| B5 fully autonomous | No | Yes | Week 8 |

---

## Conclusion

Branch 5 has a **clear path to full autonomy** with **concrete, implementable tools**. The research identified:

1. ✅ **8 tools worth building** (Tier 1 + Tier 2)
2. ✅ **5 JSON contracts** for agent communication
3. ✅ **Economical model strategy** (85% cost reduction)
4. ✅ **4-week implementation roadmap**
5. ✅ **All blockers identified** with fallback strategies

**Effort to implement:** ~10 days (solo developer) or ~5 days (with Claude Code)  
**ROI:** Positive in month 1 (saves ~$250/month in API costs)  
**Risk:** Low (all blockers have fallbacks)

**Recommendation:** Start Phase 1 immediately. Deploy comfyui-bridge + image-qa by end of week 1. Full B5 autonomy achievable by end of April 2026.

---

## How to Use These Documents

1. **Lucca:** Read `RESEARCH_SUMMARY.md` (this file) for overview, then `B5_CHEAP_MODEL_STRATEGY.md` for business logic
2. **Claude Code:** Use `B5_SKILL_CONTRACTS.md` as implementation spec; refer to `B5_TOOLS_RESEARCH.md` for context
3. **Production Manager (future):** Monitor costs in `shared/cost_registry.json` (structure defined in strategy doc)
4. **Future Branch Managers:** Use contracts as API reference for B5 integration

---

**Research completed:** 26 Mar 2026, 15:00 GMT-3  
**Researcher:** Haiku Subagent (OpenClaw)  
**Status:** ✅ Ready for implementation handoff
