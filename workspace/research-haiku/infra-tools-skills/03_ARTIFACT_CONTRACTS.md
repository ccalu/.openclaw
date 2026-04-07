# Haiku Research: Artifact Contracts & Data Flow

**Purpose:** Define JSON/markdown contracts between branches for safe, predictable data flow  
**Date:** 2026-03-26  
**Audience:** Lucca, Tobias, Claude Code (implementation)

---

## 1. SCENE BIBLE (B1 Output → B2-B10 Input)

**Created by:** B1 (Pre-Production)  
**Consumed by:** B2 (Audio), B3 (Visual Planning), B6 (Scene Composition)  
**Lifecycle:** One per video, immutable after B1 completes  
**Storage:** `~/.openclaw/workspace/production/run_<video_id>/scene_bible.json`

### Schema

```json
{
  "metadata": {
    "video_id": "video_12345",
    "account_id": "003",
    "account_name": "wwii",
    "script_source": "google_sheet_row_42",
    "language": "pt-BR",
    "created_by": "B1_scene_director",
    "created_at": "2026-03-26T10:00:00Z",
    "version": "1.0",
    "status": "finalized"
  },
  
  "script": {
    "original_text": "Em 1941, o mundo mudou para sempre...",
    "character_count": 5432,
    "word_count": 987
  },

  "scenes": [
    {
      "scene_id": 1,
      "scene_title": "Opening - Timeline",
      "text": "Em 1941, o mundo mudou para sempre. A Segunda Guerra Mundial entrou numa fase crítica.",
      "word_count": 22,
      "estimated_duration_sec": 8,
      "narrative_arc": "exposition",
      "tone": "serious, ominous",
      "key_concepts": ["1941", "World War II", "turning point"],
      "characters": ["Narrator (implied)"],
      "suggested_visuals": "timeline, maps, newspaper headlines",
      "content_warnings": []
    },
    {
      "scene_id": 2,
      "scene_title": "Battle Context",
      "text": "A Batalha do Atlântico era crucial. Navios aliados...",
      "word_count": 19,
      "estimated_duration_sec": 7,
      "narrative_arc": "rising_action",
      "tone": "dramatic, tense",
      "key_concepts": ["Battle of the Atlantic", "supply lines", "naval warfare"],
      "characters": ["Winston Churchill (mentioned)"],
      "suggested_visuals": "ship battles, naval maps, convoy scenes",
      "content_warnings": ["violence", "maritime casualties"]
    }
  ],

  "quality_metrics": {
    "readability_score": 8.2,
    "engagement_score": 7.9,
    "pacing_assessment": "even distribution across scenes"
  }
}
```

**Contract Rules:**
- Field `status` must be `"finalized"` before B2 reads
- Each scene must have `word_count`, `estimated_duration_sec`, `characters`
- `characters` list is for reference only (B3 will validate/expand them)
- Once created, scene_bible.json is READ-ONLY (no downstream modifications)
- If B2 needs changes, flag for B1 re-run (v2.0)

---

## 2. AUDIO TIMESTAMPS (B2 Output → B3-B6-B7 Input)

**Created by:** B2 (Audio) Phase 3 (WhisperX processing)  
**Consumed by:** B3 (Visual Planning), B6 (Scene Composition), B7 (Post-Prod)  
**Storage:** `~/.openclaw/workspace/production/run_<video_id>/audio_timestamps.json`

### Schema

```json
{
  "metadata": {
    "video_id": "video_12345",
    "language": "pt-BR",
    "tts_model": "google_tts",
    "whisper_model": "large-v3",
    "processed_at": "2026-03-26T10:15:00Z",
    "total_duration_sec": 47.2,
    "quality_score": 0.94
  },

  "scenes": [
    {
      "scene_id": 1,
      "audio_file": "clips/scene_01.mp3",
      "duration_sec": 8.1,
      "words": [
        {
          "word": "Em",
          "start_sec": 0.0,
          "end_sec": 0.2,
          "confidence": 0.99
        },
        {
          "word": "1941,",
          "start_sec": 0.2,
          "end_sec": 0.6,
          "confidence": 0.98
        },
        {
          "word": "o",
          "start_sec": 0.7,
          "end_sec": 0.8,
          "confidence": 0.97
        }
      ]
    }
  ],

  "validation": {
    "total_words": 987,
    "sync_quality": "good",
    "issues": []
  }
}
```

