# Branch 4 Research Package — Index & Navigation

**Date:** 26 Mar 2026  
**Total:** 6 documents, 89 KB, 2,173 lines  
**Status:** ✅ Complete and ready for implementation  

---

## Quick Navigation

| Document | Purpose | Read Time | For Whom |
|----------|---------|-----------|----------|
| **RESEARCH_SUMMARY.txt** | This research in 1 page | 5 min | Everyone (start here) |
| **00_README.md** | Strategic overview + timeline | 10 min | Lucca + decision-makers |
| **01_BRANCH4_ANALYSIS.md** | Detailed capability analysis | 15 min | Claude Code (implementation) |
| **02_SKILL_SPECS.md** | 5 skill templates | 20 min | Claude Code (coding) |
| **03_AGENT_PROMPTS.md** | 5 agent prompt templates | 20 min | Claude Code (prompts) |
| **04_INTEGRATION_CHECKLIST.md** | Step-by-step guide | 25 min | Claude Code + Lucca (oversight) |

---

## Document Breakdown

### 1. RESEARCH_SUMMARY.txt (318 lines)
**What:** Executive summary of all research findings  
**Key Sections:**
- Task scope + deliverables checklist
- Local docs read (7 project documents)
- 5 concrete skills to build (with phases)
- Cheap model workflow ($0.01/video)
- Files created + verification
- Key insights + recommendations
- Risks & mitigations
- Next steps

**When to Read:** First thing, 5 minutes, everyone  
**Takeaway:** What we're building, why, when, how much it costs

---

### 2. 00_README.md (215 lines)
**What:** Strategic overview + business case  
**Key Sections:**
- TL;DR: What problem we solve
- 5 OpenClaw skills (table)
- 5 OpenClaw agents (table)
- Implementation timeline (Phase 1-4)
- 5 key design decisions
- Cost analysis ($0.01/video)
- Success metrics
- Known constraints
- How to use this research package
- Open questions (for Lucca)

**When to Read:** After summary, 10 minutes, Lucca + stakeholders  
**Takeaway:** Business case + timeline + who does what

---

### 3. 01_BRANCH4_ANALYSIS.md (329 lines)
**What:** Complete capability analysis + requirements  
**Key Sections:**
- What Branch 4 does (role, input, output)
- Current pipeline gap
- 5 agents needed (role matrix)
- Required capabilities per agent
- 6 OpenClaw skills worth building (detailed)
  - archive-image-search
  - video-archive-finder
  - rights-normalizer
  - asset-dedup-scorer
  - asset-proof-validator (Phase 4)
  - browser-asset-scraper (Phase 4)
- Recommended contracts & artifacts
- Cheap model workflow
- Implementation phases
- Known constraints & risks
- Not building (out of scope)
- Summary table

**When to Read:** Before implementation, 15 minutes, Claude Code  
**Takeaway:** What to build, what not to build, how to build cheap

---

### 4. 02_SKILL_SPECS.md (363 lines)
**What:** Detailed specifications for 5 skills  
**Structure:** For each skill:
- Purpose + use case
- Template directory structure
- SKILL.md outline (copypaste)
- Implementation notes
- Dependencies + integrations
- API documentation
- Error handling patterns

**Skills Covered:**
1. archive-image-search (Phase 1) — LOC/Europeana/Wikimedia
2. video-archive-finder (Phase 2) — Archive.org + FFmpeg
3. asset-rights-normalizer (Phase 2) — License extraction + mapping
4. asset-dedup-scorer (Phase 3) — URL hash + perceptual hash
5. asset-proof-validator (Phase 4, deferred) — Placeholder

**When to Read:** During implementation, 20 minutes, Claude Code  
**Takeaway:** Copy-paste templates; exact API calls to use; error patterns

---

### 5. 03_AGENT_PROMPTS.md (562 lines)
**What:** Complete PROMPT.md templates for 5 agents  
**Structure:** For each agent:
- Location (where to create file)
- Content (copypaste this into PROMPT.md)
- Role + responsibilities
- Input JSON format
- Processing steps
- Output JSON format
- Decision points
- Error handling
- Special cases
- Notes

**Agents Covered:**
1. people_finder — Search portraits of historical figures
2. location_finder — Search architectural + landscape photos
3. event_object_finder — Search historical events + objects + documents
4. video_finder — Search b-roll + newsreels
5. asset_judge — Score candidates, decide real vs AI

