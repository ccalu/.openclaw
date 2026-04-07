# Branch 1 Structured Artifacts & Contracts

## Why Structured Artifacts?

Branch 1 is the _gateway_ — it ingests raw data and structures it. Everything downstream (B2-B8) depends on the **quality, schema consistency, and completeness** of B1 output.

In the current v3 pipeline, B1 output is loosely structured. For OpenClaw agent hierarchy, we need **explicit, validated contracts** that:
1. Enable clear error boundaries
2. Allow downstream agents to validate input before processing
3. Support monitoring and quality gates
4. Enable easy schema evolution

---

## Proposed Core Artifacts

### Artifact 1: `scene_bible.json`

**Purpose:** Central source of truth for all scenes in a video  
**Owner:** B1 (Pre-Production) creates; all branches (B2-B9) read  
**Schema:**

```json
{
  "$schema": "https://content-factory.local/schema/scene-bible/v1.0.json",
  "metadata": {
    "video_id": "550e8400-e29b-41d4-a716-446655440000",
    "account": {
      "code": "003_wwii",
      "name": "WWII Stories",
      "language": "en"
    },
    "created_at": "2026-03-26T14:37:00Z",
    "updated_at": "2026-03-26T14:37:00Z",
    "created_by": "scene_bible_builder (B1)",
    "version": "1",
    "status": "draft|validated|approved|locked"
  },
  
  "script_summary": {
    "title": "The Last Dispatch",
    "theme": "military|history|drama",
    "synopsis": "string (50-200 chars)",
    "estimated_duration_sec": 420,
    "total_word_count": 2400,
    "total_scenes": 8,
    "language_code": "en",
    "cjk_language": false
  },
  
  "scenes": [
    {
      "id": "scene_001",
      "num": 1,
      "title": "The Bunker",
      "text": "In the depths of a Berlin bunker, 1945. General Keitel stared at the radio receiver. The war was lost. Nothing remained but...",
      
      "content_metrics": {
        "word_count": 120,
        "char_count": 687,
        "estimated_duration_sec": 35,
        "sentence_count": 8,
        "avg_sentence_length": 15
      },
      
      "entities": {
        "characters": [
          {
            "name": "General Keitel",
            "role": "protagonist",
            "is_speaker": true,
            "first_mention_scene": 1,
            "mention_count_in_scene": 3
          },
          {
            "name": "The Führer",
            "role": "antagonist",
            "is_speaker": false,
            "mention_count_in_scene": 1
          }
        ],
        "locations": [
          {
            "name": "Berlin Bunker",
            "type": "interior|exterior|abstract",
            "era": "1945",
            "is_primary_setting": true
          }
        ],
        "props": [
          {
            "name": "radio receiver",
            "significance": "critical|supporting|background",
            "is_action_object": true
          }
        ],
        "time_references": [
          {
            "reference": "1945",
            "type": "year",
            "specificity": "exact"
          }
        ]
      },
      
      "narrative": {
        "beat": "exposition|rising_action|climax|resolution|transition",
        "beat_description": "Exposition of the final moments",
        "emotional_tone": "somber|tense|triumphant|mysterious|comedic|peaceful",
        "pov": "omniscient|first_person|third_person",
        "major_themes": ["defeat", "duty", "resignation"],
        "foreshadowing": ["The radio will deliver orders"],
        "callback_to_scene": null
      },
      
      "dialogue_info": {
        "primary_speaker": "General Keitel",
        "speakers": ["General Keitel"],
        "has_dialogue": true,
        "dialogue_count": 2,
        "speaker_changes": 0
      },
      
      "transitions": {
        "from_previous": "none|cut|fade|dissolve|voiceover",
        "to_next": "cut|fade|dissolve|voiceover",
        "continuity_notes": "Continuous timeline, no time jump"
      },
      
      "visual_hints": {
        "lighting": "dim|bright|mixed",
        "color_palette": "monochrome|warm|cool|desaturated",
        "era_aesthetic": "1940s_german_military",
        "suggested_composition": "close-up on face, shadows from overhead light"
      },
      
      "validation": {
        "is_valid": true,
        "warnings": [],
        "errors": [],
        "checked_at": "2026-03-26T14:37:00Z"
      }
    },
    // ... more scenes
  ],
  
  "continuity_extract": {
    "characters": [
      {
        "name": "General Keitel",
        "aliases": ["Keitel", "Wilhelm Keitel"],
        "first_scene": 1,
        "last_scene": 5,
        "all_scenes": [1, 2, 3, 4, 5],
        "total_mentions": 12,
        "role": "protagonist",
        "is_narrator": false,
        "description": "German military officer facing defeat",
        "key_attributes": ["authoritative", "conflicted", "aging"]
      }
    ],
    "locations": [
      {
        "name": "Berlin Bunker",
        "aliases": ["The Bunker", "Underground Headquarters"],
        "first_scene": 1,
        "scenes": [1, 2, 3, 4, 5],
        "total_mentions": 9,
        "type": "military_installation",
        "era": "1945",
        "historical_context": "Final HQ of Nazi regime"
      }
    ],
    "props": [
      {
        "name": "Radio Receiver",
        "aliases": ["radio", "receiver"],
        "first_scene": 1,
        "scenes": [1, 2],
        "significance": "critical",
        "plot_purpose": "delivers final orders"
      }
    ],
    "timeline": {
      "era": "1940s",
      "specific_period": "WWII",
      "primary_year": 1945,
      "date_precision": "year|month|day"
    }
  },
  
  "quality_metrics": {
    "scene_count_balance": 8,
    "average_scene_length": 300,
    "scene_length_stddev": 45,
    "total_word_count": 2400,
    "narrative_arc_shape": "well_formed|rushed_ending|slow_start",
    "emotional_variety_score": 0.82,
    "continuity_check_score": 0.95,
    "readiness_for_audio_score": 0.98,
    "readiness_for_visual_score": 0.85,
    "overall_quality_score": 0.90
  },
  
  "issues_and_recommendations": [
    {
      "severity": "warning|error|info",
      "type": "pacing|continuity|clarity|ambiguity",
      "scene_nums": [3, 4],
      "message": "Scenes 3-4 lack clear location anchor. B3 may struggle with visual composition.",
      "suggested_fix": "Add explicit location description to scene 3",
      "actionable": true
    }
  ],
  
  "handoff_checklist": {
    "b2_audio_ready": true,
    "b3_visual_planning_ready": true,
    "b4_asset_research_ready": true,
    "approved_by_qa": true,
    "signed_off_by": "scene_bible_builder",
    "signed_off_at": "2026-03-26T14:37:00Z"
  }
}
```

