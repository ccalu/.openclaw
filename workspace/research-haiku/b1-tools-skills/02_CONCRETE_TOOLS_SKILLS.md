# Branch 1 Tools & Skills — Concrete Recommendations

## OpenClaw Skills Worth Building

### Tier 1: Critical (Must-have for B1 to function)

#### Skill 1: `scene-bible-generator`
**Purpose:** Accept raw script, output structured scene_bible.json  
**Scope:** Decompose parallel_screenplay.py into OpenClaw-friendly skill  
**What it does:**
- Takes raw script + account config + video context
- Calls screenplay agent (GPT-4.1-mini via KMS rotation)
- Validates scene boundaries and word counts
- Extracts continuity data (characters, locations, props)
- Outputs structured JSON with strong schema validation

**Input Contract:**
```json
{
  "script_raw": "string",
  "account_code": "string",
  "language": "string",
  "scene_word_targets": {"min": 50, "max": 250},
  "video_context": {"title": "...", "theme": "..."}
}
```

**Output Contract:**
```json
{
  "scene_bible": {
    "video_id": "uuid",
    "scenes": [{
      "num": 1,
      "text": "polished text",
      "word_count": 120,
      "entities": {
        "characters": ["Name1", "Name2"],
        "locations": ["Loc1"],
        "props": ["Item1"]
      },
      "narrative_beat": "exposition|rising_action|climax|resolution",
      "tone": "somber|triumphant|mysterious"
    }],
    "continuity_extract": {...}
  },
  "validation_report": {...}
}
```

**Model:** GPT-4.1-mini (cheap, screenplay is commodity task)  
**Rate limits:** Semaphore(8) for batch processing  
**Error handling:** Graceful fallback for single-scene failures  
**Integration:** Reads from queue/Google Sheet via dedicated script_fetcher agent

---

#### Skill 2: `script-validator`
**Purpose:** Catch issues before screenplay division  
**What it does:**
- Detects language
- Validates character encoding (special chars that break TTS)
- Checks for placeholder text (e.g., "[DESCRIBE_SCENE]")
- Flags potential narrative issues (huge jumps between scenes, tense shifts)
- Suggests corrections without modifying original

**Model:** GPT-4.1-nano or Haiku (validation is cheap)  
**Output:** JSON report with severity + suggestions

---

#### Skill 3: `continuity-extractor`
**Purpose:** Pull structured entity lists for downstream branches  
**What it does:**
- Parses scene_bible.json
- Extracts all characters (with first mention scene)
- Extracts all locations (with appearance timeline)
- Extracts props and their context
- Cross-references aliases (e.g., "President Lincoln" = "Lincoln" = "Honest Abe")
- Outputs JSON registry for B3 (Visual Planning) and B4 (Asset Research)

**Model:** Haiku or local Ollama (regex + structured extraction)  
**Output:** JSON with character_registry, location_registry, prop_registry + scene cross-refs

---

### Tier 2: Valuable (Nice-to-have, increases quality)

#### Skill 4: `narrative-arc-analyzer`
**Purpose:** Validate pacing and emotional beats  
**What it does:**
- Analyzes scene sequence for narrative coherence
- Detects pacing issues (scenes too similar, no variety)
- Flags emotional arc flatness
- Suggests scene reordering if needed

**Model:** GPT-4.1-mini (needs semantic understanding)  
**Output:** Arc analysis + warnings

---

#### Skill 5: `scene-rebalancer`
**Purpose:** Auto-fix uneven scene lengths  
**What it does:**
- Detects outliers (scenes >350 words or <30 words)
- Suggests splits/merges
- If approved, regenerates affected scenes

**Model:** GPT-4.1-mini  
**Dependencies:** scene-bible-generator

---

#### Skill 6: `language-formatter`
**Purpose:** Apply language-specific TTS optimizations at screenplay level  
**What it does:**
- PT/IT: period→semicolon conversions (for XTTS naturalness)
- CJK: character-level segmentation hints
- EN: contraction expansion check
- ES/FR: accent preservation validation

**Model:** Haiku or regex-based (deterministic rules)  
**Output:** Formatted scene text

---

## Integration Points with Existing v3 System

### Hook into parallel_screenplay.py
- **Where:** CentralizedKeyClient initialization
- **What:** Replace the monolithic parallel processing with OpenClaw skill invocation
- **How:** B1 agent calls scene-bible-generator skill → skill wraps KMS logic → returns JSON
- **Benefit:** Clear separation of concerns, testable, reusable

### Hook into KMS (Key Management System)
- **What:** KMS already exists and is used by v3
- **How:** scene-bible-generator skill should use existing KMS client
- **Key:** CentralizedKeyClient is async; OpenClaw may need wrapper for sync→async bridging

### Hook into Google Sheet polling
- **What:** script_fetcher agent needs to poll for new scripts
- **Recommendation:** Keep Google Sheets API integration in a separate "script_source" adapter
- **B1 skill:** Receives already-fetched script JSON, doesn't own Sheet integration

---

## Not Recommended as Skills (Keep in Agent Prompts Instead)

### Why not skill: "screenplay-divider"
- Too tightly coupled to GPT-4.1-mini specific prompts
- Account-specific prompts vary widely (WWII vs dark history vs sci-fi)
- Better as dynamic prompt in agent's instruction set, not hardcoded skill

### Why not skill: "scene-formatter"
- Language rules change frequently
- Coupled to TTS provider (Gemini vs ElevenLabs vs Elevenlabs have different quirks)
- Better owned by B2 (Audio branch) since it's TTS-specific

---

## Recommended OpenClaw Tools (Not Skills)

