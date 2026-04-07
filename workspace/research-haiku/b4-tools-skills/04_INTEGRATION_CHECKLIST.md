# Branch 4 Integration — Implementation Checklist

**Date:** 26 Mar 2026  
**For:** Connecting Branch 4 to existing pipeline  

---

## Overview

Branch 4 sits between **Branch 3 (Visual Planning)** and **Branch 5 (Image Generation)**.

```
Branch 3 (Visual Planning)
    ↓
    └─► visual_plan.json (asset_strategy per scene)
            ↓
     BRANCH 4 (Asset Research) ← YOU ARE HERE
            ↓
     asset_candidates.json (scored, ready for decision)
            ↓
     Branch 5 (Image Generation) or Branch 6 (Composition)
```

---

## Phase 1 Checklist (Week 1)

### Infrastructure Setup
- [ ] Create directory structure:
  ```
  agents/branches/04_asset_research/
  ├── IDENTITY.md
  ├── CONTEXT.md
  ├── agents/
  │   ├── people_finder/
  │   │   └── PROMPT.md
  │   ├── location_finder/
  │   │   └── PROMPT.md
  │   ├── event_object_finder/
  │   │   └── PROMPT.md
  │   ├── video_finder/
  │   │   └── PROMPT.md
  │   └── asset_judge/
  │       └── PROMPT.md
  └── shared/
      ├── asset_schema.json
      └── integration_guide.md
  ```

- [ ] Create IDENTITY.md for Branch 4 Manager
  ```markdown
  # Branch 4 — Asset Research

  ## Role
  Execute visual research: find real images/videos for scenes.

  ## Model
  None (Branch Manager is orchestrator, not LLM-based)

  ## Inputs
  - visual_plan.json from Branch 3
  - scene_bible.json (context)

  ## Outputs
  - asset_candidates.json (scored candidates per scene)

  ## Agents Under This Branch
  - people_finder
  - location_finder
  - event_object_finder
  - video_finder
  - asset_judge

  ## Dependencies
  - archive-image-search skill
  - video-archive-finder skill (Phase 2)
  - asset-rights-normalizer skill (Phase 2)
  - asset-dedup-scorer skill (Phase 3)
  ```

- [ ] Create CONTEXT.md for Branch 4 Manager
  ```markdown
  # Branch 4 Context

  ## Current State
  - Phase 1: focused on image finding (people, locations, events)
  - Phase 2: adding video finding + rights verification
  - Phase 3: adding deduplication + scoring

  ## Known Constraints
  - Rate limits on free APIs (LOC 100 req/sec, Europeana 1000/day)
  - Must verify rights → use only CC0 or public domain
  - Archive quality varies (resolution, metadata accuracy)

  ## Key Decisions
  - Assume LOC/Europeana metadata is reliable (minimize re-verification)
  - Cache search results heavily (archive items don't change)
  - Fallback to AI generation if no real asset scores > 0.72

  ## Next Iteration
  - Monitor which queries return 0 results (gaps in archives)
  - Track rights violations or licensing errors
  - Measure finder success rates per account/era
  ```

### Skill Setup
- [ ] Install archive-image-search skill (Phase 1)
  - Copy template from 02_SKILL_SPECS.md
  - Implement LOC API wrapper (Python)
  - Create source_config.yaml with API keys (Europeana)
  - Test with 3 queries: "Winston Churchill 1943", "10 Downing Street 1940s", "D-Day 1944"

- [ ] Document skill location in shared/integration_guide.md

### Agent Prompts
- [ ] Copy PROMPT.md for each agent from 03_AGENT_PROMPTS.md:
  - people_finder/PROMPT.md
  - location_finder/PROMPT.md
  - event_object_finder/PROMPT.md
  - video_finder/PROMPT.md (simplified, will upgrade in Phase 2)
  - asset_judge/PROMPT.md

- [ ] Test each agent with 1 sample query (manual)
  ```
  Lucca feeds sample input JSON to agent:
  → agent executes (calls archive-image-search skill)
  → agent returns candidates JSON
  → Lucca visually inspects results (are they relevant?)
  ```