**Size:** ~20-30 KB per video (8 scenes)  
**Update frequency:** Once per script, immutable after lock  
**Access pattern:** Read-heavy (all downstream branches)

---

### Artifact 2: `continuity_extract.json`

**Purpose:** Lightweight entity registry for B3 (Visual Planning) and B4 (Asset Research)  
**Owner:** B1 creates; B3/B4 consume  
**Why separate?** scene_bible.json is complete; continuity_extract.json is the lookup table

**Schema:**

```json
{
  "video_id": "550e8400-e29b-41d4-a716-446655440000",
  "account": "003_wwii",
  
  "characters": [
    {
      "id": "char_001",
      "canonical_name": "General Keitel",
      "aliases": ["Keitel", "General", "Wilhelm Keitel"],
      "role": "protagonist|antagonist|supporting|mention_only",
      "first_scene": 1,
      "scenes": [1, 2, 3, 4, 5],
      "description": "German military officer, authoritative but conflicted",
      "visual_notes": "older male, military uniform",
      "historical_entity": {
        "is_real_person": true,
        "birth_year": 1888,
        "death_year": 1946,
        "wikipedia": "Wilhelm_Keitel"
      },
      "needs_portrait_generation": true,
      "needs_asset_search": true
    }
  ],
  
  "locations": [
    {
      "id": "loc_001",
      "canonical_name": "Berlin Bunker",
      "aliases": ["The Bunker", "Führerbunker"],
      "type": "military_installation",
      "first_scene": 1,
      "scenes": [1, 2, 3, 4, 5],
      "era": "1945",
      "historical_entity": {
        "is_real_place": true,
        "wikidata": "Q123456"
      },
      "visual_needs": ["interior shots", "period-accurate decor"],
      "needs_asset_search": true
    }
  ],
  
  "props": [
    {
      "id": "prop_001",
      "name": "Radio Receiver",
      "aliases": ["radio", "receiver"],
      "first_scene": 1,
      "scenes": [1, 2],
      "significance": "critical|supporting|background",
      "plot_purpose": "delivers final military orders",
      "visual_notes": "1940s military radio, period accurate",
      "needs_asset_search": true
    }
  ],
  
  "timeline": {
    "era": "WWII (1939-1945)",
    "primary_date": "1945-05-08",
    "period_aesthetic": "1940s_military_germany",
    "historical_context": "Final days of Nazi regime"
  },
  
  "lookup_tables": {
    "character_by_scene": {
      "1": ["General Keitel", "The Führer"],
      "2": ["General Keitel"]
    },
    "location_by_scene": {
      "1": ["Berlin Bunker"],
      "2": ["Berlin Bunker", "Command Room"]
    }
  }
}
```

**Size:** ~5-10 KB per video  
**Update frequency:** Immutable (references scene_bible.json)  
**Access:** B3 queries "all characters in scene 3", B4 queries "all locations"