**When to Read:** During implementation, 20 minutes, Claude Code  
**Takeaway:** Exact prompts; copypaste into agent folders; processing logic

---

### 6. 04_INTEGRATION_CHECKLIST.md (385 lines)
**What:** Step-by-step implementation roadmap  
**Structure:**
- Overview (how Branch 4 fits in pipeline)
- Phase 1 checklist (Week 1: Mar 26-30)
  - Infrastructure setup
  - Skill setup
  - Agent prompt setup
  - Input/output contracts
  - Manual testing
- Phase 2 checklist (Week 2: Apr 2-6)
  - Skills expansion
  - Agent enhancement
  - Testing + multi-account expansion
- Phase 3 checklist (Week 3: Apr 9-13)
  - Deduplication system
  - Scoring refinement
  - Analytics & reporting
- Phase 4 checklist (Ongoing)
  - Browser fallback
  - Reverse image search
  - Non-WWII accounts
  - ML-based improvements
- Testing strategy (unit, integration, E2E)
- Deployment steps
- Known issues & workarounds
- Success criteria per phase

**When to Read:** During implementation, 25 minutes, Claude Code + Lucca  
**Takeaway:** Exact steps, timing, testing, deployment sequence

---

## How to Use This Package

### For Lucca (Strategic Decision)
1. **Read RESEARCH_SUMMARY.txt** (5 min)
2. **Read 00_README.md** (10 min)
3. **Decision:** Approve Phase 1-2-3 go-ahead
4. **Action:** Brief Claude Code on go-ahead + timeline

### For Claude Code (Implementation)
1. **Read 00_README.md** (10 min) — understand overall strategy
2. **Read 01_BRANCH4_ANALYSIS.md** (15 min) — understand detailed requirements
3. **Read 02_SKILL_SPECS.md** (20 min) — prepare skill implementations
4. **Read 03_AGENT_PROMPTS.md** (20 min) — prepare agent prompts
5. **Read 04_INTEGRATION_CHECKLIST.md** (25 min) — prepare implementation plan
6. **Begin Phase 1** — follow checklist step-by-step
7. **Reference docs** as needed during coding

### For Lucca (Oversight)
1. **Week 1:** Follow Phase 1 checklist alongside Claude Code
2. **Day 5:** Manual test of 1 WWII video (verify outputs)
3. **Week 2:** Monitor Phase 2 (video finding + rights)
4. **Week 3:** Monitor Phase 3 (deduplication + scaling)
5. **Week 4+:** Monitor production runs, analytics

---

## File Locations

All files created in:
```
C:\Users\User-OEM\.openclaw\workspace\research-haiku\b4-tools-skills\
```

Individual files:
- `00_README.md` — Strategic overview
- `01_BRANCH4_ANALYSIS.md` — Detailed analysis
- `02_SKILL_SPECS.md` — Skill specifications
- `03_AGENT_PROMPTS.md` — Agent prompts
- `04_INTEGRATION_CHECKLIST.md` — Implementation guide
- `RESEARCH_SUMMARY.txt` — This research in 1 page
- `INDEX.md` — This file (navigation guide)

---

## Key Concepts at a Glance

### 5 Skills (Implementation Order)
```
Phase 1: archive-image-search            (LOC/Europeana APIs)
Phase 2: video-archive-finder            (Archive.org + FFmpeg)
Phase 2: asset-rights-normalizer         (License mapping)
Phase 3: asset-dedup-scorer              (URL hash + perceptual hash)
Phase 4: asset-proof-validator (defer)   (TinEye reverse search — optional)
```

### 5 Agents (Parallel Execution)
```
people_finder          → search portraits of historical figures
location_finder        → search architectural photos
event_object_finder    → search historical events + objects
video_finder           → search b-roll + newsreels
asset_judge            → score candidates, decide real vs AI
```

### 3 Data Flows
```
Branch 3 (Visual Planning)
    ↓ visual_plan.json
Branch 4 (Asset Research) ← YOU ARE HERE
    ↓ asset_candidates.json
Branch 5 (Image Generation) or Branch 6 (Composition)
```

### Cost Model
```
Archive search:       $0 (web API)
Metadata extraction:  $0 (parsing)
Video validation:     $0 (FFmpeg)
Scoring:              ~$0.01 (Haiku batched)
─────────────────────────
Total per video:      ~$0.01 (90% reduction from $5.55)
```

---

## Decision Points