### Input Contract (from Branch 3)
- [ ] Confirm Branch 3 will output `visual_plan.json` with structure:
  ```json
  {
    "video_id": "001_wwii_churchill",
    "scenes": [
      {
        "scene_num": 5,
        "narration": "Churchill addressed the war cabinet...",
        "visual_strategy": [
          {
            "type": "person",
            "entity": "Winston Churchill",
            "era": "1940-1945",
            "context": "Formal speech, determined expression",
            "constraints": { "prefer_bw": true }
          },
          {
            "type": "location",
            "entity": "Cabinet War Rooms",
            "era": "1943",
            "context": "Meeting room, wartime conditions"
          }
        ]
      }
    ]
  }
  ```

- [ ] If visual_plan.json structure differs, update agent PROMPTs accordingly

### Output Contract (to Branch 5 & 6)
- [ ] Formalize `asset_candidates.json` output:
  ```json
  {
    "video_id": "001_wwii_churchill",
    "processing_timestamp": "2026-03-26T14:37:00Z",
    "scenes": [
      {
        "scene_num": 5,
        "assets": [
          {
            "asset_id": "person_churchill_001",
            "type": "person",
            "source": "loc",
            "url": "https://loc.gov/...",
            "title": "Churchill at War Cabinet",
            "finder_confidence": 0.95,
            "judge_score": 0.87,
            "recommendation": "USE_REAL",
            "reasoning": "Exact match, public domain, high quality"
          },
          {
            "asset_id": "location_cabinet_001",
            "type": "location",
            "source": "europeana",
            "url": "https://europeana.eu/...",
            "title": "War Cabinet Rooms",
            "judge_score": 0.79,
            "recommendation": "USE_REAL"
          }
        ]
      }
    ]
  }
  ```

- [ ] Coordinate with Branch 5 (Image Generation): when recommendation="GENERATE_AI", Branch 5 knows to create image

### Manual Testing
- [ ] Test full flow with 1 video (account 003, WWII)
  - Feed visual_plan.json to Branch 4
  - Observe finder outputs
  - Observe judge scoring
  - Verify asset_candidates.json format
  - Hand off to Branch 5 for image generation decision

- [ ] Document any gaps (queries with 0 results, scoring disagreements)

---

## Phase 2 Checklist (Week 2)

### Skills Expansion
- [ ] Install video-archive-finder skill
  - Implement Archive.org search
  - Implement FFmpeg validation (local)
  - Create public_domain_video_sources.md reference

- [ ] Install asset-rights-normalizer skill
  - Implement metadata extraction (EXIF, headers)
  - Create cc_license_mapping.json (CC0, CC-BY, public domain)
  - Create source_license_rules.json (per-source rules)

### Agent Enhancement
- [ ] Update video_finder agent with video-archive-finder skill integration

- [ ] Update all finders to call asset-rights-normalizer
  - Before returning candidates, verify rights
  - Phase 2 constraint: only return candidates with rights_safety >= 0.90

### Testing
- [ ] Test video_finder with queries from account 003 (WWII videos)
  - Verify FFmpeg validation works
  - Verify video URLs are downloadable
  - Verify duration/resolution metadata accurate

- [ ] Test asset-rights-normalizer with 10 candidates from Phase 1
  - Verify metadata extraction accurate
  - Verify rights scoring correct (CC0=1.0, unknown=<0.70)

### Multi-Account Expansion
- [ ] Expand account 003 (WWII) Branch 4 to run automatically
  - Set up Branch 4 job triggering from Production Manager
  - Monitor first 5 video runs
  - Measure: candidates found, judge recommendations, AI fallback rate

- [ ] Plan Phase 3 expansion to account 005 (dark history) or 008 (stick figures)
  - Will need different search strategies (different eras, visual styles)

---

## Phase 3 Checklist (Week 3)

