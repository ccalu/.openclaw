# Branch 1 Implementation Roadmap

## Overview

This roadmap details how to implement B1 (Pre-Production) as a set of interconnected OpenClaw agents and skills, starting from zero and reaching full operational capability.

**Timeline:** 4-6 weeks  
**Owner:** Claude Code (implementation) + Tobias (oversight)  
**Workspace:** `C:\Users\User-OEM\Desktop\content-factory\auto_content_factory\`

---

## Phase 0: Preparation (Week 0, ~1 day)

### Task 0.1: Set Up Directory Structure
```
auto_content_factory/
├── agents/
│   └── branches/
│       └── 01_pre_production/
│           ├── IDENTITY.md              (B1 manager identity)
│           ├── CONTEXT.md               (B1 context + data flow)
│           ├── agents/
│           │   ├── script_fetcher/
│           │   │   ├── PROMPT.md
│           │   │   ├── input_schema.json
│           │   │   └── output_schema.json
│           │   ├── screenplay_divider/
│           │   │   ├── PROMPT.md
│           │   │   ├── input_schema.json
│           │   │   └── output_schema.json
│           │   ├── scene_bible_builder/
│           │   │   ├── PROMPT.md
│           │   │   ├── input_schema.json
│           │   │   └── output_schema.json
│           │   └── continuity_extractor/
│           │       ├── PROMPT.md
│           │       ├── input_schema.json
│           │       └── output_schema.json
│           └── README.md                (B1 branch overview)
│
├── skills/
│   ├── scene-bible-generator/
│   │   ├── SKILL.md
│   │   ├── scene_bible_generator.py
│   │   ├── schemas/
│   │   │   ├── scene_bible_schema.json
│   │   │   ├── continuity_extract_schema.json
│   │   │   └── validation_report_schema.json
│   │   └── tests/
│   │
│   ├── script-validator/
│   │   ├── SKILL.md
│   │   ├── script_validator.py
│   │   └── rules/
│   │
│   └── continuity-extractor/
│       ├── SKILL.md
│       ├── continuity_extractor.py
│       └── schemas/
│
├── shared/
│   ├── scene_bible/             (runtime output)
│   │   └── .gitkeep
│   ├── validation_reports/
│   │   └── .gitkeep
│   └── schemas/
│       ├── scene_bible_v1.0.json
│       ├── continuity_extract_v1.0.json
│       └── validation_report_v1.0.json
│
└── docs/
    └── BRANCH_1_IMPLEMENTATION.md  (this document)
```

**Task effort:** 30 min (file creation)

---

## Phase 1: Core Schemas (Week 1, ~2-3 days)

### Task 1.1: Formalize JSON Schemas
Create strict JSON Schema files (draft-2020-12) for:
- `scene_bible_v1.0.json` — [from 03_STRUCTURED_ARTIFACTS.md]
- `continuity_extract_v1.0.json`
- `validation_report_v1.0.json`

**Deliverable:** 3 JSON Schema files in `shared/schemas/`  
**Owner:** Claude Code  
**Effort:** 1-2 hours (schema writing + validation)

### Task 1.2: Create Pydantic Models (Python)
If B1 agents will be Python-based:
```python
# shared/models/scene_bible.py
from pydantic import BaseModel, Field
from typing import List, Optional

class Scene(BaseModel):
    id: str
    num: int
    text: str
    word_count: int
    entities: SceneEntities
    narrative: Narrative
    # ... fields from schema

class SceneBible(BaseModel):
    metadata: Metadata
    scenes: List[Scene]
    continuity_extract: ContinuityExtract
    quality_metrics: QualityMetrics
```

**Deliverable:** Pydantic models in `shared/models/`  
**Owner:** Claude Code  
**Effort:** 2 hours

### Task 1.3: Integration Tests for Schemas
Test that:
- Pydantic models validate against JSON Schema
- Sample scene_bible.json passes validation
- Invalid scenes fail validation with clear errors

**Deliverable:** pytest suite in `tests/schema_validation_test.py`  
**Owner:** Claude Code  
**Effort:** 1 hour

---

## Phase 2: Skill Development (Week 1-2, ~4-5 days)

### Task 2.1: Implement `script-validator` Skill

**What it does:**
- Detects language
- Validates character encoding
- Checks for placeholders
- Flags special characters problematic for TTS
- Returns structured validation_report.json

**Code structure:**
```python
# skills/script-validator/script_validator.py
class ScriptValidator:
    def validate(self, script: str, language: str) -> ValidationReport:
        # 1. Language detection (if not provided)
        # 2. Encoding check
        # 3. Placeholder detection
        # 4. Character validation
        # 5. Sanity checks (word count, etc.)
        return ValidationReport(...)
