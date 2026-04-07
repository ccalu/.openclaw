# Branch 1 Research Index

**Research Scope:** Tools, skills, integrations, and cheap-model workflows for Branch 1 (Pre-Production) of Content Factory video-editing department using OpenClaw.

**Researcher:** Anthropic Haiku Subagent  
**Date:** 2026-03-26  
**Total Size:** ~66 KB across 6 documents  
**Status:** Complete

---

## Document Guide

### 1. **RESEARCH_SUMMARY.md** (START HERE)
**9.3 KB | ~15 min read**

High-level overview of all research findings. Includes:
- What was found in local docs + code
- Concrete tools/skills recommendations
- Structured artifacts overview
- Cheap model workflow summary
- Implementation roadmap snapshot
- Key insights + immediate recommendations for Tobias

**Read this first if:** You want the executive summary

---

### 2. **01_LOCAL_DOCS_READ.md**
**5.5 KB | ~10 min read**

Documentation of local files analyzed. Includes:
- Which files were read from Content Factory project
- Which files were skipped (and why)
- Current B1 state in v3 pipeline
- Missing pieces and opportunities
- Data contracts expected by downstream branches

**Read this if:** You want to understand the baseline state

---

### 3. **02_CONCRETE_TOOLS_SKILLS.md**
**10.3 KB | ~20 min read**

Actionable list of tools and skills to build. Includes:
- 6 specific skills (3 critical + 3 optional) with detailed specs
- Why certain things should NOT be skills (decision logic)
- 3 recommended tools (not skills)
- Integration points with existing v3 code
- Complete Pydantic schemas for 4 core data structures
- Implementation priority (weeks 1-4)
- Cost-per-task breakdown

**Read this if:** You're planning development sprints

---

### 4. **03_STRUCTURED_ARTIFACTS.md**
**13.7 KB | ~25 min read**

Complete schema definitions and governance. Includes:
- Full scene_bible.json schema (20KB example)
- continuity_extract.json schema (entity registry)
- validation_report.json schema (quality gates)
- Why artifacts are separate vs combined
- Versioning and backward compatibility rules
- Storage location and access patterns
- Downstream dependency contracts (what B2-B9 expect)
- Governance model (B1 owns schemas)

**Read this if:** You're designing data contracts

---

### 5. **04_CHEAP_MODEL_WORKFLOW.md**
**9.6 KB | ~20 min read**

Cost optimization and model routing. Includes:
- Model selection per task (Haiku, GPT-4.1-mini, Ollama)
- Cost breakdown: $0.118-0.148 per video
- Monthly budget: $20-47 for 160-320 videos
- 4 specific optimization strategies
- Cost monitoring via B10 (Monitoring branch)
- Emergency cost controls (circuit breakers)
- Long-term paths (fine-tuning, hybrid extraction, prompt caching)

**Read this if:** You're concerned about costs or scaling

---

### 6. **05_IMPLEMENTATION_ROADMAP.md**
**17.8 KB | ~35 min read**

Detailed 4-6 week implementation plan. Includes:
- 7 phases with specific tasks
- Effort estimates per task (days)
- Deliverables at each phase
- Phase 0: Directory setup (0.5d)
- Phase 1: JSON schemas (2.5d)
- Phase 2: Skills implementation (4.5d)
- Phase 3: OpenClaw agent integration (4.5d)
- Phase 4: KMS integration (2d)
- Phase 5: End-to-end testing (2d)
- Phase 6: Production readiness (2.5d)
- Phase 7: Handoff & training (1d)
- Success criteria checklist
- Risk mitigation table
- Questions to answer before starting

**Read this if:** You're planning the implementation sprint

---

## Quick Reference: Key Decisions

### What to Build (Tier 1 = Must Have)
1. ✅ **scene-bible-generator** skill — Core B1 function
2. ✅ **script-validator** skill — Quality gate before processing
3. ✅ **continuity-extractor** skill — Enables B3/B4

### What Models to Use
- **Validation/Extraction:** Haiku ($0.005-0.008 each)
- **Screenplay division:** GPT-4.1-mini (via KMS, $0.10)
- **Conditional arc check:** GPT-4.1-mini if quality score < 0.85 ($0.03)
- **Local fallback:** Ollama Qwen-3.5 (free)

### Cost Target
**$0.13-0.15 per video** (screenplay division dominates at $0.10)

### Timeline
**4-6 weeks** (19 days effort spread over 25 calendar days)

### Core Artifacts
1. **scene_bible.json** (20-30 KB) — Complete scene data, read by all branches
2. **continuity_extract.json** (5-10 KB) — Entity registry, optimized for lookups
3. **validation_report.json** — Quality gate (pre-division)

---

## How to Use This Research

### For Claude Code (Implementation)
1. Read **01_LOCAL_DOCS_READ.md** → understand baseline
2. Read **02_CONCRETE_TOOLS_SKILLS.md** → get precise specs
3. Read **03_STRUCTURED_ARTIFACTS.md** → design schemas
4. Follow **05_IMPLEMENTATION_ROADMAP.md** → implement phase-by-phase

