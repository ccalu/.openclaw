# Recommended agents / skills for Branch 1 (Pre-Production)

## Recommended branch structure

### Branch Manager: `01_pre_production`
Responsibilities:
- receive a job from Production Manager
- orchestrate the B1 agent sequence
- enforce schema / validation gates
- publish `scene_bible` artifacts for downstream branches

### Agent 1: `script_fetcher`
Cheap / mostly deterministic.

**Job**
- pull script/title/account/language metadata from the current source of truth
- normalize text
- assign a `video_id`
- write raw input artifact

**Output**
- `input_script.json`
- `input_script.md`

**Good fit for**
- deterministic code/script + very small LLM use only if cleanup heuristics are needed

### Agent 2: `scene_director`
This is the real cognitive core of B1.

**Job**
- split script into scenes
- define scene goals and narrative beats
- classify each scene
- mark continuity anchors
- estimate scene complexity / importance

**Recommended output fields per scene**
- `scene_id`
- `sequence`
- `title`
- `text`
- `summary`
- `narrative_function` (setup / escalation / reveal / explanation / payoff / transition etc.)
- `emotional_tone`
- `information_density` (low / medium / high)
- `visual_priority` (low / medium / high)
- `continuity_entities` (people, places, objects, concepts)
- `must_show_or_imply`
- `risk_flags` (ambiguity, chronology uncertainty, missing context, sensitive content)
- `downstream_hints` (very lightweight, not full visual planning)

**Why this matters**
If the output is good here, downstream branches can be narrower and cheaper.

### Agent 3: `scene_bible_builder`
Turns the scene plan into the canonical contract artifact.

**Job**
- compile scene list + video metadata + branch-level summary
- validate total coverage and schema
- create machine-readable and human-readable versions
- optionally create diff/version metadata when rerun

**Outputs**
- `scene_bible.json`
- `scene_bible.md`
- `scene_bible_validation.json`

## Recommended extra micro-agents or skills (worth adding)

The docs currently mention 3 B1 agents. That is fine for v1, but B1 becomes more robust if split slightly further.

### Optional Agent 4: `scene_validator`
A cheap guardrail agent or deterministic validator.

**Job**
- verify all script text is covered by scenes
- verify no scene is empty or duplicated
- check size thresholds
- flag suspicious splits
- reject malformed JSON

This should be cheap and mostly deterministic.

### Optional Agent 5: `continuity_extractor`
Very useful if history/drama videos depend on recurring characters, places, or timelines.

**Job**
- extract cross-scene entities
- normalize names / aliases
- produce continuity anchors that B3/B4/B5 can use later

Could eventually feed `character_bible` automatically.

## Best cheap implementation path

### V1 (very practical)
1. deterministic fetch / cleanup
2. one LLM call for scene split + semantic labeling
3. one deterministic validation pass
4. one artifact builder pass

This gives most of the benefit fast.

### V2
Add:
- continuity extraction
- chronology flags
- confidence scores
- rerun/review workflow when validation fails

### V3
Add:
- account-specific B1 rules (`accounts/<id>/prompts`, `constraints`, style guide hooks)
- adaptive scene granularity by niche/account/language
- compare against previous successful videos from the same channel

## Strong candidate skills for B1

These are not third-party install recommendations. They are good custom skills to author locally for this project.

### Skill: `scene-bible-schema`
Purpose:
- teach agents the canonical schema for `scene_bible.json`
- include required fields, field meanings, examples, validation rules

Why valuable:
- reduces drift across reruns/models
- makes downstream parsing stable
- turns docs into infrastructure

### Skill: `narrative-scene-splitting`
Purpose:
- teach how to split scripts by narrative function, not only by token count
- include heuristics for when to keep a beat together or split it

Heuristics to encode:
- split on narrative shift, not every paragraph
- keep cause-effect pairs together unless duration constraints force separation
- preserve reveals and punchlines
- avoid scenes that contain multiple unrelated editorial jobs

### Skill: `preproduction-validation`
Purpose:
- deterministic and semi-deterministic QA rules for B1 outputs
- coverage checks, ID rules, schema rules, ambiguity warnings

### Skill: `channel-b1-rules`
Purpose:
- bind account/channel constraints into B1 only
- e.g. documentary/history channels may need chronology anchors and factual uncertainty flags

This avoids polluting generic B1 prompts with per-account style noise.

## Suggested `scene_bible` contract

A practical top-level structure:

```json
{
  "video_id": "...",
  "account_id": "...",
  "language": "pt-BR",
  "source": {
    "title": "...",
    "script_origin": "google_sheet",
    "fetched_at": "..."
  },
  "video_summary": "...",
  "narrative_arc": {
    "hook": "...",
    "core_question": "...",
    "stakes": "...",
    "resolution": "..."
  },
  "scenes": [],
  "continuity": {
    "characters": [],
    "locations": [],
    "objects": [],
    "timeline_markers": []
  },
  "validation": {
    "full_coverage": true,
    "schema_valid": true,
    "warnings": []
  }
}
```

## Model/cost guidance

Given the project docs and cost sensitivity:
- use a cheap text model for `scene_director` first
- only escalate to better models when:
  - the script is unusually complex
  - validation fails repeatedly
  - the niche requires high factual/structural precision

B1 should be one of the cheapest creative branches in the system.

## Main recommendation

Do **not** make B1 overly clever in v1.
Its job is to create a stable semantic contract for the rest of the pipeline.
A boring, consistent, validated scene bible is more valuable than an impressive but unstable “creative director” prompt.