```

**Model:** Haiku for semantic checks; regex for structural  
**Tests:** Unit tests for each validation type  
**Deliverable:** SKILL.md + Python implementation  
**Owner:** Claude Code  
**Effort:** 1 day

### Task 2.2: Implement `screenplay-divider` Skill

**What it does:**
- Accepts script + constraints (word count per scene)
- Calls GPT-4.1-mini via KMS for scene splitting
- Validates output (word counts, required fields)
- Returns list of Scene objects

**Code structure:**
```python
# skills/scene-bible-generator/screenplay_divider.py
class ScreenplayDivider:
    async def divide(self, script: str, constraints: SceneConstraints) -> List[Scene]:
        # 1. Batch script if needed
        # 2. Call GPT-4.1-mini via KMS (parallel)
        # 3. Validate each scene
        # 4. Merge back into order
        # 5. Return scenes
```

**Integration:** Reuse logic from `parallel_screenplay.py` (content_factory_v3)  
**KMS integration:** Create KMS wrapper that OpenClaw agents can call  
**Tests:** Integration test with mock KMS  
**Deliverable:** SKILL.md + Python implementation  
**Owner:** Claude Code  
**Effort:** 1.5 days

### Task 2.3: Implement `continuity-extractor` Skill

**What it does:**
- Parses scene_bible.json
- Extracts entities (characters, locations, props)
- Detects aliases using Haiku or Ollama
- Creates lookup tables
- Returns continuity_extract.json

**Code structure:**
```python
# skills/continuity-extractor/continuity_extractor.py
class ContinuityExtractor:
    def extract(self, scene_bible: SceneBible) -> ContinuityExtract:
        # 1. Iterate scenes, collect entities
        # 2. Deduplicate + alias detection
        # 3. Build character_registry, location_registry, prop_registry
        # 4. Create lookup tables (character_by_scene, etc.)
        # 5. Return ContinuityExtract
```

**Model options:**
- Haiku for alias detection ($0.008)
- Ollama for alias detection ($0, local)
- Regex fallback (free, 80% accurate)

**Tests:** Unit tests for entity extraction, alias detection  
**Deliverable:** SKILL.md + Python implementation  
**Owner:** Claude Code  
**Effort:** 1 day

---

## Phase 3: OpenClaw Agent Integration (Week 2-3, ~4-5 days)

### Task 3.1: Create B1 Branch Manager Agent

**IDENTITY.md:**
```
Name: B1 Pre-Production Manager
Scope: Orchestrate screenplay division, continuity extraction, scene bible aggregation
Model: GPT-4.1-mini (routing coordination) or Haiku (lightweight)
Inputs: script_raw + account_config
Outputs: scene_bible.json, continuity_extract.json
```

**Responsibilities:**
- Receive script from script_fetcher
- Route through validation → screenplay division → extraction
- Aggregate outputs into scene_bible.json
- Validate schema before write
- Report status + cost to Production Manager

**CONTEXT.md:**
- Link to branch architecture (04_BRANCH_ARCHITECTURE.md)
- List of agents under B1
- Data flow diagram
- Dependencies (KMS, Google Sheets, shared/)

**README.md:**
- Quick overview
- How to invoke B1
- Expected input/output
- Troubleshooting

**Deliverable:** 3 markdown files in `agents/branches/01_pre_production/`  
**Owner:** Claude Code (writing) + Tobias (review)  
**Effort:** 4 hours

### Task 3.2: Create Script Fetcher Agent

**PROMPT.md:**
```
You are the Script Fetcher for B1 Pre-Production.

Your job: Fetch raw scripts from the queue (Google Sheet or JSON queue) and hand
off to the B1 manager for processing.

Input: {video_id, account_code, language}
Output: {script_raw, video_context}

