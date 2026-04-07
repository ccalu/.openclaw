# Branch 1 (Pre-Production) OpenClaw Research

**Status:** COMPLETE ✅  
**Created:** 2026-03-26 14:37 GMT-3  
**For:** Tobias (CEO) → Claude Code (Implementation)

---

## What This Is

Complete research deliverable for building **Branch 1 Pre-Production** as a hierarchical set of OpenClaw agents and reusable skills. Includes:

- ✅ Analysis of existing Content Factory v3 code
- ✅ 6 specific skills to build (with exact specs)
- ✅ 4 formal data schemas (JSON + Pydantic)
- ✅ Cheap model workflow ($0.13-0.15/video)
- ✅ 4-6 week implementation roadmap
- ✅ Success criteria and risk mitigation

**Total:** ~76 KB of structured documentation

---

## Start Here

### For Tobias (Oversight)
1. **INDEX.md** — Quick reference guide
2. **RESEARCH_SUMMARY.md** — Executive overview (10 min)
3. **02_CONCRETE_TOOLS_SKILLS.md** — What gets built (15 min)
4. **04_CHEAP_MODEL_WORKFLOW.md** — Budget approval ($20-50/month for B1)
5. **05_IMPLEMENTATION_ROADMAP.md** — Timeline approval (4-6 weeks)

### For Claude Code (Implementation)
1. **INDEX.md** — Quick reference
2. **01_LOCAL_DOCS_READ.md** — Baseline state
3. **02_CONCRETE_TOOLS_SKILLS.md** — Exact skill specs
4. **03_STRUCTURED_ARTIFACTS.md** — Schema design
5. **05_IMPLEMENTATION_ROADMAP.md** — Phase-by-phase plan

---

## The Findings (TL;DR)

### What We're Building
**3 critical skills:**
1. **scene-bible-generator** — Script → structured scene_bible.json
2. **script-validator** — Quality gate before processing
3. **continuity-extractor** — Entity registry for downstream branches

**5 OpenClaw agents** to orchestrate these skills

### Cost
**$0.13-0.15 per video** (breakdown: screenplay $0.10, validation $0.005, extraction $0.008, checks $0.005-0.03)

For 160 videos/month: **~$21-24** (incredibly cheap)

### Timeline
**4-6 weeks** (19 days effort)

- Week 0: Setup
- Week 1: Schemas
- Week 1-2: Skills
- Week 2-3: Agents
- Week 3-4: Testing + Production readiness
- Week 4: Handoff

### Key Deliverable: Data Contracts
**scene_bible.json** (20-30 KB) — immutable artifact, read by all 8 downstream branches

Contains: scenes, entities (characters/locations/props), narrative beats, quality metrics, validation report

---

## Files in This Directory

```
00_README.md                    ← You are here
INDEX.md                        ← Quick reference + how to use
RESEARCH_SUMMARY.md             ← Executive summary
01_LOCAL_DOCS_READ.md           ← Baseline analysis
02_CONCRETE_TOOLS_SKILLS.md     ← Skill specs (Tier 1 + 2)
03_STRUCTURED_ARTIFACTS.md      ← Schema definitions
04_CHEAP_MODEL_WORKFLOW.md      ← Cost optimization
05_IMPLEMENTATION_ROADMAP.md    ← 4-6 week plan
```

**Read INDEX.md next** for guidance on which docs to read based on your role.

---

## Key Decisions Made

| Question | Decision | Rationale |
|----------|----------|-----------|
| **How many skills?** | 6 (3 critical + 3 optional) | MVP + future enhancements |
| **Which models?** | Haiku + GPT-4.1-mini + Ollama fallback | Cost-effective, proven, scalable |
| **Cost per video?** | $0.13-0.15 | Screenplay dominates; others cheap |
| **Data format?** | JSON with formal schema | Version-controlled, downstream-friendly |
| **Implementation approach?** | OpenClaw agents + reusable skills | Modular, testable, cloud-ready |
| **Timeline?** | 4-6 weeks | Achievable without rushing |

---

## Recommendations for Tobias

### 🟢 Approve & Go
- ✅ Greenlight the 4-6 week timeline
- ✅ Approve $20-50/month budget for B1
- ✅ Assign Claude Code to implementation

### 🟡 Decide Before Starting
- ❓ Where are scripts fetched from? (Google Sheets? Queue? Webhook?)
- ❓ How are account-specific overrides stored?
- ❓ Does scene_bible.json need human approval before B2?
- ❓ Max SLA for scene_bible.json availability?
- ❓ Fallback if B1 fails (halt or use v3)?

*(See 05_IMPLEMENTATION_ROADMAP.md for full list)*

### 🔵 Prepare for Integration
- Plan how Production Manager will invoke B1 (method signature, return format)
- Plan schema validation at B1→B2 handoff
- Plan cost tracking via B10 (Monitoring)

---

## What This Doesn't Cover

- Specific prompt engineering (will evolve during implementation)
- Integration with B2-B9 agents (separate research)
- Multi-machine deployment (separate research)
- Security hardening (separate research)
- Analytics and performance optimization (later phases)

---

## Next Step: Hand to Claude Code

Once Tobias approves the timeline + budget:

1. Claude Code reads **01_LOCAL_DOCS_READ.md** → understand baseline
2. Claude Code reads **02_CONCRETE_TOOLS_SKILLS.md** → get exact specs
3. Claude Code reads **03_STRUCTURED_ARTIFACTS.md** → design schemas
4. Claude Code follows **05_IMPLEMENTATION_ROADMAP.md** → implement phase-by-phase

**Est. Claude Code review time:** 2-3 hours  
**Est. first phase (setup + schemas):** 2-3 days

---

## Contact & Questions

If Tobias has questions:
- **On feasibility:** See 02_CONCRETE_TOOLS_SKILLS.md + 05_IMPLEMENTATION_ROADMAP.md
- **On cost:** See 04_CHEAP_MODEL_WORKFLOW.md
- **On data contracts:** See 03_STRUCTURED_ARTIFACTS.md
- **On current state:** See 01_LOCAL_DOCS_READ.md

All questions should be answerable from these 7 documents.

---

## Research Metadata

| Property | Value |
|----------|-------|
| Research Duration | ~8 hours (Haiku subagent) |
| Total Documentation | 76 KB across 7 files |
| Local Docs Analyzed | 10+ (architecture, pipeline, code) |
| Local Docs Skipped | 25+ (knowledge-base course content) |
| Code Files Inspected | 3 (script_processor, parallel_screenplay, etc.) |
| Skills Designed | 6 |
| Data Schemas Created | 4 (with examples) |
| Agent Roles Defined | 5 |
| Implementation Phases | 7 |
| Success Criteria | 8 checkboxes |

---

**Status:** Ready for Tobias review & Claude Code implementation.

**Location:** `C:\Users\User-OEM\.openclaw\workspace\research-haiku\b1-tools-skills\`