**Contract Rules:**
- Must include `start_sec` and `end_sec` for every word (frame-perfect sync)
- Confidence scores must be ≥ 0.90 for all words
- If any word fails validation, entire scene must be re-processed
- This is the "single source of truth" for timing (all other operations read from here)
- Lock: B2 owns this file exclusively, other agents read-only

---

## 3. VISUAL PLAN (B3 Output → B4-B5-B6 Input)

**Created by:** B3 (Visual Planning)  
**Consumed by:** B4 (Asset Research), B5 (Image Generation), B6 (Scene Composition)  
**Storage:** `~/.openclaw/workspace/production/run_<video_id>/visual_plan.json`

### Schema

```json
{
  "metadata": {
    "video_id": "video_12345",
    "account_id": "003",
    "account_style": "wwii_bw_documentary",
    "planned_at": "2026-03-26T10:30:00Z",
    "visual_director": "B3_agent"
  },

  "scenes": [
    {
      "scene_id": 1,
      "visual_theme": "opening_timeline",
      "mood": "serious, ominous",
      "color_palette": ["#1a1a1a", "#4a4a4a", "#8b8b8b", "#c0c0c0"],
      "era": "1940s",
      "visual_style": "black_and_white_documentary",
      "composition": "wide_establishing_shot",
      
      "asset_strategy": {
        "primary_asset_type": "photographs",
        "sources": ["library_of_congress", "wikipedia_wwii"],
        "backup_asset_type": "ai_generated",
        "num_images_needed": 3,
        "image_duration_sec": 2.5,
        "motion_treatment": "subtle_pan_or_static"
      },

      "characters_in_scene": [],
      "suggested_subjects": ["timeline display", "war maps", "period newspapers"],
      
      "qa_checklist": [
        "images are historically accurate for 1941",
        "color palette matches wwii_bw_documentary",
        "no anachronistic elements"
      ]
    },
    {
      "scene_id": 2,
      "visual_theme": "naval_battle",
      "mood": "dramatic, tense",
      "color_palette": ["#000033", "#003366", "#336699", "#669999"],
      "era": "1940s",
      "visual_style": "black_and_white_documentary_with_color_grading",
      "composition": "dynamic_wide_angle",
      
      "asset_strategy": {
        "primary_asset_type": "videos",
        "sources": ["british_pathé", "library_of_congress"],
        "backup_asset_type": "photographs",
        "num_assets_needed": 2,
        "asset_duration_sec": 3.5,
        "motion_treatment": "dynamic_cuts"
      },

      "characters_in_scene": ["Churchill (mentioned, no image needed)"],
      "suggested_subjects": ["naval convoy", "submarine", "ship warfare"],
      
      "qa_checklist": [
        "footage is real naval combat (not fictional)",
        "matches dramatic tone",
        "no color (historical accuracy)"
      ]
    }
  ],

  "overall_notes": "Stick to documentary style per account rules. No modern artifacts. Max 3 cuts per scene to avoid visual fatigue."
}
```

**Contract Rules:**
- `asset_strategy` drives both B4 (asset research) and B5 (image generation)
- If `primary_asset_type` is "photographs", B4 searches first; if not found, B5 generates
- If `primary_asset_type` is "videos", B4 searches for video; if not found, B4 can substitute with photographs or B5 generates stills
- `num_images_needed` sets expectation for B4/B5
- `qa_checklist` is passed to B9 (QA) for validation
- Once locked, immutable (no downstream changes)

---

## 4. ASSET CANDIDATES (B4 Output → B5/B6 Input)

**Created by:** B4 (Asset Research)  
**Consumed by:** B5 (Image Generation), B6 (Scene Composition)  
**Storage:** `~/.openclaw/workspace/production/run_<video_id>/asset_candidates.json`

### Schema