Steps:
1. Query queue system for script with video_id
2. Validate that script exists
3. Load account_config (style guide, prompts, etc.)
4. Extract video_context (title, theme, duration estimate)
5. Return ScriptInput JSON
```

**Input/Output schemas:**
```json
{
  "input": {
    "video_id": "550e8400-...",
    "account_code": "003_wwii"
  },
  "output": {
    "script_raw": "...",
    "video_context": {...},
    "account_config": {...}
  }
}
```

**Model:** Haiku (fetching is lightweight)  
**Deliverable:** PROMPT.md + input/output schemas  
**Owner:** Claude Code  
**Effort:** 2 hours

### Task 3.3: Create Screenplay Divider Agent

**PROMPT.md:**
- Calls the screenplay-divider skill
- Validates output
- Handles errors (KMS exhaustion, GPT failures)
- Returns list of Scene objects

**Integration:**
- Calls skill: `scene-bible-generator` (or `screenplay-divider` subset)
- Reports to B1 manager on success/failure
- Cost logging

**Model:** Coordinator with Haiku; execution via GPT-4.1-mini skill  
**Deliverable:** PROMPT.md + input/output schemas  
**Owner:** Claude Code  
**Effort:** 3 hours

### Task 3.4: Create Scene Bible Builder Agent

**PROMPT.md:**
- Aggregates screenplay output
- Calls continuity-extractor skill
- Computes quality metrics (pacing, emotional variety, narrative arc)
- Validates full scene_bible.json against schema
- Writes to `shared/scene_bible/{video_id}/scene_bible.json`

**Validation logic:**
- All required fields populated
- No duplicate scene numbers
- Scene order is sequential
- Word counts match specified constraints

**Error handling:**
- If scene missing text, return error (skip write)
- If validation fails, report to B1 manager + Production Manager
- Fallback: Write to `shared/scene_bible/{video_id}/draft/` for manual review

**Model:** Haiku for coordination; Ollama/Haiku for extraction  
**Deliverable:** PROMPT.md + validation logic  
**Owner:** Claude Code  
**Effort:** 1 day

### Task 3.5: Create Continuity Extractor Agent

**PROMPT.md:**
- Calls continuity-extractor skill
- Adds search hints for B4 (Asset Research)
- Adds visual notes for B3 (Visual Planning)
- Writes to `shared/scene_bible/{video_id}/continuity_extract.json`

**Search hint logic:**
```
For each character:
  - is_real_person: check Wikipedia
  - search_terms: ["General Keitel", "Wilhelm Keitel", "1888-1946"]
For each location:
  - is_real_place: check Wikidata
  - search_terms: ["Berlin Bunker", "Führerbunker", "1945"]
```

**Model:** Haiku  
**Deliverable:** PROMPT.md  
**Owner:** Claude Code  
**Effort:** 4 hours

---

## Phase 4: KMS Integration (Week 2, ~2-3 days)

### Task 4.1: Create KMS Client Wrapper

**Why:** screenplay-divider skill needs clean access to KMS key rotation  
**What:**
```python
# shared/kms_client_wrapper.py
class KMSClientWrapper:
    async def get_screenplay_key(self) -> OpenAIKey:
        # Query KMS for available GPT-4.1-mini key
        # Apply cooldown if needed
        # Return key + expiry hint
    
    async def call_screenplay_api(self, prompt, constraints) -> dict:
        # Get key from KMS
        # Call OpenAI with key
        # Log cost to OpenClaw
        # Handle 429 gracefully (retry with backoff)
```

**Integration points:**
- Query KMS server (URL from config)
- Machine ID (from OpenClaw config)
- Cost tracking for B10 (Monitoring)

**Tests:** Unit test with mock KMS  
**Deliverable:** Python wrapper + documentation  
**Owner:** Claude Code  
**Effort:** 1 day

### Task 4.2: Test KMS Integration with Screenplay Divider

**Steps:**
1. Create test script (short, 10 scenes)
2. Call screenplay-divider skill with real KMS
3. Verify output matches schema
4. Check cost in KMS logs
5. Test fallback (if primary key fails)

**Deliverable:** Integration test + report of actual costs  
**Owner:** Claude Code  
**Effort:** 4 hours

---

## Phase 5: End-to-End Testing (Week 3, ~2 days)

### Task 5.1: Create Test Data

**Test scripts:**
- `test_script_en.txt` — English, 2000 words, 8 scenes
- `test_script_pt.txt` — Portuguese, 1800 words, 7 scenes
- `test_script_edge_cases.txt` — Special chars, placeholders, etc.

**Expected outputs:**
- `expected_scene_bible_en.json`
- `expected_continuity_en.json`
- `expected_validation_report_en.json`

**Deliverable:** Test data in `tests/data/`  
**Owner:** Claude Code  
**Effort:** 4 hours

### Task 5.2: End-to-End Pipeline Test

**Steps:**
1. script_fetcher → load test script
2. script_validator → validate (expect PASS)
3. screenplay_divider → split into scenes
4. continuity_extractor → extract entities
5. scene_bible_builder → aggregate + write
6. Validate output against schema
7. Check that files exist in `shared/scene_bible/`

**Coverage:**
- Happy path (valid script)
- Sad path (invalid script)
- Edge cases (special characters, long scenes, etc.)

**Deliverable:** pytest suite, results report  
**Owner:** Claude Code  
**Effort:** 1 day

### Task 5.3: Cost Analysis Report

**What to measure:**
- Total cost per video (script validation + screenplay + extraction)
- Token usage per step
- Fallback rate (how often KMS exhausted)
- Quality scores (comparison to expected)

**Deliverable:** CSV report + interpretation  
**Owner:** Claude Code  
**Effort:** 2 hours

---

## Phase 6: Production Readiness (Week 4, ~2-3 days)

### Task 6.1: Error Handling & Logging

**Implement for all agents:**
- Try/catch around skill calls
- Meaningful error messages (not stack traces)
- Logging to OpenClaw heartbeat
- Fallback strategies (retry, degrade, halt)

**Example:**
```python
try:
    result = screenplay_divider.divide(script, constraints)
