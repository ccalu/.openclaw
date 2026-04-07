# Branch 5 Research — Tools, Skills & Integrations for Content Factory

**Date:** 26 March 2026  
**Total Research Output:** 4 markdown documents (70 KB)  
**Status:** ✅ Complete, ready for implementation

---

## Quick Navigation

### For Decision-Makers (Lucca)
Start here:
1. **RESEARCH_SUMMARY.md** — 5-minute overview of findings, roadmap, costs
2. **B5_CHEAP_MODEL_STRATEGY.md** — Business case ($5.55 → $0.50–1.50/video)

### For Implementers (Claude Code)
Start here:
1. **B5_SKILL_CONTRACTS.md** — API specs for all 8 tools (copy-paste ready)
2. **B5_TOOLS_RESEARCH.md** — Detailed context on each tool's purpose

### For Operators (Production Manager, Branch Managers)
Reference:
- **B5_CHEAP_MODEL_STRATEGY.md** → "Cost Monitoring Dashboard" section
- **RESEARCH_SUMMARY.md** → "Success Metrics" section

---

## The 4 Documents

| Document | Size | Purpose | Key Takeaway |
|----------|------|---------|--------------|
| **RESEARCH_SUMMARY.md** | 14 KB | Overview + summary | What to build, why, timeline |
| **B5_TOOLS_RESEARCH.md** | 19 KB | Detailed research | 8 concrete tools, 4-phase roadmap |
| **B5_SKILL_CONTRACTS.md** | 24 KB | Implementation specs | JSON schemas for all tools |
| **B5_CHEAP_MODEL_STRATEGY.md** | 13 KB | Cost optimization | Model selection, budget strategy |

---

## What Was Delivered

### 1. Concrete Tools Identified (8 Total)

**Essential (Tier 1):**
- `comfyui-bridge` — Queue ComfyUI jobs locally ($0/image)
- `image-qa` — Score images with Haiku ($0.002/call)
- `browser-animator` — img2video via Freepik/Higgsfield or Selenium ($0–1/image)

**High-Value (Tier 2):**
- `image-director-brief` — B3 → B5 glue
- `portrait-consistency-check` — Character validation
- `cost-tracker-b5` — Real-time budget visibility
- `lora-selector` — Auto-select LoRAs per scene
- `animation-fallback-handler` — Handle timeouts gracefully

### 2. Communication Contracts (5 Total)

JSON schemas for agent-to-agent communication:
- `generation_request.json` — B3 → B5 (what to generate)
- `image_qa_report.json` — B5 → B6 (quality verdict)
- `animation_output_spec.json` — B5 → B6 (video output)
- Plus full OpenClaw skill signatures (input/output)

### 3. Model Strategy

**Per-agent model selection:**
- Haiku for formatting + QA ($0.002/call, 96% cheaper than Sonnet)
- Flash Lite for vision (free tier)
- ComfyUI local for generation ($0, already deployed)
- Selenium for browser automation ($0, fallback for img2video)

**Cost impact:** $5.55/video → $0.50–1.50/video (**85% savings**)

### 4. Implementation Roadmap

**4 phases, 10 days total effort:**

- **Phase 1 (2 days):** comfyui-bridge + image-qa → autonomous generation
- **Phase 2 (2 days):** image-director-brief + consistency checks → full coordination
- **Phase 3 (3 days):** browser-animator → img2video workflow
- **Phase 4 (2 days):** monitoring + cost tracking → fully instrumented

---

## Key Decisions Made

| Decision | Rationale | Document |
|----------|-----------|----------|
| Freepik/Higgsfield API unknown; use Selenium fallback first | Faster to implement; no blocker | RESEARCH_SUMMARY |
| Use Haiku for QA instead of Sonnet | 96% cheaper, sufficient for scoring | B5_CHEAP_MODEL_STRATEGY |
| ComfyUI local as primary (>95% target) | Already deployed on M1, $0/image | B5_CHEAP_MODEL_STRATEGY |
| Static image fallback if animation fails | Keeps pipeline flowing, acceptable | RESEARCH_SUMMARY |
| Batch processing for QA (5–10 images at once) | Reduces per-image overhead | B5_TOOLS_RESEARCH |

---

## Critical Open Questions

These need answers from Lucca or Micha **before starting Phase 1**:

1. **Does Freepik have a partner API?** (impacts animation cost)
2. **Does Higgsfield have an API?** (alternative to Freepik)
3. **What's the actual Gemini free tier quota?** (impacts QA cost)
4. **What QA score threshold = approved?** (affects remediation rate)
5. **Can ComfyUI handle 95%+ of requests locally?** (affects OpenRouter fallback budget)

**See:** B5_CHEAP_MODEL_STRATEGY.md → "Open Questions & Decisions Needed"

---

## Success Criteria

By end of Phase 4 (Week 8):

| Metric | Target | Status |
|--------|--------|--------|
| Cost per video | <$1.00 (was $5.55) | ✅ Designed |
| B5 fully autonomous | Yes (zero manual steps) | ✅ Designed |
| Image QA approval rate | >85% | ✅ Framework ready |
| Local execution ratio | >95% | ✅ Strategy defined |
| Animation success rate | >90% | ✅ Fallback planned |

---

## How to Hand Off to Claude Code

1. Give Claude Code the **B5_SKILL_CONTRACTS.md** file
2. Say: "Build these 8 tools in this order: comfyui-bridge, image-qa, image-director-brief"
3. For each tool, Claude Code has:
   - Full function signature (input/output schemas)
   - Example requests/responses
   - Error handling cases
   - Context from B5_TOOLS_RESEARCH.md

4. Integration test: B3 visual_plan → comfyui-bridge → image_qa_report ✅

---

## Project Structure (Created)

```
C:\Users\User-OEM\.openclaw\workspace\research-haiku\
└── b5-tools-skills/
    ├── README.md                          ← You are here
    ├── RESEARCH_SUMMARY.md                ← Start here (5 min read)
    ├── B5_TOOLS_RESEARCH.md               ← Full research (30 min read)
    ├── B5_SKILL_CONTRACTS.md              ← Implementation spec (45 min read)
    └── B5_CHEAP_MODEL_STRATEGY.md         ← Cost optimization (25 min read)
```

---

## Related Documentation (Existing Project)

**Reference, do not modify:**
- `C:\Users\User-OEM\Desktop\content-factory\auto_content_factory\docs\04_BRANCH_ARCHITECTURE.md` — B5 structure
- `C:\Users\User-OEM\Desktop\content-factory\auto_content_factory\docs\06_MODEL_STRATEGY.md` — General model selection
- `C:\Users\User-OEM\Desktop\content-factory\auto_content_factory\docs\07_BRAINDUMP_OPENCLAW.md` — Context on KMS, ComfyUI

---

## Questions?

- **For strategy/business logic:** See RESEARCH_SUMMARY.md + B5_CHEAP_MODEL_STRATEGY.md
- **For implementation details:** See B5_SKILL_CONTRACTS.md + B5_TOOLS_RESEARCH.md
- **For cost modeling:** See B5_CHEAP_MODEL_STRATEGY.md → "Cost Projection"
- **For timeline:** See RESEARCH_SUMMARY.md → "Implementation Roadmap"

---

**Research completed by Haiku subagent on 26 Mar 2026.**  
**Status: ✅ Ready for handoff to Claude Code and Lucca.**