### Deduplication System
- [ ] Install asset-dedup-scorer skill
  - Implement URL normalization
  - Implement perceptual hashing (dhash)
  - Create SQLite registry (or JSON file)

- [ ] Set up Asset Registry in shared/:
  ```
  shared/asset_registry/
  ├── registry.db (SQLite) OR registry.json
  ├── dedup_rules.md
  └── cache_policy.md (30-day cache, 7-day retry for broken links)
  ```

- [ ] Integrate asset-dedup-scorer into finder pipeline
  - Before asset_judge, all candidates pass through dedup_scorer
  - If candidate is duplicate, mark with redundancy_score < 5
  - asset_judge can skip redundant assets

### Scoring Refinement
- [ ] Review asset_judge scores from Phase 1-2
  - Which queries get low scores? Why?
  - Which accounts/eras have poor archive coverage?
  - Document patterns (e.g., "pre-1900 images have lower resolution")

- [ ] Fine-tune scoring rubric
  - Adjust weights if needed (currently: relevance 30%, accuracy 25%, quality 20%, rights 15%, uniqueness 10%)
  - Add era-specific scoring rules (e.g., B&W photos expected for pre-1950)

### Analytics & Reporting
- [ ] Create monitoring dashboard (or manual weekly report)
  ```
  Metrics to track:
  - Total queries (per account, per era)
  - Queries returning 0 results (gaps)
  - Average finder confidence (should increase as system learns)
  - Average judge score (target: > 0.75 for "USE_REAL")
  - AI fallback rate (target: < 30%)
  - Rights violations (target: 0)
  - Cost per video (target: $0 for asset research)
  ```

- [ ] Create monthly summary for Lucca
  - What worked well? What failed?
  - Which archives most productive?
  - Recommendations for Phase 4

---

## Phase 4 Checklist (Ongoing)

### Browser Fallback (If Needed)
- [ ] Implement browser-asset-scraper skill (only if APIs become unreliable)
  - Use OpenClaw browser tool or external Playwright
  - Target: advanced search pages (Flickr, NYPL, etc.)

### Reverse Image Search
- [ ] Implement asset-proof-validator skill (high-priority validation)
  - Integrate TinEye API or Google Images reverse search
  - Cost: ~$0.01-0.05 per check; use sparingly for high-stakes editorial

### Non-WWII Accounts
- [ ] Expand Branch 4 to other accounts
  - Account 005 (dark history) — different era spans, different archives needed
  - Account 008 (stick figures) — modern cultural content, different sources
  - Each account may need custom search strategies

### Archive Coverage Analysis
- [ ] For accounts with low "USE_REAL" rate, investigate:
  - Are archives insufficient (pre-1900, obscure locations)?
  - Are queries too specific (no results)?
  - Could archive sources be expanded?

- [ ] Consider adding sources:
  - British Library archives
  - German Federal Archives
  - Russian State Archives
  - etc. (per account/era needs)

### ML-Based Improvements (Later)
- [ ] Visual matching via embeddings (if needed for better dedup/ranking)
- [ ] Query expansion (if needed for low-result queries)
- [ ] Auto-generated captions for unlabeled images
  - *Defer to Phase 5+; start with heuristic approach*

---

## Testing Strategy

### Unit Tests (Per Skill)
```
test_archive_image_search:
  - test_loc_search_query_format
  - test_europeana_search_query_format
  - test_fallback_chain (if source A fails, try B)
  - test_result_parsing (verify JSON schema)

test_asset_rights_normalizer:
  - test_exif_extraction
  - test_license_parsing (CC0, CC-BY, public domain)
  - test_source_rules (LOC always public domain)
  - test_confidence_scoring

test_asset_dedup_scorer:
  - test_url_normalization
  - test_perceptual_hash_matching
  - test_registry_storage
```

### Integration Tests (Per Agent)
```
test_people_finder:
  - input: {person_name: "Winston Churchill", era: "1940-1945"}
  - verify: candidates returned, url valid, rights field present

test_asset_judge:
  - input: 5 candidates with varying scores
  - verify: final_score calculated correctly, recommendation matches threshold
```

