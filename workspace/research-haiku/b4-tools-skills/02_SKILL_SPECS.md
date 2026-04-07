# Branch 4 Skills — Detailed Specifications

**Date:** 26 Mar 2026  
**For:** Implementation phase  

---

## SKILL 1: archive-image-search

### Purpose
Retrieve images from public archives (LOC, Europeana, Wikimedia, Smithsonian) with fallback chain.

### Template Structure
```
archive-image-search/
├── SKILL.md
├── scripts/
│   ├── loc_search.py
│   ├── europeana_search.py
│   ├── wikimedia_search.py
│   └── fallback_chain.py
└── references/
    ├── LOC_API_docs.md
    ├── license_mappings.json
    └── source_config.yaml
```

### SKILL.md Outline
```markdown
# archive-image-search

## Purpose
Fetch images from public archives via structured APIs and web search fallback.

## Usage
archive-image-search --query "Winston Churchill" --era "1940-1945" --source "loc" --format "json"

## Providers (in fallback order)
1. Library of Congress API (direct)
2. Europeana API (direct)
3. Wikimedia Commons (direct)
4. Smithsonian Collections (direct)
5. Web search (Brave API) as last resort

## Output Schema
```json
{
  "query": "...",
  "results": [
    {
      "source": "loc|europeana|...",
      "url": "https://...",
      "title": "...",
      "creator": "...",
      "date": "YYYY or YYYY-MM-DD",
      "format": "jpg|png|...",
      "resolution": "WIDTHxHEIGHT",
      "rights": "public_domain|cc0|cc_by|...",
      "direct_download_url": "https://..."
    }
  ],
  "source_used": "loc",
  "total_results": 42,
  "search_time_sec": 1.2
}
```

## Configuration
- LOC API key: optional (no auth required but higher rate limit with key)
- Europeana API key: required (free, register at europeana.eu)
- Fallback chain: configurable via source_config.yaml

## Rate Limits
- LOC: 100 req/sec (burst allowed)
- Europeana: 1000 req/day (unless paid)
- Wikimedia: no official limit but be respectful
- Web search (Brave): 1000/day free tier

## Error Handling
- If source A fails, try source B immediately (no wait)
- Log each attempt for debugging
- Return empty array if all sources fail, with error details
```

### Implementation Notes
- **LOC API:** https://libraryofcongress.github.io/data-exploration/ — Use search endpoint
- **Europeana:** https://pro.europeana.eu/page/apis — Requires registration (free), returns 10-100 results per call
- **Wikimedia:** Use Wikimedia API with query builder (no auth required)
- **Config file:** Store API keys in encrypted KMS, not in repo
- **Caching:** Store results in JSON file (archive_search_cache.json) keyed by query hash, expire after 30 days
- **Dedup:** Within results, remove duplicate URLs and near-duplicates via simple string matching

---

## SKILL 2: video-archive-finder

### Purpose
Search for public domain and CC-licensed video clips usable as b-roll or historical footage.

### Template Structure
```
video-archive-finder/
├── SKILL.md
├── scripts/
│   ├── archive_org_video.py
│   ├── youtube_search.py
│   ├── ffmpeg_validate.py
│   └── video_dedup.py
└── references/
    ├── public_domain_video_sources.md
    └── cc_license_check.md
```

### SKILL.md Outline
```markdown
# video-archive-finder

## Purpose
Find usable public domain and CC-licensed video clips for editorial use.

## Usage
video-archive-finder --query "WWII soldiers marching" --era "1940-1945" --min_duration "5" --format "json"

## Providers
1. Archive.org (Internet Archive) — millions of public domain videos
2. YouTube (filtered by CC-licensed channels and playlists)
3. British Pathé (public domain newsreels)
4. Smithsonian Folklife Magazine (CC videos)
5. Public domain broadcast archives

## Output Schema
```json
{
  "query": "...",
  "results": [
    {
      "source": "archive_org|youtube|...",
      "url": "https://...",
      "title": "...",
      "description": "...",
      "date": "YYYY or YYYY-MM-DD",
      "duration_sec": 45.2,
      "resolution": "1920x1080",
      "fps": 24,
      "format": "mp4|webm|...",
      "rights": "public_domain|cc0|cc_by|...",
      "direct_download_url": "https://...",
      "ffmpeg_validated": true,
      "validation_errors": []
    }
  ],
  "source_used": "archive_org",
  "total_results": 12,
  "search_time_sec": 2.3
}
```

## Validation
- FFmpeg check: ensure file exists, has video stream, duration matches
- License verification: parse metadata, check description for CC license
- Resolution filter: if --min_resolution specified, skip < that
- Format check: prefer MP4/WebM, skip exotic codecs

## Rate Limits
- Archive.org: reasonable rate limit (~10 req/sec)
- YouTube: API key required for scale (not used in Phase 1)
- Archive.org direct: download links are direct (no rate limiting for fetch)

## Error Handling
- If FFmpeg validation fails, note in output but don't skip result
- Log video URL separately for manual inspection
- Return detailed validation_errors array
```

