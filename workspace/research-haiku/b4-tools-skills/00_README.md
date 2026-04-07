# Branch 4 (Asset Research) — Research & Implementation Guide

**Date:** 26 Mar 2026  
**Subagent:** Haiku Research  
**Status:** Ready for implementation  

---

## What This Is

Complete research package for building **Branch 4 (Asset Research)** — the agent branch responsible for finding real images and videos for Content Factory video production.

This folder contains:
1. **01_BRANCH4_ANALYSIS.md** — Strategic overview + capability requirements
2. **02_SKILL_SPECS.md** — Detailed skill specifications (5 skills)
3. **03_AGENT_PROMPTS.md** — PROMPT.md templates for 5 agents
4. **04_INTEGRATION_CHECKLIST.md** — Step-by-step implementation plan
5. **00_README.md** — This file

---

## TL;DR: What We're Building

### Problem
Current pipeline: manually finding images + applying fixed image-generation prompts. Lucca hand-picks assets for most accounts → bottleneck on his time + inconsistent quality.

### Solution
Autonomous agent-based asset research:
- **people_finder** → searches portraits of historical figures
- **location_finder** → searches photographs of places
- **event_object_finder** → searches historical events, objects, documents
- **video_finder** → searches b-roll and newsreel footage
- **asset_judge** → evaluates candidates, decides real vs AI generation

### Output
Scored candidates JSON that feeds into Branch 5 (Image Generation) and Branch 6 (Composition). If real asset scores > 0.72, use it. If < 0.72, generate with AI.

### Cost
~$0.01/video for asset research (mostly local computation + free web search).

---

## 5 OpenClaw Skills to Build

| # | Skill | Phase | Model | Cost | Purpose |
|---|-------|-------|-------|------|---------|
| 1 | **archive-image-search** | 1 | Web API | $0 | Search LOC/Europeana/Wikimedia for images |
| 2 | **video-archive-finder** | 2 | FFmpeg | $0 | Search Archive.org/YouTube for video clips |
| 3 | **asset-rights-normalizer** | 2 | Rules | $0 | Extract + verify licensing (CC0, public domain) |
| 4 | **asset-dedup-scorer** | 3 | Hash | $0 | Detect duplicates; score uniqueness |
| 5 | **asset-proof-validator** | 4 | API | $0.05 | Reverse image search (defer to Phase 4) |

**Skills 1-4 are critical for Phase 1-3. Skill 5 is optional (Phase 4 if needed).**

---

## 5 OpenClaw Agents (per Branch)

| # | Agent | Type | Input | Output | Model |
|---|-------|------|-------|--------|-------|
| 1 | **people_finder** | Finder | person + era | image candidates[] | Web search |
| 2 | **location_finder** | Finder | location + era | image candidates[] | Web search |
| 3 | **event_object_finder** | Finder | event/object + era | image candidates[] | Web search |
| 4 | **video_finder** | Finder | query + era + duration | video candidates[] | Web search |
| 5 | **asset_judge** | Evaluator | candidates[] | {score, decision, reason} | Haiku (~$0.01) |

---

## Implementation Timeline

### Phase 1 (Week 1: Mar 26-30)
- [ ] Install archive-image-search skill (LOC + Europeana APIs)
- [ ] Create people_finder, location_finder, event_object_finder, video_finder agents
- [ ] Create asset_judge agent (scoring logic)
- [ ] Manual test with 1 WWII video
- [ ] Output: working agent team, manual validation only

### Phase 2 (Week 2: Apr 2-6)
- [ ] Install video-archive-finder skill (Archive.org + FFmpeg)
- [ ] Install asset-rights-normalizer skill
- [ ] Update all finders to verify rights (CC0 + public domain only)
- [ ] Automated testing with account 003 (WWII)
- [ ] Output: Production Manager can trigger Branch 4 → get scored assets