### For Tobias (Oversight)
1. Read **RESEARCH_SUMMARY.md** (this file) → overview
2. Read **02_CONCRETE_TOOLS_SKILLS.md** → understand deliverables
3. Read **04_CHEAP_MODEL_WORKFLOW.md** → budget approval
4. Read **05_IMPLEMENTATION_ROADMAP.md** → timeline + risks
5. Keep **03_STRUCTURED_ARTIFACTS.md** as reference for schema decisions

### For Production Manager (Future Integration)
1. Read **02_CONCRETE_TOOLS_SKILLS.md** → what B1 outputs
2. Read **03_STRUCTURED_ARTIFACTS.md** → schema format
3. Reference **01_LOCAL_DOCS_READ.md** → baseline state
4. (After implementation) Read **RUNNING_B1.md** → how to invoke

---

## Critical Questions Answered

### "What skills should we build?"
→ **02_CONCRETE_TOOLS_SKILLS.md** (6 skills ranked by priority)

### "What data structures should B1 output?"
→ **03_STRUCTURED_ARTIFACTS.md** (3 schemas with full examples)

### "How much will B1 cost per video?"
→ **04_CHEAP_MODEL_WORKFLOW.md** ($0.13-0.15 per video, includes cost breakdown)

### "How long will implementation take?"
→ **05_IMPLEMENTATION_ROADMAP.md** (4-6 weeks, 19 days effort)

### "What's the current baseline state?"
→ **01_LOCAL_DOCS_READ.md** (v3 monolithic code, missing continuity extraction)

### "What should we do first?"
→ **RESEARCH_SUMMARY.md** → immediate recommendations section

---

## Key Files to Create / Modify

Based on this research, the following files/directories need to be created:

### New Directories
```
auto_content_factory/
├── agents/branches/01_pre_production/
│   ├── agents/
│   │   ├── script_fetcher/
│   │   ├── screenplay_divider/
│   │   ├── scene_bible_builder/
│   │   └── continuity_extractor/
│   └── docs/
├── skills/
│   ├── scene-bible-generator/
│   ├── script-validator/
│   └── continuity-extractor/
└── shared/
    ├── scene_bible/
    ├── schemas/
    └── logs/
```

### New Files (Detailed in Roadmap)
- IDENTITY.md (B1 manager identity)
- CONTEXT.md (B1 context)
- SKILL.md files (3 skills)
- PROMPT.md files (5 agents)
- JSON Schema files (4 schemas)
- Python implementation files (skills)

---

## Integration with Existing System

### Hooks into content_factory_v3
- Reuse `parallel_screenplay.py` logic via KMS client wrapper
- Consume `script_processor.py` output (already cleaned scripts)
- Output scene_bible.json that B2 can consume

### KMS Integration
- Create wrapper for async KMS key management
- screenplay-divider skill calls wrapper
- Cost tracking logged to OpenClaw

### Downstream Branches
- B2 (Audio) reads scene_bible.json
- B3 (Visual Planning) reads continuity_extract.json
- B4 (Asset Research) uses continuity_extract.json for search hints
- All branches validate input schema version before processing

---

## Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| KMS key exhaustion | Medium | Screenplay processing halts | Fallback to OpenRouter; queue for retry |
| GPT-4.1-mini hallucination | Low | Invalid scene structure | Validation layer (scene count, word count) |
| Continuity alias misses | Low | B4 misses entities | Manual review + Haiku prompt refinement |
| High latency (>2 min) | Low | Production backlog | Parallel screenplay division (Semaphore) |
| Schema compatibility | Low | Downstream breaks | Version schemas; test backward compatibility |

---

## Success Metrics

B1 is production-ready when:
- ✅ 100% of valid scripts → schema-compliant scene_bible.json
- ✅ Invalid scripts fail gracefully with clear errors
- ✅ continuity_extract.json is 95%+ accurate (manual verification)
- ✅ Cost per video < $0.20
- ✅ Latency < 2 min per script
- ✅ B10 (Monitoring) can track B1 metrics
- ✅ Production Manager can invoke B1 independently
- ✅ Documentation complete and tested

---

## What's NOT in This Research

- Detailed code implementation (that's Claude Code's job)
- Specific prompt engineering (will evolve during Phase 2)
- Integration with B2-B9 agents (separate research later)
- Multi-machine deployment strategy (separate research)
- Security hardening details (separate research)

---

## Next Steps

### Immediate (Before Starting Implementation)
1. ✅ Review RESEARCH_SUMMARY.md (Tobias)
2. ✅ Approve timeline + budget (Tobias)
3. ✅ Answer critical questions (Tobias) — see 05_IMPLEMENTATION_ROADMAP.md
4. ✅ Assign Claude Code to implementation (Tobias)

### Short-term (Week 0-1)
1. Claude Code reads 01-05 documents (in order)
2. Claude Code sets up directories (Phase 0)
3. Claude Code creates JSON schemas (Phase 1)

### Medium-term (Week 1-4)
1. Implement 3 skills (Phase 2)
2. Create 5 OpenClaw agents (Phase 3)
3. KMS integration + testing (Phase 4)
4. End-to-end testing (Phase 5)
5. Production readiness (Phase 6)
6. Handoff & training (Phase 7)

---

**Created:** 2026-03-26 14:37 GMT-3  
**Total research effort:** ~8 hours (Haiku subagent)  
**Ready for:** Implementation sprint (Claude Code)