```json
{
  "metadata": {
    "video_id": "video_12345",
    "account_id": "003",
    "search_completed_at": "2026-03-26T10:45:00Z",
    "searcher_agent": "B4_asset_research"
  },

  "scenes": [
    {
      "scene_id": 1,
      "candidates": [
        {
          "candidate_id": "loc_012345",
          "source": "library_of_congress",
          "source_url": "https://loc.gov/pictures/item/12345",
          "asset_type": "photograph",
          "title": "Newspaper headline, 1941",
          "creator": "Unknown",
          "date": "1941",
          "format": "jpeg",
          "dimensions": "3000x2000",
          "copyright_status": "public_domain",
          "relevance_score": 0.95,
          "quality_score": 0.88,
          "annotation": "Excellent period-accurate newspaper display"
        },
        {
          "candidate_id": "wiki_67890",
          "source": "wikipedia_wwii",
          "source_url": "https://en.wikipedia.org/wiki/...",
          "asset_type": "photograph",
          "title": "1941 World Map",
          "creator": "Wikipedia Commons",
          "date": "~1941",
          "format": "png",
          "dimensions": "2400x1600",
          "copyright_status": "cc_by_sa",
          "relevance_score": 0.87,
          "quality_score": 0.82,
          "annotation": "Good for timeline establishment"
        }
      ],
      "search_summary": "Found 2 strong candidates for opening scene. Both public domain or CC-licensed."
    },
    {
      "scene_id": 2,
      "candidates": [
        {
          "candidate_id": "bpath_001",
          "source": "british_pathé",
          "source_url": "https://www.britishpathe.com/video/...",
          "asset_type": "video",
          "title": "Naval Battles of 1941",
          "duration_sec": 42,
          "creator": "British Pathé",
          "date": "1941-1942",
          "format": "mp4",
          "copyright_status": "rights_pending",
          "relevance_score": 0.92,
          "quality_score": 0.90,
          "annotation": "Authentic naval footage. Must clear rights with Pathé.",
          "licensing_note": "Contact pathé@..., expected $50-200 per-use license"
        },
        {
          "candidate_id": "usarmy_045",
          "source": "library_of_congress",
          "source_url": "https://loc.gov/collections/...",
          "asset_type": "video",
          "title": "U.S. Navy Training Film - Convoy Operations",
          "duration_sec": 18,
          "creator": "U.S. Army Signal Corps",
          "date": "1942",
          "format": "mp4",
          "copyright_status": "public_domain",
          "relevance_score": 0.85,
          "quality_score": 0.78,
          "annotation": "Public domain, lower image quality but usable."
        }
      ],
      "search_summary": "Found 2 video candidates. Strong option (Pathé) requires licensing. Public-domain backup available."
    }
  ],

  "overall_search_stats": {
    "total_searches": 12,
    "total_candidates_found": 4,
    "candidates_require_licensing": 1,
    "public_domain_candidates": 3,
    "api_calls_used": 18,
    "search_cost": "$2.15"
  }
}
```