### Phase 3 (Week 3: Apr 9-13)
- [ ] Install asset-dedup-scorer skill
- [ ] Set up Asset Registry (Supabase or SQLite)
- [ ] Multi-source fallback (LOC → Europeana → Smithsonian → fallback)
- [ ] Expand to account 005 or 008
- [ ] Output: Dedup working; ready for scaling

### Phase 4+ (Ongoing)
- [ ] Monitor gaps (queries with 0 results)
- [ ] Add browser-based fallback if APIs fail
- [ ] Consider reverse image search (TinEye) for validation
- [ ] Expand to more accounts/eras
- [ ] Archive coverage analysis + optimization

---

## Key Design Decisions

### 1. Archive-First, AI-Fallback
Real images from public archives are preferred. AI generation is fallback when no real asset scores > 0.72.
- Why: Authenticity, diversity, legal safety
- Cost: $0 for real + ~$0.50-1.00 for AI fallback per scene

### 2. Only CC0 + Public Domain (Phase 1-2)
Avoid rights complexity. Use only CC0 or verified public domain.
- Why: Legal certainty, no attribution burden
- Risk: Lower coverage for recent/niche topics
- Mitigation: Plan to expand to CC-BY in Phase 3+ if needed

### 3. Parallel Finder Agents
All 4 finders run in parallel (people, location, event, video).
- Why: Speed + diversity of results
- Output: Combined candidates list for asset_judge to score

### 4. Scoring Threshold: 0.72
If final_score >= 0.72 → "USE_REAL". < 0.72 → "GENERATE_AI".
- Why: Empirically tuned balance (high enough for quality, low enough for coverage)
- Tunable: Can adjust based on Phase 1-2 results

### 5. Asset Registry (Phase 3)
Centralized tracking of all found assets (URL, hash, usage, rights).
- Why: Deduplication, analytics, reuse across videos
- Storage: SQLite or JSON file in shared/asset_registry/

---

## Cost Analysis (Estimated)

### Per Video
- Archive search (web API): $0
- FFmpeg validation (local): $0
- Rights verification (parsing): $0
- Asset scoring (1 Haiku call): $0.008
- **Total: ~$0.01/video**

### Comparison
- Current: $5.55/video (Gemini paid images) + manual labor
- With Branch 4: $0.01/video (asset research) + $0.50 (AI gen if fallback)
- **Savings: 90%+ for asset research phase**

---

## Known Constraints

### Rate Limits
- Brave API (web search): 1000 calls/day free tier
- Europeana API: 1000 calls/day (unless paid)
- Archive.org: ~10 req/sec (reasonable)
- Workaround: Heavy caching, batch requests

### Archive Coverage Gaps
- Some queries (pre-1800, obscure figures) may return 0 results
- Different archives have different coverage (LOC strong for US, Europeana strong for EU)
- Mitigation: Multi-source fallback, broad query expansion

### Rights Verification Complexity
- License metadata varies in quality (EXIF, headers, page HTML)
- Some archives have inconsistent licensing across mirrors
- Mitigation: Phase 1 uses only CC0 + public domain (highest confidence)

### Video Degradation
- Public domain videos often have lower resolution (360p) or film grain
- May need upscaling or color correction (Branch 5 responsibility)
- Mitigation: asset_judge flags "USE_REAL_WITH_ENHANCEMENT"

---

## Success Metrics

### Phase 1
- ✅ All agents running without errors
- ✅ Manual test of 1 video: > 70% of scenes get real asset (score > 0.72)
- ✅ No broken URLs in output
- ✅ No licensing violations

### Phase 2
- ✅ Automated scheduling works (Production Manager → Branch 4)
- ✅ First 5 production videos processed without human intervention
- ✅ Rights verified for all candidates

### Phase 3
- ✅ Deduplication reducing redundancy (< 10% near-duplicates)
- ✅ Asset Registry populated + queryable
- ✅ Expanded to 2+ accounts (003 + 005)