### End-to-End Tests (Full Branch 4)
```
test_full_video_run (account 003, WWII):
  - Input: visual_plan.json from Branch 3
  - Run all 5 agents in parallel
  - Output: asset_candidates.json with all candidates scored
  - Verify: no broken URLs, all candidates have required fields
```

---

## Deployment Steps

### Local Machine (M1 — Your Dev Machine)
1. [ ] Clone/copy Branch 4 agent structure to `agents/branches/04_asset_research/`
2. [ ] Install archive-image-search skill locally
3. [ ] Test with sample queries (manual)
4. [ ] Git commit with message: "Branch 4 Phase 1: asset finder agents + archive-image-search skill"

### Production Machines (M2-M6)
1. [ ] Deploy after Phase 1 validation passes
2. [ ] Copy same structure to each M2-M6 machine
3. [ ] Configure API keys (Europeana, etc.) via KMS on each machine
4. [ ] Schedule Branch 4 agent runs from Production Manager cron

### Rollout Schedule
- **Week 1 (Phase 1):** Deploy to M1 (dev), test manually
- **Week 2 (Phase 2):** Deploy to M1 + M2 (production), monitor first 5 videos
- **Week 3 (Phase 3):** Deploy to all M1-M6, enable automated scheduling
- **Week 4+:** Monitor, iterate, expand to other accounts

---

## Known Issues & Workarounds

### Issue 1: Archive.org Rate Limiting
**Problem:** Archive.org sometimes rate-limits or is slow
**Workaround:** Implement retry logic (exponential backoff), cache results heavily
**Mitigation:** Use multiple sources (LOC, Europeana) in parallel; don't rely on single source

### Issue 2: Metadata Quality Varies
**Problem:** Some archives have incomplete/inaccurate dates or descriptions
**Workaround:** Validate era via visual inspection (clothing, vehicles, architecture)
**Mitigation:** asset_judge should downgrade confidence if metadata suspects errors

### Issue 3: Rights Info Inconsistent
**Problem:** Same image on different archives may have different license claims
**Workaround:** Prioritize sources known for accuracy (LOC > random site)
**Mitigation:** Flag confidence < 0.80 for human review

### Issue 4: Low Coverage for Obscure Topics
**Problem:** Some queries (obscure historical figures, remote locations) return 0 results
**Workaround:** Broaden query (remove era, remove modifiers), try different terms
**Mitigation:** Fall back to AI generation; log gap for archive expansion in Phase 4

---

## Success Criteria

### Phase 1
- [ ] All 4 finder agents + asset_judge agent running
- [ ] archive-image-search skill tested and working
- [ ] Manual test of 1 WWII video: > 70% of scenes get real asset with score > 0.72
- [ ] No broken URLs in output
- [ ] No rights violations in Phase 1 test run

### Phase 2
- [ ] video_finder agent working with public domain videos
- [ ] asset-rights-normalizer integrated; all returned candidates have verified rights
- [ ] Automated Branch 4 run for account 003 WWII videos
- [ ] First 5 automated runs show no errors

### Phase 3
- [ ] asset-dedup-scorer reducing redundancy
- [ ] Asset Registry tracking all found assets
- [ ] Analytics dashboard showing metrics (candidates found, scores, AI fallback %)
- [ ] Ready for account 005 (dark history) expansion

---

## Next Steps

1. Coordinate with Branch 3 (Visual Planning) to finalize visual_plan.json schema
2. Coordinate with Branch 5 (Image Generation) to confirm asset_candidates.json schema
3. Set up archive-image-search skill on M1
4. Create directory structure for agents
5. Manual test with 1 WWII query
6. Iterate based on Lucca feedback

---

## Contact & Escalation

**Questions about:**
- Skill implementation → Lucca + Claude Code
- Agent prompts/scoring → Lucca + asset_judge feedback loop
- Archive coverage/API issues → Lucca (may need investigation)
- Integration with other branches → Lucca (orchestration)