### Implementation Notes
- **Archive.org API:** Use https://archive.org/advancedsearch.php?q=..&format=json (easy)
- **FFmpeg validation:** Call `ffmpeg -i {url} -f null -` locally; check return code and duration output
- **YouTube:** Avoid API for Phase 1; use web_search with "site:youtube.com license:CC-BY" filters instead
- **British Pathé:** Maintain seed list of known newsreel collections; search their catalog via web
- **Caching:** Store validated video metadata in JSON; re-validate URLs weekly (some links rot)
- **Error handling:** Video links can break; keep fallback URLs from different sources

---

## SKILL 3: asset-rights-normalizer

### Purpose
Extract, verify, and normalize licensing information for any image/video asset.

### Template Structure
```
asset-rights-normalizer/
├── SKILL.md
├── scripts/
│   ├── metadata_extractor.py
│   ├── license_parser.py
│   └── rights_scorer.py
└── references/
    ├── cc_license_mapping.json
    ├── source_license_rules.json
    └── rights_documentation.md
```

### SKILL.md Outline
```markdown
# asset-rights-normalizer

## Purpose
Extract and normalize rights/licensing metadata for images and videos.

## Usage
asset-rights-normalizer --url "https://loc.gov/..." --source "loc" --format "json"

## Licensing Tiers
- Tier 0 (proprietary): Cannot use without license purchase
- Tier 1 (CC-BY-SA): Can use if attributed and remixes licensed same
- Tier 2 (CC-BY): Can use if attributed
- Tier 3 (CC0): Can use freely, no attribution needed
- Tier 4 (public domain): Can use freely (no copyright)

## Output Schema
```json
{
  "url": "https://...",
  "source": "loc|europeana|youtube|...",
  "rights_info": {
    "license": "CC0|CC-BY|CC-BY-SA|public_domain|proprietary|unknown",
    "attribution_required": false,
    "share_alike_required": false,
    "commercial_use_allowed": true,
    "modifications_allowed": true,
    "confidence": 0.95,
    "evidence": "metadata EXIF IPTC tag"
  },
  "tier": 3,
  "safe_to_use": true,
  "safe_to_use_reason": "CC0 license confirmed via LOC API",
  "usage_restrictions": [],
  "verified_at": "2026-03-26T14:37:00Z"
}
```

## Metadata Sources (Priority Order)
1. HTTP headers (Content-License, Content-Rights)
2. EXIF/IPTC tags (if image file)
3. JSON-LD schema in page <head>
4. Source API documentation (if known source)
5. Page HTML parsing (Creative Commons license badges)
6. Manual lookup table (per-source rules)

## Confidence Scoring
- Explicit metadata (EXIF, API): 0.95-1.0
- Badge/HTML detection: 0.80-0.95
- Implicit (e.g., "Archive.org = public domain"): 0.70-0.85
- Uncertain/unknown: <0.70

## Error Handling
- If cannot determine rights, return tier = unknown, safe_to_use = false
- Suggest manual verification for anything < 0.70 confidence
```

### Implementation Notes
- **Metadata extraction:** Use PIL/Pillow for EXIF, check HTTP headers via requests library
- **License parsing:** Canonicalize CC license variants (CC-BY-2.0, CC-BY-3.0, etc.) to CC-BY
- **Source rules:** Maintain JSON lookup (loc.gov → always public_domain, europeana → check field X, etc.)
- **Confidence:** Score based on evidence source; explicit metadata = 0.95+, inferred = 0.70-0.80
- **Cache:** Store results per URL; if rights_info unchanged after 30 days, skip re-check
- **Fallback:** If all checks fail, return tier = unknown + flag for human review

---

## SKILL 4: asset-dedup-scorer

### Purpose
Detect duplicate or near-duplicate assets; score uniqueness and relevance.

### Template Structure
```
asset-dedup-scorer/
├── SKILL.md
├── scripts/
│   ├── url_normalizer.py
│   ├── perceptual_hash.py
│   └── similarity_engine.py
└── references/
    ├── dedup_cache.db (SQLite)
    └── IMPLEMENTATION_NOTES.md
```