### Phase 4+
- ✅ AI fallback rate stable (target: < 30% of scenes)
- ✅ Archive coverage gaps documented + prioritized
- ✅ Cost per video < $0.10 (including AI fallback)

---

## Files in This Research Package

```
research-haiku/b4-tools-skills/
├── 00_README.md                      ← You are here
├── 01_BRANCH4_ANALYSIS.md            ← Strategic overview + capabilities
├── 02_SKILL_SPECS.md                 ← 5 skill specifications
├── 03_AGENT_PROMPTS.md               ← PROMPT.md templates for 5 agents
└── 04_INTEGRATION_CHECKLIST.md       ← Step-by-step implementation plan
```

---

## How to Use This Research

### For Lucca (Strategic)
1. Read **01_BRANCH4_ANALYSIS.md** for full context
2. Review **04_INTEGRATION_CHECKLIST.md** for timeline + dependencies
3. Decide on Phase 1-2-3 go/no-go
4. Coordinate with Claude Code for implementation

### For Claude Code (Implementation)
1. Copy skill templates from **02_SKILL_SPECS.md** → create skill folders
2. Copy agent prompts from **03_AGENT_PROMPTS.md** → create agent folders
3. Follow **04_INTEGRATION_CHECKLIST.md** step-by-step
4. Test each phase before proceeding to next

### For Branch 4 Agents (Once Running)
1. Each agent reads only its own PROMPT.md
2. Agents call skills via skill/SKILL.md interface
3. Agents output JSON following schema in **03_AGENT_PROMPTS.md**
4. asset_judge validates all outputs

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| **Archive APIs become unreliable** | Branch 4 fails, fallback to AI | Implement browser-based scraper (Phase 4) |
| **Low coverage for certain eras/topics** | High AI fallback rate | Expand archives; consider paid services |
| **Rights verification errors** | Legal liability | Phase 1: CC0 only; Phase 2+: human review layer |
| **Perceptual hashing complexity** | Dedup quality suffers | Start with URL normalization; add hashing later |
| **Cost of API calls exceeds budget** | Unsustainable | All Phase 1-3 skills use free APIs; avoid paid reverse search |

---

## Open Questions (For Lucca)

1. **Rights sensitivity:** How strict should licensing be? CC0 only vs CC-BY acceptable?
2. **Quality tolerance:** What resolution is minimum acceptable? (Currently assuming 720p+)
3. **AI fallback behavior:** If real asset < 0.72, auto-generate AI or flag for review?
4. **Video editing:** Can video_finder clips be used as-is, or do they need cutting/effects?
5. **Archive expansion:** Which archives should Phase 4 prioritize? (British Library? German archives?)

---

## Related Documentation

Outside this folder (in project root):
- **09_HIERARCHY_AND_STRUCTURE.md** — Overall agent hierarchy
- **04_BRANCH_ARCHITECTURE.md** — All 10 branches overview
- **03_PIPELINE_MAP.md** — How Branch 4 fits in pipeline
- **content_factory_v3/** — Existing production code (reference)

---

## Next Step

1. **Lucca reviews this research** → approves Phase 1-2-3 plan
2. **Claude Code implements** using 02_SKILL_SPECS.md + 03_AGENT_PROMPTS.md + 04_INTEGRATION_CHECKLIST.md
3. **Tobias monitors** implementation progress + adjusts as needed
4. **First Branch 4 run** with account 003 WWII videos
5. **Iterate** based on real-world results

---

## Summary

Branch 4 (Asset Research) is the execution layer for finding real images and videos. With 5 skills and 5 agents, it enables:

✅ Autonomous image/video discovery  
✅ Rights verification + safety  
✅ Scoring + decision logic  
✅ Fallback to AI generation when needed  
✅ Cost reduction from $5.55 → $0.01 per video  

Ready to build. Waiting for Lucca go-ahead on Phase 1.

---

**Research completed by:** Haiku subagent (26 Mar 2026, 14:37 GMT-3)  
**Research status:** ✅ Complete and ready for implementation