except RateLimitError:
    # Fallback: queue for retry in 5 min
    logger.warning("GPT-4.1-mini rate limited, queueing retry")
    return {"status": "queued", "retry_at": now + 5min}
except ValidationError as e:
    # Fatal error: report to PM
    logger.error(f"Scene validation failed: {e}")
    return {"status": "failed", "errors": [str(e)]}
```

**Deliverable:** Error handling across B1 agents  
**Owner:** Claude Code  
**Effort:** 1 day

### Task 6.2: Monitoring & Alerts

**What B10 (Monitoring) should track:**
- B1 success rate (% of videos processed successfully)
- B1 cost per video (rolling average)
- B1 latency (time from script → scene_bible)
- Top errors (what fails most often)

**Implementation:**
- B1 agents log structured JSON to `shared/logs/b1_events.jsonl`
- B10 agent reads and summarizes
- Telegram alerts if success rate < 95%

**Deliverable:** Logging code + B10 integration points  
**Owner:** Claude Code  
**Effort:** 1 day

### Task 6.3: Documentation for Operators

**Create:**
- `RUNNING_B1.md` — How to invoke B1 from Production Manager
- `TROUBLESHOOTING_B1.md` — Common errors + fixes
- `EXTENDING_B1.md` — How to add new validation checks

**Deliverable:** 3 markdown files in `agents/branches/01_pre_production/`  
**Owner:** Tobias (writing) + Claude Code (review)  
**Effort:** 2 hours

---

## Phase 7: Handoff to Tobias (Week 4, ~1 day)

### Task 7.1: Training & Transition

**What Tobias needs to know:**
1. How to manually invoke B1 agents (for testing)
2. How to interpret scene_bible.json
3. How to troubleshoot common B1 failures
4. Cost implications of changes
5. How to add new validation rules

**Deliverable:** Live walkthrough + documentation  
**Owner:** Claude Code (demonstration) + Tobias (learning)  
**Effort:** 3-4 hours

### Task 7.2: Handoff Checklist

- [ ] All agents can be invoked independently
- [ ] All scripts pass through validation
- [ ] scene_bible.json schema validated
- [ ] continuity_extract.json matches expectations
- [ ] Cost tracking working (B10 sees data)
- [ ] Error handling tested (script fails gracefully)
- [ ] Documentation complete
- [ ] Production Manager can invoke B1

---

## Timeline Summary

| Phase | Week | Tasks | Effort |
|-------|------|-------|--------|
| 0 | 0 | Directory setup | 0.5d |
| 1 | 1 | JSON schemas + Pydantic | 2.5d |
| 2 | 1-2 | 3 skills (validator, divider, extractor) | 4.5d |
| 3 | 2-3 | 5 agents (manager, fetcher, divider, builder, extractor) | 4.5d |
| 4 | 2 | KMS integration + testing | 2d |
| 5 | 3 | End-to-end testing | 2d |
| 6 | 4 | Production readiness (errors, monitoring, docs) | 2.5d |
| 7 | 4 | Handoff & training | 1d |
| **TOTAL** | **4 weeks** | **~19 days effort** | **~25 calendar days** |

**Actual timeline:** 4-6 weeks (accounting for review cycles, testing iteration)

---

## Success Criteria

B1 is ready for production when:

1. ✅ All agents can execute independently and in sequence
2. ✅ 100% of valid scripts produce schema-compliant scene_bible.json
3. ✅ Invalid scripts fail gracefully with clear error messages
4. ✅ continuity_extract.json is 95%+ accurate (manual spot check)
5. ✅ Cost per video is <$0.20 (including KMS overhead)
6. ✅ Latency < 2 min per script (including parallel processing)
7. ✅ B10 (Monitoring) can track B1 metrics
8. ✅ Production Manager can invoke B1 without Claude Code help
9. ✅ Documentation is complete and tested

---

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| KMS key exhaustion | Implement fallback to OpenRouter; queue scripts for retry |
| GPT-4.1-mini hallucination | Add validation layer (scene count, word count checks) |
| Schema evolution | Version schemas; support backward compatibility |
| Haiku failures on Haiku tasks | Fallback to Ollama local for continuity extraction |
| Continuity aliases missing | Manual review + feedback loop to improve Haiku prompt |
| High latency (>5 min) | Parallelize screenplay division (Semaphore(8)) |

---

## Next Steps After Phase 7

Once B1 is complete:
1. Integrate with Production Manager (accesses B1 output)
2. Integrate with B2 (Audio) — validates scene_bible.json
3. Integrate with B3 (Visual Planning) — uses continuity_extract.json
4. Run pilot production (10-20 videos through full pipeline B1→B2→B3→...)