### Tool 1: KMS Client Wrapper
**Purpose:** Async KMS key management for screenplay agents  
**What it does:**
- Wraps existing CentralizedKeyClient
- Exposes simple `get_key(provider, model)` interface
- Handles rotation, cooldowns, cost tracking
- Logs to OpenClaw heartbeat for monitoring

**Integration:** scene-bible-generator skill uses this

---

### Tool 2: Script Source Adapter
**Purpose:** Fetch scripts from multiple sources (Google Sheet, queue, webhook)  
**What it does:**
- Abstract script fetching
- Supports Google Sheets, local JSON files, Telegram messages
- Returns normalized ScriptInput schema
- Caches to avoid redundant fetches

---

### Tool 3: Validation Report Formatter
**Purpose:** Normalize validation output for B1→B2→B3 handoff  
**What it does:**
- Takes raw validation JSON
- Formats for human readability + machine parsing
- Logs to Telegram + returns to PM

---

## Structured Output / Contracts Recommended

### Core Schemas (Pydantic or JSON Schema)

**1. ScriptInput**
```json
{
  "script_raw": "string (raw text)",
  "account_code": "string (003_wwii)",
  "language": "string (en, pt, es, fr, it, de)",
  "video_context": {
    "title": "string",
    "theme": "string",
    "channel_style": "string",
    "estimated_duration_sec": "int"
  },
  "config": {
    "scene_word_min": "int (default 50)",
    "scene_word_max": "int (default 250)"
  }
}
```

**2. Scene**
```json
{
  "num": "int",
  "text": "string (screenplay for this scene)",
  "word_count": "int",
  "char_count": "int",
  "estimated_duration_sec": "float",
  "entities": {
    "characters": ["string"],
    "locations": ["string"],
    "props": ["string"],
    "timezones": ["string (if relevant)"]
  },
  "narrative": {
    "beat": "enum (exposition|rising|climax|resolution|transition)",
    "tone": "enum (somber|triumphant|mysterious|comedic|tense|peaceful)",
    "pov": "string (first_person|third_person|omniscient)"
  },
  "continuity": {
    "speaker_primary": "string (character name or 'narrator')",
    "speakers": ["string"],
    "transitions": {
      "from_scene": "int (previous scene num, or null)",
      "to_scene": "int (next scene num, or null)"
    }
  },
  "validation": {
    "is_valid": "bool",
    "warnings": ["string"],
    "issues": ["string"]
  }
}
```

**3. SceneBible**
```json
{
  "metadata": {
    "video_id": "string (uuid)",
    "account_code": "string",
    "language": "string",
    "created_at": "timestamp",
    "version": "int"
  },
  "script_summary": {
    "title": "string",
    "theme": "string",
    "total_word_count": "int",
    "total_scenes": "int",
    "estimated_duration_sec": "float"
  },
  "scenes": ["Scene[]"],
  "continuity_extract": {
    "characters": [
      {
        "name": "string",
        "aliases": ["string"],
        "first_appearance_scene": "int",
        "all_scenes": ["int"],
        "role": "enum (protagonist|antagonist|supporting|mention_only)"
      }
    ],
    "locations": [
      {
        "name": "string",
        "aliases": ["string"],
        "first_appearance_scene": "int",
        "all_scenes": ["int"],
        "era": "string (if historical)"
      }
    ],
    "props": [
      {
        "name": "string",
        "aliases": ["string"],
        "first_appearance_scene": "int",
        "all_scenes": ["int"],
        "significance": "enum (critical|supporting|background)"
      }
    ]
  },
  "validation_report": {
    "is_valid": "bool",
    "critical_issues": ["string"],
    "warnings": ["string"],
    "score": "float (0-100, readiness for downstream)"
  }
}
```

**4. ContinuityExtract** (subset for B3/B4)
```json
{
  "characters": [
    {
      "name": "string",
      "aliases": ["string"],
      "scenes": [{"num": "int", "first_mention": "bool"}],
      "descriptions": ["string (from screenplay context)"]
    }
  ],
  "locations": [
    {
      "name": "string",
      "aliases": ["string"],
      "scenes": ["int"],
      "era": "string (if historical)"
    }
  ],
  "props": [
    {
      "name": "string",
      "scenes": ["int"],
      "context": "string"
    }
  ]
}
```

---

## Cheap Model Workflow (Haiku Budget)

### Recommended Model Routing for B1

| Task | Model | Cost | Rationale |
|------|-------|------|-----------|
| Script validation | Haiku | ~$0.01 | Lightweight, fast |
| Screenplay division | GPT-4.1-mini (KMS) | ~$0.05/video | Existing, proven |
| Continuity extraction | Haiku | ~$0.01 | Structured entity extraction |
| Narrative arc check | GPT-4.1-mini | ~$0.03 | Semantic analysis |
| Scene rebalancing | GPT-4.1-mini | ~$0.03 | If needed |
| Language formatting | Ollama Qwen (local) | $0 | Deterministic rules |

**Total per video (B1 only):** ~$0.13 (screenplay) + ~$0.15 (optional checks) = **$0.13-0.28/video**

**For 40 videos/week:** ~$5-11/week, or ~$20-44/month for B1 alone

---

## Implementation Priority

1. **Week 1:** scene-bible-generator skill (critical path blocker)
2. **Week 1:** Formalize SceneBible + ContinuityExtract JSON schemas
3. **Week 2:** script-validator skill (quality gate)
4. **Week 2:** KMS client wrapper + integration
5. **Week 3:** continuity-extractor skill (B3/B4 dependency)
6. **Week 4+:** Narrative analysis + rebalancing (nice-to-have)