**Question 1: Approve Phase 1-2-3?**
- Phase 1: People/location/event/video finders + scoring ($0.01/video)
- Phase 2: Video finding + rights verification (addition to Phase 1)
- Phase 3: Deduplication + multi-source fallback (scalability)
- **Recommendation:** Yes — all low risk, high ROI

**Question 2: CC0 only or CC-BY acceptable?**
- Phase 1-2: CC0 only (legal certainty, no risk)
- Phase 3+: Consider CC-BY with human review layer (more coverage)
- **Recommendation:** Start CC0; expand in Phase 3 if coverage insufficient

**Question 3: Scoring threshold 0.72 or different?**
- Current: 0.72 = empirically balanced
- Can adjust after Phase 1-2 testing
- **Recommendation:** Use 0.72; refine based on real data

---

## Success Criteria

**Phase 1 (Week 1):**
- ✅ All agents running
- ✅ Manual test of 1 video: > 70% scenes with real asset (score > 0.72)
- ✅ No broken URLs or licensing violations

**Phase 2 (Week 2):**
- ✅ Automated scheduling works
- ✅ First 5 production videos processed automatically
- ✅ Rights verified for all candidates

**Phase 3 (Week 3):**
- ✅ Deduplication reducing redundancy
- ✅ Asset Registry populated
- ✅ Expanded to 2+ accounts

**Phase 4+ (Ongoing):**
- ✅ AI fallback rate < 30%
- ✅ Cost per video < $0.10
- ✅ Analytics dashboard showing trends

---

## Open Questions (For Lucca)

1. **Rights tolerance:** CC0 only, or expand to CC-BY in Phase 3?
2. **Quality bar:** Minimum resolution? (assuming 720p+)
3. **AI fallback:** Auto-generate if < 0.72, or flag for review?
4. **Video usage:** Can archive videos be used as-is, or need cutting?
5. **Archive expansion:** Which new archives to prioritize? (Phase 4)

---

## Next Action

**Immediate (Today):**
1. Lucca: Review RESEARCH_SUMMARY.txt + 00_README.md
2. Lucca: Approve Phase 1-2-3 timeline
3. Claude Code: Begin Phase 1 implementation per 04_INTEGRATION_CHECKLIST.md

**Week 1:**
4. Claude Code: Implement Phase 1 (archive-image-search + 5 agents)
5. Lucca + Claude: Manual test with 1 WWII video
6. Iterate based on results

**Week 2+:**
7. Claude Code: Implement Phase 2-3 per checklist
8. Lucca: Monitor production runs + analytics
9. Continuous improvement

---

## Research Metadata

**Research Date:** 26 Mar 2026, 14:37 GMT-3  
**Subagent:** Haiku (depth 1/1)  
**Status:** ✅ Complete  
**Total Size:** 89.1 KB (6 documents, 2,173 lines)  
**Ready for:** Immediate implementation  

**Documents:**
- RESEARCH_SUMMARY.txt (executive summary)
- 00_README.md (strategic overview)
- 01_BRANCH4_ANALYSIS.md (detailed analysis)
- 02_SKILL_SPECS.md (implementation specs)
- 03_AGENT_PROMPTS.md (prompt templates)
- 04_INTEGRATION_CHECKLIST.md (step-by-step guide)
- INDEX.md (this file)

---

## How This Research Will Be Used

1. **Lucca** approves strategy from 00_README.md + RESEARCH_SUMMARY.txt
2. **Claude Code** implements using 02_SKILL_SPECS.md + 03_AGENT_PROMPTS.md + 04_INTEGRATION_CHECKLIST.md
3. **Tobias (CEO)** monitors implementation progress + adjusts as needed
4. **Production Manager** triggers Branch 4 for video production
5. **Branch 4 agents** execute autonomously following PROMPT.md + skills
6. **Asset candidates JSON** feeds into Branch 5 (Image Generation)

---

## Final Note

This research package is **implementation-ready**. All files are structured to be directly copied into the project tree. No additional research needed; ready to build.

Questions or issues during implementation? Refer back to the relevant document:
- **Strategic questions** → 00_README.md + RESEARCH_SUMMARY.txt
- **Technical design** → 01_BRANCH4_ANALYSIS.md
- **Skill coding** → 02_SKILL_SPECS.md
- **Agent prompting** → 03_AGENT_PROMPTS.md
- **Phased rollout** → 04_INTEGRATION_CHECKLIST.md

---

**Research completed by:** Haiku subagent  
**Date:** 26 Mar 2026, 14:37 GMT-3  
**Status:** ✅ Complete and ready for implementation
