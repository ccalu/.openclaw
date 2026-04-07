# Haiku Research: OpenClaw Infrastructure for Content Factory

**Subagent:** haiku-infra-tools-skills  
**Date:** 2026-03-26  
**Status:** ✅ Complete  
**Audience:** Lucca, Tobias, Claude Code

---

## What This Is

Research on **infrastructure, tooling, and skills** needed for Content Factory's video-editing department to operate autonomously on OpenClaw.

Focus: Platform/tooling around **multi-machine orchestration**, **shared storage**, **cost control**, and **artifact coordination** — NOT high-level philosophy.

---

## Quick Start: What to Read

1. **START HERE:** 05_IMPLEMENTATION_ROADMAP.md
   - 5 critical decisions you need to make
   - Timeline estimate (Week 1-4)
   - Success criteria
   - Who does what

2. **Deep Dive (as needed):**
   - 01_DOCS_READ.md — What was researched, gaps identified
   - 02_RECOMMENDED_TOOLS_SKILLS.md — 10 concrete tools/skills to build
   - 03_ARTIFACT_CONTRACTS.md — JSON schemas for data flow (scene_bible, asset_registry, etc.)
   - 04_CHEAP_MODEL_WORKFLOWS.md — Cost optimization for sub-agents (~$0.05/video)

---

## Key Findings

### Critical Infrastructure Needed (Must-Do)

| # | Item | Impact | Effort | Cost |
|---|------|--------|--------|------|
| 1 | **Git-based config storage** | Version control, multi-machine sync | 2h | $0 |
| 2 | **Hybrid Git+Local artifacts** | Coordination between B1-B10 agents | 1h | $0 |
| 3 | **Remote-exec SSH skill** | Dispatch jobs to M2-M6 for parallel work | 2-3d | $0 |
| 4 | **Cost circuit breaker** | Safety guardrail ($500/day hard stop) | 1d | $0 |

### Nice-to-Have (Optimize Later)

- Config validation CI/CD
- Monitoring dashboard
- Browser automation (img2video)
- Dedicated browser node (M7)
- Cost attribution per account

---

## The Architecture

### 4-Level Hierarchy
```
Level 1: CEO (Tobias)
         └─ Production Manager (Level 2)
            └─ 10 Branch Managers (Level 3)
               └─ ~42 Individual Agents (Level 4)
```

### 10 Branches
| # | Branch | Purpose | Agents |
|---|--------|---------|--------|
| 1 | Pre-Production | Script → Scenes | 3 |
| 2 | Audio | TTS, validation | 4 |
| 3 | Visual Planning | Direction specs | 5 |
| 4 | Asset Research | Find real images | 5 |
| 5 | Image Generation | ComfyUI + browser animation | 5 |
| 6 | Scene Composition | Timeline assembly | 3 |
| 7 | Post-Production | Music, SFX, lettering | 5 |
| 8 | Assembly & Render | TSX gen, render, upload | 4 |
| 9 | Quality Assurance | Validation at every stage | 5 |
| 10 | Monitoring | Cost tracking, alerts | 3 |

### Data Flow
```
B1 (Scene Bible)
  ├─→ B2 (Audio Timestamps)
  ├─→ B3 (Visual Plan)
  │   ├─→ B4 (Asset Candidates)
  │   └─→ B5 (Generated Assets)
  ├─→ B6 (Scene Composition)
  │   ├─→ B7 (Post-Prod Plan)
  │   │   └─→ B8 (Final Video)
  │   │       ├─→ B9 (QA)
  │   │       └─→ B10 (Monitoring)
  └─ All artifacts validated by B9, tracked by B10
```

---

## Artifact Contracts

8 core JSON schemas that flow between branches:

1. **Scene Bible** (B1 → B2-B10) — Script divided into scenes
2. **Audio Timestamps** (B2 → B3-B8) — Exact word timing for sync
3. **Visual Plan** (B3 → B4-B6) — Direction specs per scene
4. **Asset Candidates** (B4 → B5-B6) — Found real images/videos
5. **Generated Assets** (B5 → B6-B8) — AI-generated images
6. **Scene Composition** (B6 → B7-B8) — Timeline with motion specs
7. **Post-Prod Plan** (B7 → B8) — Music, SFX, lettering
8. **Final Manifest** (B8 → B9-B10) — Render output + QA signoffs

Full schemas in **03_ARTIFACT_CONTRACTS.md**

---

## Cost Breakdown

### Current (Mar 2026)
- Image generation: ~$5.55/video
- Audio: Free (Gemini TTS)
- Rendering: ~$2.50/video
- **Total: ~$8.05/video**