**Contract Rules:**
- `relevance_score` (0-1) is subjective (B4's judgment)
- `quality_score` (0-1) is objective (resolution, clarity, format)
- `copyright_status` must be one of: `public_domain`, `cc_by_sa`, `cc_by`, `rights_pending`, `unknown`
- If `rights_pending`, include `licensing_note` with contact info and estimated cost
- B5 uses this to decide: "use real asset (B4 candidate)" or "generate new one"
- B6 uses this to inform scene composition timing (video duration affects pacing)

---

## 5. GENERATED ASSETS (B5 Output → B6-B7-B8 Input)

**Created by:** B5 (Image Generation)  
**Consumed by:** B6 (Scene Composition), B7 (Post-Prod), B8 (Assembly/Render)  
**Storage:** `~/.openclaw/workspace/production/run_<video_id>/assets/generated/`

### Schema (JSON metadata per image)

```json
{
  "metadata": {
    "asset_id": "gen_0042",
    "video_id": "video_12345",
    "scene_id": 1,
    "generated_at": "2026-03-26T11:00:00Z",
    "generator_agent": "B5_ai_image_generator"
  },

  "generation_info": {
    "service": "comfyui",
    "model": "juggernaut_xl_ragnarok",
    "loras": ["FilmGrain_Redmond_v2", "wwii_aesthetic_lora"],
    "prompt": "Black and white photograph of 1941 newspaper headline announcing world war. Grainy film texture, vintage print quality. No people. Documentary style.",
    "negative_prompt": "color, modern, digital artifacts, blurry",
    "seed": 42123456,
    "steps": 25,
    "guidance_scale": 7.5,
    "cost": "$0.00"
  },

  "output": {
    "file_path": "assets/generated/gen_0042.jpg",
    "format": "jpeg",
    "dimensions": "1920x1080",
    "file_size_mb": 1.2,
    "duration_sec": null,
    "quality_score": 0.91
  },

  "qa_status": {
    "passed_visual_qa": true,
    "passed_content_qa": true,
    "passed_legal_qa": true,
    "qa_notes": [
      "Image matches scene mood (serious, period-accurate)",
      "No copyright concerns (AI-generated)",
      "Ready for composition"
    ]
  },

  "asset_registry_entry": {
    "asset_type": "photograph_stylized",
    "era": "1940s",
    "color_treatment": "black_and_white",
    "usage_count": 1,
    "reusability": "scene_specific"
  }
}
```

**Contract Rules:**
- Every generated image must have a `quality_score` (0-1, assessed by B5)
- Must include full generation parameters (reproducibility)
- Cost is $0.00 for local (ComfyUI), or actual cost if via API
- `qa_status` is filled by B9 (QA), not by B5
- Once generated, asset is immutable (never re-generated in same run)

---

## 6. SCENE COMPOSITION PLAN (B6 Output → B7-B8 Input)

**Created by:** B6 (Scene Composition)  
**Consumed by:** B7 (Post-Prod), B8 (Assembly/Render)  
**Storage:** `~/.openclaw/workspace/production/run_<video_id>/scene_composition.json`

### Schema

```json
{
  "metadata": {
    "video_id": "video_12345",
    "composed_at": "2026-03-26T11:30:00Z",
    "composer_agent": "B6_scene_composer"
  },

  "composition_timeline": [
    {
      "scene_id": 1,
      "scene_title": "Opening - Timeline",
      "start_time_sec": 0.0,
      "end_time_sec": 8.1,
      "duration_sec": 8.1,
      
      "assets": [
        {
          "asset_id": "gen_0042",
          "asset_type": "image",
          "file_path": "assets/generated/gen_0042.jpg",
          "in_time_sec": 0.0,
          "out_time_sec": 2.7,
          "duration_on_screen_sec": 2.7,
          "motion": "pan_left_slow",
          "opacity_curve": "constant",
          "effects": []
        },
        {
          "asset_id": "wiki_67890",
          "asset_type": "image",
          "file_path": "assets/real/wiki_67890.png",
          "in_time_sec": 2.8,
          "out_time_sec": 5.3,
          "duration_on_screen_sec": 2.5,
          "motion": "static",
          "opacity_curve": "fade_in_0.3s_fade_out_0.3s",
          "effects": ["slight_grain_overlay"]
        }
      ],

      "narration": {
        "audio_file": "clips/scene_01.mp3",
        "start_sec": 0.0,
        "end_sec": 8.1,
        "volume": 1.0,
        "sync_status": "locked"
      },

      "composition_notes": "Establish opening with newspaper, transition to timeline map. Pacing feels natural with 0.1s gap between assets."
    }
  ],

  "overall_pacing": {
    "total_runtime_sec": 47.2,
    "scene_count": 8,
    "avg_scene_duration_sec": 5.9,
    "visual_transitions": "smooth_fades_and_pans",
    "cut_count": 12,
    "assessed_engagement": 7.8
  }
}
```

**Contract Rules:**
- `in_time_sec` / `out_time_sec` must align with audio timestamps (B2) exactly
- `motion` field describes camera/image behavior (pan_left, static, zoom_in, etc.)
- `effects` array is passed directly to B7 (Post-Prod) for audio/SFX addition
- Once locked by B6, immutable (B7 reads only, adds music/SFX on top)

---

## 7. POST-PRODUCTION PLAN (B7 Output → B8 Input)

**Created by:** B7 (Post-Production)  
**Consumed by:** B8 (Assembly/Render)  
**Storage:** `~/.openclaw/workspace/production/run_<video_id>/post_prod_plan.json`

### Schema

```json
{
  "metadata": {
    "video_id": "video_12345",
    "planned_at": "2026-03-26T12:00:00Z"
  },

  "music_plan": {
    "tracks": [
      {
        "track_id": "mus_001",
        "title": "Cinematic Drama",
        "artist": "Stock Library",
        "start_sec": 0.0,
        "end_sec": 47.2,
        "volume": 0.6,
        "fade_in": 0.0,
        "fade_out": 1.0
      }
    ],
    "total_cost": "$0.00"
  },

  "sfx_plan": {
    "effects": [
      {
        "sfx_id": "sfx_001",
        "name": "newspaper_rustle",
        "start_sec": 0.5,
        "duration_sec": 0.8,
        "volume": 0.4
      },
      {
        "sfx_id": "sfx_002",
        "name": "typewriter_clack",
        "start_sec": 3.0,
        "duration_sec": 1.5,
        "volume": 0.5
      }
    ],
    "total_cost": "$0.00"
  },

  "lettering_plan": {
    "title_cards": [
      {
        "card_id": "title_001",
        "text": "1941",
        "start_sec": 0.5,
        "duration_sec": 2.0,
        "style": "serif_bold_white",
        "position": "center_upper",
        "animation_in": "fade_in_0.3s",
        "animation_out": "fade_out_0.3s"
      }
    ],
    "scene_titles": []
  },

  "animation_plan": {
    "transitions": [
      {
        "from_scene": 1,
        "to_scene": 2,
        "transition_type": "cross_dissolve",
        "duration_sec": 0.5
      }
    ],
    "motion_graphics": []
  }
}
```

**Contract Rules:**
- All time references must be in seconds, aligned to audio/composition
- Cost fields show estimated expense (from music/SFX libraries)
- Lettering styles reference account style guide (wwii_bw_documentary, etc.)
- B8 reads this as "directive", generates TSX code based on these specs

---

## 8. FINAL VIDEO MANIFEST (B8 Output)

**Created by:** B8 (Assembly/Render)  
**Status tracking:** Used by B9 (QA) and B10 (Monitoring)  
**Storage:** `~/.openclaw/workspace/production/run_<video_id>/manifest.json`

```json
{
  "metadata": {
    "video_id": "video_12345",
    "account_id": "003",
    "render_started": "2026-03-26T12:30:00Z",
    "render_completed": "2026-03-26T14:00:00Z",
    "total_render_time_sec": 5400,
    "renderer_machine": "M1"
  },

  "output_files": {
    "video_file": "final.mp4",
    "video_path": "C:\\production\\video_12345\\final.mp4",
    "video_size_mb": 287,
    "video_duration_sec": 47.2,
    "video_codec": "h264",
    "video_bitrate_kbps": 4800,
    "resolution": "1920x1080",
    "frame_rate": 30
  },

  "cost_summary": {
    "total_cost": "$4.20",
    "breakdown": {
      "gemini_api": "$0.50",
      "image_generation": "$0.00",
      "openrouter": "$1.20",
      "rendering": "$2.50"
    }
  },

  "qa_signoffs": [
    {
      "qa_type": "audio_qa",
      "status": "passed",
      "notes": "Audio sync verified frame-perfect, quality excellent"
    },
    {
      "qa_type": "visual_qa",
      "status": "passed",
      "notes": "Color grading consistent, no artifacts"
    },
    {
      "qa_type": "editorial_qa",
      "status": "passed",
      "notes": "Pacing excellent, content accurate"
    }
  ],

  "ready_for_upload": true
}
```

---

## Summary: Data Flow Diagram

```
B1: Scene Bible
  └─► B2: Audio Timestamps
  └─► B3: Visual Plan
      └─► B4: Asset Candidates + B5: Generated Assets
          └─► B6: Scene Composition (combines B2 + B4 + B5)
              └─► B7: Post-Prod Plan (adds music/SFX)
                  └─► B8: Final Video Manifest + final.mp4
                      └─► B9: QA (reads all artifacts, validates)
                          └─► B10: Monitoring (tracks cost, success)
```

---

**Key Principles:**
1. **Immutability:** Once a stage completes, earlier outputs are READ-ONLY
2. **Clear contracts:** Every JSON has defined schema, validation rules
3. **Single source of truth:** Audio timestamps are the temporal baseline
4. **Lineage tracking:** Every artifact includes `created_by`, `created_at`, version
5. **Cost visibility:** Every artifact tracks cost incurred at that stage

---

**Next:** Cheap model workflows for each agent type.
