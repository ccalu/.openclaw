# Branch 4 (Asset Research) — Tools & Skills Analysis

**Date:** 26 Mar 2026  
**Scope:** OpenClaw skills, integrations, tools for real image/video retrieval  
**Context:** Content Factory video-editing department, faceless YouTube production  
**Status:** Research notes for incremental implementation  

---

## What Branch 4 Does

**Function:** Execute visual research phase → find real images and videos for editorial use  
**Input:** Visual strategy from Branch 3 (asset targets: people, locations, events, objects)  
**Output:** Asset candidates JSON + scoring metadata  
**Scale:** 5 agents specialized by asset type  

### Current Pipeline Gap
- Dataset system exists (Library of Congress, Europeana, Smithsonian, Wikimedia) but only configured for account 003 (WWII)
- Manual search fallback: Lucca hand-picks images for most accounts
- No structured rights/copyright tracking
- No deduplication system
- No scoring/relevance ranking
- Video finding is minimal (assumed to be manual or low-priority today)

### Agents Needed
| Agent | Role | Input | Output |
|-------|------|-------|--------|
| **people_finder** | Photo retrieval for persons | {name, era, context} | candidates[] + metadata |
| **location_finder** | Photo/video for places | {location, era, type} | candidates[] + metadata |
| **event_object_finder** | Objects, events, historical moments | {query, era, category} | candidates[] + metadata |
| **video_finder** | Real b-roll, historical footage, clips | {query, era, format} | video_candidates[] + metadata |
| **asset_judge** | Evaluates candidates, decides real vs AI | {candidate, context, constraints} | score + decision + reason |

---

## Required Capabilities (per Agent)

### Common to All Finders
- **Web search** (structured, permission-respecting)
- **Image metadata extraction** (resolution, format, source, license info)
- **Archive API integration** (Library of Congress, Europeana, etc.)
- **Fallback logic** (if API A fails, try B, then C)
- **Deduplication** (avoid same image from multiple sources)
- **Structured output** (JSON candidates with scoring basis)

### people_finder Specific
- **Face search capability** (reverse image, named search)
- **Historical person databases** (Wikipedia, Europeana, LOC collections)
- **Face matching** (simple: era + name, complex: visual embedding search)
- **Era verification** (confirm image matches time period claimed)

### location_finder Specific
- **Geo-tagged search** (location + year)
- **Architectural style matching** (era + visual character)
- **Satellite/aerial footage** (for landscape shots)
- **Street view historical** (Google Street View time machine, archive.org imagery)

