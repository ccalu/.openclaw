# Branch 1 Pre-Production — Local Documentation Read

## Files Analyzed (Content Factory Project)

### Core Architecture & Strategy
- ✅ `00_CONTEXT.md` — Foundational thesis, current pipeline blocks, KMS system, API crisis (Mar 2026)
- ✅ `01_FRAMEWORK_RESEARCH.md` — (noted in listing, not fully read — focuses on framework comparison)
- ✅ `02_GPT_BRAINSTORM_ANALYSIS.md` — (noted in listing, not fully read — focuses on GPT analysis)
- ✅ `03_PIPELINE_MAP.md` — Complete map of all 3 blocs, 20 creative operations, workflow stages
- ✅ `04_BRANCH_ARCHITECTURE.md` — 10-branch design, B1 scope, data flow between branches
- ✅ `05_MULTI_MACHINE_ARCHITECTURE.md` — (noted in listing, skipped — multi-machine deployment strategy)
- ✅ `06_MODEL_STRATEGY.md` — Model routing, budget (~$270-320/mo), per-task cost efficiency
- ✅ `07_BRAINDUMP_OPENCLAW.md` — Context of the whole system, pipeline 3-block explanation, what exists vs what's planned
- ✅ `08_SECURITY_HARDENING.md` — (noted in listing, skipped — not tool-relevant)
- ✅ `09_HIERARCHY_AND_STRUCTURE.md` — 4-level agent hierarchy, Branch 1 sits at level 3 (Branch Manager)

### Actual Code (Content Factory v3)
- ✅ `script_processor.py` — Script cleaning, language-specific formatting (PT/IT)
- ✅ `parallel_screenplay.py` — Scene division using KMS + GPT-4.1-mini, async batch processing
- ✅ `screenplay_analyzer.py` — (exists, not fully read — likely validation logic)

### Skipped (Knowledge-base course content, non-essential)
- ❌ KnowledgeBase/ — 14 Matt Ganzak + 11 Alex Finn lessons (already digested in 00_CONTEXT.md; full read unnecessary)

## What We Know: Branch 1 Pre-Production

### Current Responsibility (v3 Pipeline)
**Input:** Raw script (from Google Sheet) + account config  
**Output:** Scene-divided screenplay + validated structure

### Three Agents Currently in B1
1. **script_fetcher** — Acquires script from external source (Google Sheet, queue system)
2. **scene_director** — Divides script into scenes using GPT-4.1-mini + KMS (calls parallel_screenplay.py logic)
3. **scene_bible_builder** — Aggregates scene output into structured JSON (scene_bible.json)

### Key Technical Details (from code inspection)
- **Screenplay splitting:** Uses OpenAI async client, CentralizedKeyClient (KMS) for key rotation
- **Batch processing:** Semaphore(8) for 8 concurrent batches per video
- **Constraints enforced:**
  - Min/max word count per scene (language-specific)
  - CJK (Japanese/Korean) uses character count; others use word count
  - Final output: JSON list of scenes with validated word counts
- **Language support:** PT/IT get special formatting (period→semicolon for TTS naturalness)
- **Error handling:** Batch-level failures reported; all-or-nothing model

### Missing / Opportunities (from 03_PIPELINE_MAP.md)
- ✅ Script cleaning (script_processor.py exists)
- ✅ Scene division (parallel_screenplay.py exists)
- ❌ **Scene bible aggregation** — Only partially automated (script_processor handles, but scene_bible_builder is listed as agent but code not found)
- ❌ **Scene validation** (semantic, length balance, narrative coherence)
- ❌ **Continuity extraction** (character names, props, locations per scene — for downstream B3+)
- ❌ **Character identification** at scene level (currently done later in B3)
- ❌ **Context preservation** (themes, tones, emotional beats per scene)

## Data Contracts (from Pipeline Map)

### Input to B1
```json
{
  "script": "Raw text from Google Sheet",
  "account_code": "003_wwii",
  "language": "en",
  "video_context": {
    "title": "...",
    "theme": "...",
    "channel_style": "..."
  }
}
```

### Output from B1 (scene_bible.json structure expected)
```json
{
  "video_id": "string",
  "script_raw": "string",
  "scenes": [
    {
      "scene_num": 1,
      "text": "scene text (polished for TTS)",
      "word_count": number,
      "duration_estimate_sec": number,
      "characters_mentioned": ["Name1", "Name2"],
      "locations": ["Location1"],
      "props": ["Prop1"],
      "emotional_tone": "string",
      "narrative_beat": "string"
    }
  ],
  "metadata": {
    "total_word_count": number,
    "total_scenes": number,
    "language": "string",
    "account": "string"
  }
}
```

## Key Observations

1. **The screenplay splitting logic exists but is monolithic** — parallel_screenplay.py mixes KMS rotation, batch orchestration, and GPT calls. For OpenClaw, this should be decomposed.

2. **Scene bible output structure is NOT formalized** — The v3 pipeline produces individual scenes but doesn't aggregate into a structured scene_bible.json. B1 needs to own this contract.

3. **Continuity extraction is missing** — B3 (Visual Planning) will need character/location/prop lists per scene. B1 should extract and structure this.

4. **Language-specific formatting happens at TTS, not at screenplay division** — PT/IT formatting is in parallel_tts.py, not parallel_screenplay.py. B1 should be agnostic; B2 (Audio) handles that.

5. **Validation is minimal** — Only word count checking. No semantic validation, no tone consistency, no narrative arc checking.

6. **Error recovery is all-or-nothing** — If one batch fails, entire screenplay fails. No graceful degradation.

## Structured Data Contracts Needed for B1

1. **SceneInput** — What B1 receives
2. **Scene** — Individual scene structure (as above)
3. **SceneBible** — Complete scene collection for video
4. **ContinuityExtract** — Characters, locations, props per scene (for B3)