### SKILL.md Outline
```markdown
# asset-dedup-scorer

## Purpose
Detect duplicate/near-duplicate assets; maintain unified asset registry.

## Usage
asset-dedup-scorer --url "https://..." --asset_type "image" --query_context "Winston Churchill" --format "json"

## Deduplication Tiers
- **Tier 1 (Exact):** Same URL (after normalization)
- **Tier 2 (Near):** Different URLs, same image (perceptual hash match)
- **Tier 3 (Similar):** Related assets (same person, location, era but different photo)

## Output Schema
```json
{
  "asset_url": "https://...",
  "duplicate_status": "unique|near_duplicate|exact_duplicate",
  "duplicates": [
    {
      "asset_url": "https://...",
      "source": "loc|europeana|...",
      "similarity_score": 0.98,
      "tier": 1
    }
  ],
  "uniqueness_score": 1.0,
  "relevance_to_context": 0.85,
  "registry_entry_id": "asset_abc123",
  "first_seen": "2026-03-20T10:00:00Z",
  "usage_count": 2,
  "used_in_videos": ["001_wwii_churchill", "002_wwii_generals"]
}
```

## Deduplication Logic
1. Normalize URL (remove query params, redirect chains, UTM params)
2. Check exact match in registry
3. If new, compute perceptual hash
4. Compare against existing hashes (threshold: 85% match = near-duplicate)
5. Log in registry with metadata

## Relevance Scoring
- Context match: does asset match query_context? (0-1)
- Era match: is asset from correct time period? (0-1)
- Freshness: newer/older assets? (0-1)
- Avg of above = relevance_to_context

## Registry
- SQLite or JSON file storing: URL, hash, usage_count, usage_videos, added_date, source
- Indexed by: URL hash, perceptual hash, query context
- Periodic cleanup: remove unused assets after 90 days

## Rate Limits
- None (all local computation)

## Error Handling
- If URL is broken, mark in registry (don't recheck for 7 days)
- If perceptual hash fails, log error but continue with exact match only
```

### Implementation Notes
- **URL normalization:** Remove query params, utm_ params; canonicalize domain (www., https, trailing slash)
- **Perceptual hash:** Use dhash (difference hash) — lightweight, fast, no ML needed
- **Hash comparison:** Hamming distance < 5 out of 64 bits = match
- **Registry:** SQLite with columns: url_hash, perceptual_hash, source, added_date, usage_count, last_used
- **Caching:** Check registry before computing hash (fast lookup)
- **Cleanup:** Mark URLs as "checked_broken" if 404; don't recheck for 1 week

---

## SKILL 5: asset-proof-validator (Phase 4, Not Phase 1)

### Purpose
Verify assets are authentic and match their metadata before committing to use.

### Deferred Implementation
- Complex skill combining image analysis + reverse search
- Requires: TinEye API or Google Images reverse search (expensive)
- Use case: High-stakes editorial (historical accuracy verification)
- Phase 1 scope: Assume archive.org/LOC metadata is reliable enough

### Placeholder SKILL.md
```markdown
# asset-proof-validator

## Purpose
Validate asset authenticity and metadata accuracy (Phase 4).

## Deferred Features
- Reverse image search (TinEye API ~$0.01-0.05 per check)
- Visual similarity to historical references
- Metadata cross-validation with Wikidata/DBpedia
- Fraud detection (deepfakes, anachronisms)

## When to Implement
- If editorial team reports asset quality issues
- If discovery of license violations (using proprietary content)
- If scaling to non-history accounts where authenticity is critical

## Placeholder Output
```json
{
  "asset_url": "...",
  "status": "deferred",
  "reason": "Use archive-image-search + asset-rights-normalizer for Phase 1; add proof validation in Phase 4 if needed"
}
```
```

---

## Summary Table

| Skill | Phase | Dependencies | Model | Cost/Video | Notes |
|-------|-------|--------------|-------|-----------|-------|
| archive-image-search | 1 | Brave API | N/A | $0 | Free web search |
| video-archive-finder | 2 | FFmpeg local | N/A | $0 | Local validation |
| asset-rights-normalizer | 2 | archive-image-search | N/A | $0 | Rules-based parsing |
| asset-dedup-scorer | 3 | archive-image-search | N/A | $0 | Local hashing |
| asset-proof-validator | 4 | TinEye API | N/A | $0.05 | Defer; expensive |

---

## Implementation Checklist for Phase 1

- [ ] Create skill directory structure
- [ ] Write archive-image-search SKILL.md (complete reference docs)
- [ ] Implement LOC API wrapper (Python script)
- [ ] Test LOC search with 3 sample queries
- [ ] Create source_config.yaml with API keys
- [ ] Create license_mappings.json (CC0, public domain)
- [ ] Test fallback chain (LOC → Europeana → fallback)
- [ ] Write integration guide for Branch 4 agents

---

## Next Step

Create 03_AGENT_PROMPTS.md with PROMPT.md templates for:
- people_finder
- location_finder
- event_object_finder
- video_finder
- asset_judge