### video_finder Specific
- **Video platform search** (YouTube, Archive.org, Vimeo, specialized history channels)
- **B-roll libraries** (Pexels Videos, Pixabay, Coverr, Mixkit)
- **Public domain video archive** (Internet Archive, British Pathé, Getty Historical)
- **Duration/frame detection** (can we extract usable clips?)
- **Licensing verification** (what's actually usable?)

### asset_judge Specific
- **Multi-criteria scoring:**
  - Relevance to context (1-10)
  - Historical accuracy/plausibility (1-10)
  - Visual quality (resolution, color, composition) (1-10)
  - Rights/copyright clearance (binary: safe/risky)
  - Redundancy vs existing assets (1-10)
  - Generic-ness (unique or stock shot?) (1-10)
- **Decision logic:** if score < 0.72 → flag for AI generation
- **Explanation** (why this asset? why this score?)

---

## OpenClaw Skills Worth Building

### Skill 1: Browser-Based Image Retrieval with Fallback
**Name:** `archive-image-search`  
**Purpose:** Structured search across multiple image sources with fallback  
**Building blocks:**
- web_search (Brave API — already available)
- web_fetch (extract metadata from archive results)
- Manual source rotation (LOC → Europeana → Smithsonian → Wikimedia → fallback Google Images)
- Dedup via hash or URL normalization

**Cost:** Cheap — mostly web calls, minimal API calls  
**Complexity:** Low-medium  
**Incremental build:** Start with LOC/Europeana, add Smithsonian/Wikimedia later  

### Skill 2: Video Search & Metadata Extraction
**Name:** `video-archive-finder`  
**Purpose:** Find public domain/CC-licensed video clips for use as b-roll  
**Building blocks:**
- web_search for "site:archive.org [query] filetype:mp4"
- YouTube API search (if needed; can also use web_search)
- Frame detection (ffmpeg integration to check duration, FPS, resolution)
- Licensing verification (parse video metadata, check description)

**Cost:** Cheap — web search + optional ffmpeg calls (local)  
**Complexity:** Medium (video validation requires ffmpeg; might need separate skill)  
**Incremental build:** Start with Archive.org + public domain YouTube channels  

### Skill 3: Rights & Copyright Normalization
**Name:** `asset-rights-normalizer`  
**Purpose:** Extract, normalize, and verify usage rights for any image/video URL  
**Building blocks:**
- Metadata extraction (EXIF, headers, page crawl for license info)
- License parser (CC0, CC-BY, CC-BY-SA, public domain, proprietary)
- Rights scoring (0 = proprietary, 1 = fully free)
- Cache/registry (avoid re-checking same URLs)

**Cost:** Very cheap — mostly parsing, minimal API calls  
**Complexity:** Medium (need canonical license mappings)  
**Incremental build:** Start simple (CC0 + public domain only), expand to CC-BY rules later  

### Skill 4: Image Deduplication & Similarity Scoring
**Name:** `asset-dedup-scorer`  
**Purpose:** Prevent duplicate or near-duplicate assets; score relevance via perceptual hashing  
**Building blocks:**
- Perceptual hash (phash, dhash — lightweight, no GPU needed)
- Similarity comparison (cosine distance between hashes)
- URL normalization (handle redirects, parameters, CDN variations)
- Cache storage (SQLite or JSON file)

**Cost:** Very cheap — all local computation  
**Complexity:** Low-medium (hash algorithms are standard)  
**Incremental build:** Start with exact URL dedup, add perceptual hashing later  

### Skill 5: Browser-Based Image/Video Retrieval (Fallback)
**Name:** `browser-asset-scraper`  
**Purpose:** When API fails, use Playwright/Puppeteer-like automation to search/retrieve from human-friendly sources  
**Building blocks:**
- OpenClaw browser tool (if available; otherwise consider external Playwright call)
- Screenshot-on-search (for visual validation of results)
- Click-and-retrieve flow (Flickr advanced search, NYPL digital collection, etc.)

**Cost:** Moderate — browser automation is resource-intensive  
**Complexity:** High (stateful browser automation)  
**Incremental build:** **Skip for Phase 1** — use web_search + web_fetch instead; add browser fallback only if APIs become unreliable  

### Skill 6: Archival Content Proofing (QA Layer)
**Name:** `asset-proof-validator`  
**Purpose:** Verify asset is actually what we think it is before committing to it  
**Building blocks:**
- Reverse image search (TinEye API, Google Images API — if licensed)
- Visual inspection (is this image what the filename claims?)
- Metadata verification (does publication date match era we need?)
- Integrity check (file corruption? 404 link? expired?)

**Cost:** Moderate (reverse image API calls; can be expensive if not batched)  
**Complexity:** Medium  
**Incremental build:** Start with basic checks (404 test, file size, format); add reverse search later  

---

## Integrations to Build (Not Full Skills, but Connectors)

### Integration 1: Archive.org API Wrapper
**What:** Wrapper around Archive.org's image search + download APIs  
**Why:** Centralized fallback for millions of public domain images  
**Effort:** Low (API is well-documented)  
**Call pattern:** Already available via web_search, but could optimize with direct API  

### Integration 2: Library of Congress API
**What:** Direct LOC API queries (metadata + image retrieval)  
**Why:** Billions of images, excellent metadata, fully public domain  
**Effort:** Low (LOC API is open, well-documented)  
**Note:** Already used in dataset system; could be formalized as skill  

### Integration 3: Europeana API
**What:** Structured access to Europeana's 60M+ cultural heritage objects  
**Why:** Global coverage (Europe, Middle East, Africa), high metadata quality  
**Effort:** Low-medium (requires API key, but freely available)  

### Integration 4: Supabase Vector Store (for Asset Registry)
**What:** Structured JSON storage of found assets with vector embeddings  
**Why:** Centralized asset tracking, fast similarity search, multi-account sharing  
**Effort:** Medium (already exists in pipeline; just needs formalization)  

### Integration 5: FFmpeg Integration (Video Analysis)
**What:** Local ffmpeg calls for video metadata extraction  
**Why:** Determine usable clips, duration, FPS, resolution without downloading  
**Effort:** Low (ffmpeg is available on M1-M6; just need skill wrapper)  

---

## Recommended Contracts & Artifacts

### Artifact 1: Asset Candidate JSON Schema
```json
{
  "id": "asset_uuid_hash",
  "type": "image|video",
  "url": "https://...",
  "source": "loc|europeana|wikimedia|youtube|...",
  "metadata": {
    "title": "...",
    "creator": "...",
    "date": "YYYY-MM-DD or range",
    "format": "jpg|png|mp4|...",
    "resolution": "1920x1080",
    "duration_sec": 45.5,
    "rights": "CC0|CC-BY|public-domain|proprietary",
    "rights_confidence": 0.95
  },
  "relevance_score": 0.87,
  "scoring_basis": {
    "relevance": 9,
    "accuracy": 8,
    "quality": 8,
    "rights_safe": 1.0,
    "redundancy_new": 0.95,
    "generic": 7
  },
  "decision": "use|review|reject|fallback_to_ai",
  "decision_reason": "High relevance to query [person name], era matches, rights clear",
  "fetched_at": "2026-03-26T14:37:00Z"
}
```

### Artifact 2: Branch 4 Job Input Schema (from Branch 3)
```json
{
  "video_id": "...",
  "scene_number": 5,
  "query": {
    "type": "person|location|object|event|video",
    "entity": "Winston Churchill",
    "era": "1940-1945",
    "context": "WWII leader speaking",
    "visual_tone": "historical, formal, documentary"
  },
  "constraints": {
    "min_resolution": "1280x720",
    "prefer_bw": true,
    "safe_for_historical_accuracy": true,
    "no_modern_artifacts": true
  },
  "fallback": "generate_ai_image_if_score_below_0.72"
}
```

### Artifact 3: Asset Registry (Persistent)
```json
{
  "account_id": "003",
  "video_id": "001_wwii_churchill",
  "assets_used": [
    {
      "asset_id": "asset_abc123",
      "scene": 5,
      "role": "churchill_portrait",
      "source": "loc",
      "score": 0.91,
      "url": "...",
      "usage_count": 1
    }
  ],
  "dedup_registry": {
    "url_hashes": ["hash1", "hash2"],
    "perceptual_hashes": ["phash1", "phash2"],
    "last_updated": "2026-03-26T14:37:00Z"
  }
}
```

---

## Cheap Model Workflow (Cost Optimization)

### For Asset Finders (people_finder, location_finder, etc.)
- **Primary:** Web_search + web_fetch (free, already in OpenClaw)
- **Decision logic:** Simple heuristic rules (no LLM unless needed)
- **Fallback:** If web_search returns <3 results, trigger alert to asset_judge

### For asset_judge (Scoring Decision)
- **Light model:** Claude 3.5 Haiku (~$0.008/1k tokens)
- **Prompt structure:** Give it JSON candidate + context, ask for score + reason
- **Batch:** Judge 5-10 candidates per job to amortize API call overhead
- **Cache:** Score same query repeatedly? Cache result for 7 days

### For video_finder (Video Search)
- **Hybrid approach:**
  - Web_search for "site:archive.org [query]" (free)
  - FFmpeg metadata extraction (free, local)
  - Only call LLM if uncertain about usability

### Overall Workflow
```
Branch 3 → {person_finder, location_finder, event_obj_finder, video_finder}
                ↓ (parallel, all web-based)
        5-20 raw candidate URLs per query
                ↓
        asset_judge (1 Haiku call per 5-10 candidates)
                ↓
        Scored candidates JSON → Branch 5 or Branch 6
```

**Cost per video (estimated):**
- Web searches: $0 (free via OpenClaw Brave API)
- Haiku calls (1-2 per video for scoring): ~$0.01
- FFmpeg (local): $0
- **Total: ~$0.01/video for asset research** (vs $5.55 for AI image gen today)

---

## Implementation Phases

### Phase 1 (This Week)
- [ ] Formalize archive-image-search skill (Brave API + LOC/Europeana direct API)
- [ ] Build asset_candidate JSON schema
- [ ] Create people_finder agent (manual testing with 1 query)
- [ ] Create asset_judge agent (manual testing with 5 candidates)

### Phase 2 (Next Week)
- [ ] Add video-archive-finder skill + FFmpeg wrapper
- [ ] Implement asset-rights-normalizer (CC0 + public domain only)
- [ ] Connect asset_judge scoring to decision: "real ≥0.72" vs "generate AI"
- [ ] Test full flow: Branch 3 → finder → judge → output

### Phase 3 (Week After)
- [ ] Add location_finder, event_object_finder
- [ ] Implement asset-dedup-scorer (URL-based, perceptual hashing optional)
- [ ] Set up Asset Registry in Supabase
- [ ] Multi-source fallback logic (LOC → Europeana → Smithsonian → fallback)

### Phase 4 (Ongoing)
- [ ] Browser-based fallback (Skill 5) — only if APIs become unreliable
- [ ] Reverse image validation (asset-proof-validator) — batch TinEye calls
- [ ] Analytics: which sources are most productive? Which queries fail?
- [ ] Expand to non-WWII accounts (different eras, regions, themes)

---

## Known Constraints & Risks

### Rate Limits
- Brave API: <1000 calls/day on free tier → use batch requests
- Europeana: 1000 calls/day unless paid
- Solution: Cache results heavily, batch finder calls

### Rights Complexity
- Different sources have different license info quality
- Need canonical mapping (CC-BY-SA variants, regional copyrights, etc.)
- Risk: Using asset we think is CC0 but isn't
- Mitigation: asset_judge flags "risky" assets for human review; Phase 1 only uses CC0/public domain

### Archive.org Reliability
- Public APIs are sometimes slow or rate-limited
- Fallback to mirror archives (Europeana, LOC direct)
- Mitigation: Test API health first; have 3-tier fallback

### Deduplication Complexity
- Perceptual hashing requires image download
- Solution: Use URL normalization + EXIF date/creator as primary dedup; add perceptual hashing only if needed

### Video Licensing
- Most public domain videos are B&W, short, lower resolution
- May need to mix: real archival video + AI-enhanced clip
- Solution: asset_judge can recommend "use real as-is" vs "use real + AI upscale"

---

## Not Building (Out of Scope for Phase 1)

1. **Reverse image search at scale** (TinEye/Google API is expensive; defer to Phase 4)
2. **ML-based visual matching** (too complex; heuristic rules + manual seed sufficient)
3. **Geo-tagging verification** (complex; text search + metadata is good enough)
4. **Browser automation for scraping** (fragile; web_search + API is more reliable)
5. **Custom image hosting** (use found URLs directly; no storage/serving infra needed)
6. **Automated rights negotiation** (impossible; stick to fully free sources)

---

## Summary Table

| Capability | Skill | Model | Cost | Phase | Note |
|-----------|-------|-------|------|-------|------|
| Image search API | archive-image-search | N/A (web) | $0 | 1 | Free Brave API |
| Video search | video-archive-finder | N/A (web) | $0 | 2 | Archive.org + YT |
| Scoring candidates | asset_judge | Haiku | $0.01/video | 1 | Batch 5-10 candidates |
| Rights verification | asset-rights-normalizer | N/A (parse) | $0 | 2 | Rules-based |
| Deduplication | asset-dedup-scorer | N/A (hash) | $0 | 3 | Local computation |
| Visual validation | asset-proof-validator | Haiku | $0.01 | 4 | Defer to Phase 4 |
| Browser fallback | browser-asset-scraper | N/A (automation) | Moderate | 4 | Skip Phase 1 |

---

## Next Step

Fork this research into:
- 02_SKILL_SPECS.md (detailed SKILL.md templates for each skill)
- 03_AGENT_PROMPTS.md (PROMPT.md for each agent)
- 04_INTEGRATION_CHECKLIST.md (how to connect to existing pipeline)