---

### Artifact 3: `script_validation_report.json`

**Purpose:** Quality gate before screenplay division  
**Owner:** script-validator agent (B1)  
**Used by:** B1 branch manager (can halt if critical issues)

**Schema:**

```json
{
  "video_id": "550e8400-e29b-41d4-a716-446655440000",
  "account": "003_wwii",
  "language": "en",
  "validated_at": "2026-03-26T14:36:00Z",
  
  "overall_status": "passed|warnings|failed",
  "readiness_score": 0.95,
  
  "checks": [
    {
      "name": "character_encoding",
      "passed": true,
      "issues": []
    },
    {
      "name": "language_detection",
      "passed": true,
      "detected_language": "en",
      "confidence": 0.99
    },
    {
      "name": "placeholder_detection",
      "passed": true,
      "placeholders_found": 0,
      "examples": []
    },
    {
      "name": "word_count_sanity",
      "passed": true,
      "total_words": 2400,
      "is_within_bounds": true,
      "bounds": {"min": 500, "max": 5000}
    },
    {
      "name": "special_character_check",
      "passed": false,
      "issues": [
        {
          "char": "–",
          "count": 3,
          "type": "en_dash",
          "severity": "warning",
          "recommendation": "Convert to regular hyphen for TTS consistency"
        }
      ]
    },
    {
      "name": "narrative_structure",
      "passed": true,
      "detected_acts": 3,
      "structure_quality": "well_formed"
    }
  ],
  
  "critical_issues": [],
  "warnings": [
    "3 en-dashes found; recommend converting to hyphens for TTS"
  ],
  "recommendations": [
    "No major issues detected. Script is ready for screenplay division."
  ]
}
```

---

## Artifact Versioning & Evolution

Each artifact should include a version field:
```json
{
  "$schema": "https://content-factory.local/schema/scene-bible/v1.0.json",
  "schema_version": "1.0",
  "compatible_branches": ["2", "3", "4", "5", "6", "7", "8", "9"]
}
```

### Backward Compatibility Rules
- If schema changes, bump version (1.0 → 1.1 → 2.0)
- Minor additions (new optional field) = patch version
- Required field changes = major version
- Downstream branches declare minimum schema version they support

---

## Artifact Storage & Access

### Where Artifacts Live
```
auto_content_factory/shared/scene_bible/
├── {video_id}/
│   ├── scene_bible.json          (main artifact)
│   ├── continuity_extract.json   (lookup table)
│   ├── validation_report.json    (quality gate)
│   ├── history/                  (versioning)
│   │   ├── scene_bible_v1.json
│   │   ├── scene_bible_v2.json
│   │   └── ...
│   └── metadata.json             (status, ownership, timestamps)
```

### Access Pattern (OpenClaw)
- **B1 writes:** `shared/scene_bible/{video_id}/scene_bible.json`
- **B2-B9 read:** Query `shared/scene_bible/{video_id}/` with video_id
- **Monitoring (B10):** Read metadata.json for artifact status across all videos
- **B1 agent:** Validates before write; enforces schema

---

## Schema Validation Strategy

### At Write Time (B1)
- Pydantic models or JSON Schema with strict validation
- Reject incomplete/malformed artifacts
- Log validation errors to Telegram + OpenClaw heartbeat

### At Read Time (B2-B9)
- Lightweight schema version check
- Fallback to known compatible version if minor mismatch
- Error if major version mismatch (requires B1 regeneration)

### Tooling
- **Pydantic:** Python validation (if B1 agents are Python)
- **JSON Schema:** Language-agnostic, enforces at API boundary
- **OpenAPI:** If exposing artifact queries via REST

---

## Critical Contracts for Downstream

**B2 (Audio) Expects:**
- scene_bible.json with complete, validated scene text
- No empty scene.text fields
- All word_count fields populated

**B3 (Visual Planning) Expects:**
- continuity_extract.json with full character/location/prop lists
- scene_bible.json with narrative beats and visual_hints
- Valid character names and location names

**B4 (Asset Research) Expects:**
- continuity_extract.json with is_real_person / is_real_place flags
- Historical metadata (Wikipedia, Wikidata links)
- search_terms already populated for quick asset lookup

**B6 (Scene Composition) Expects:**
- scene_bible.json with transitions.from_previous and transitions.to_next
- Continuity notes for smooth cuts/fades
- Timing data (estimated_duration_sec) for sync with audio

---

## Governance Notes

1. **B1 is the schema owner** — any changes to scene_bible.json schema require B1 agent approval
2. **Backward compatibility first** — try to never break downstream
3. **Monitoring watches schemas** — B10 (Monitoring) tracks schema versions in use across all videos
4. **Clear error messages** — when downstream agents find malformed artifacts, error should point to B1 for remediation