### Target (Post-Optimization)
- LLM costs: ~$0.054/video (batching + cheap models)
- Image generation: $0.00 (ComfyUI local)
- Rendering: ~$2.50/video
- **Total: ~$2.55/video** (68% savings!)

See **04_CHEAP_MODEL_WORKFLOWS.md** for per-branch routing.

---

## Multi-Machine Setup

### Current
- **M1:** Main gateway (Ryzen 9, RTX 4070 Super, 128GB RAM) — OpenClaw + ComfyUI

### Future
- **M2-M6:** Node hosts — SSH access, ComfyUI, asset search
- **M7 (optional):** Browser node — 20 Chrome instances for parallel asset research

### Coordination
- Git: Configs synced via `git pull` at agent start
- Artifacts: Local workspace on M1, committed periodically
- Jobs: Remote-exec skill dispatches to M2-M6 via SSH
- Parallelization: Image gen, asset search, rendering can run across machines

---

## Timeline

### Week 1 (Critical Infrastructure)
- [ ] Git repo setup (Lucca: 30 min)
- [ ] Workspace sync structure (Claude Code: 1h)
- [ ] Cost breaker cron (Haiku/Lucca: 1d)
- [ ] Remote-exec skill planning (Claude Code: 1d)

### Week 2-4 (Core Agents)
- [ ] Production Manager (Claude Code: 2-3d)
- [ ] B1-B5 agents (Claude Code: ~2w)
- [ ] Test 5-10 videos end-to-end
- [ ] Tune model costs, validate contracts

### Month 2+ (Scaling)
- [ ] B6-B10 agents
- [ ] Full autonomy testing
- [ ] Creative adaptation (per-video decisions)

---

## Decisions You Need to Make

### Decision 1: GitHub or Local-Only Configs?
→ **Recommendation:** GitHub (version control, audit trail)

### Decision 2: How to Coordinate Artifacts?
→ **Recommendation:** Local workspace + periodic git commit

### Decision 3: Can M1 Dispatch to M2-M6?
→ **Recommendation:** Yes, build remote-exec skill

### Decision 4: Hard Stop at $500/day?
→ **Recommendation:** Yes, safety guardrail

### Decision 5: Target LLM Budget?
→ **Recommendation:** ~$0.05/video (batching + cheap models)

**See 05_IMPLEMENTATION_ROADMAP.md for details on each.**

---

## Key Principles

1. **Immutability:** Once a stage completes, outputs are READ-ONLY
2. **Clear contracts:** Every JSON has defined schema + validation
3. **Single source of truth:** Audio timestamps (B2) are temporal baseline
4. **Lineage tracking:** Every artifact includes `created_by`, `created_at`
5. **Cost visibility:** Every artifact tracks cost incurred at that stage
6. **Batching:** Scene processing (8 scenes → 1 LLM call) = 92% cost reduction

---

## Files in This Research

```
research-haiku/infra-tools-skills/
├── README.md                           (this file)
├── 01_DOCS_READ.md                     (what was read, constraints)
├── 02_RECOMMENDED_TOOLS_SKILLS.md      (10 tools/skills to build)
├── 03_ARTIFACT_CONTRACTS.md            (JSON schemas + data flow)
├── 04_CHEAP_MODEL_WORKFLOWS.md         (cost optimization per branch)
└── 05_IMPLEMENTATION_ROADMAP.md        (decisions, timeline, success criteria)
```

---

## What This Enables

✅ **Multi-machine coordination** without central database (uses git + artifacts)  
✅ **Cost control** via circuit breaker + cheap model routing  
✅ **Safe scaling** from 2 agents (Tobias + PM) → 43 agents incrementally  
✅ **Creative autonomy** via artifact-driven coordination (not rigid code)  
✅ **Traceability** (every video has audit trail, cost breakdown, QA signoffs)  

---

## Next Steps

1. **Lucca:** Review 05_IMPLEMENTATION_ROADMAP.md, make 5 decisions
2. **Claude Code:** Start Week 1 tasks (Git, workspace sync, cost breaker)
3. **Haiku:** Available for implementation details, code review, troubleshooting
4. **Tobias:** Stand by to lead broader strategy once infrastructure is live

---

## Questions?

Open questions documented in **05_IMPLEMENTATION_ROADMAP.md** section "Open Questions for Lucca".

---

**Research completed:** 2026-03-26 14:37:00 GMT-3  
**Status:** ✅ Ready for implementation planning  
**Handoff:** To Lucca + Claude Code
