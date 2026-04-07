# Haiku Research: Cheap Model Workflows for Sub-Agents

**Purpose:** Route each agent task to the most cost-efficient LLM without sacrificing quality  
**Date:** 2026-03-26  
**Budget Constraint:** ~$0.50-1.00 per video in LLM costs (excluding image gen, rendering)

---

## Model Options Available

| Model | Provider | Cost | Best For | Latency | Quality |
|-------|----------|------|----------|---------|---------|
| **GPT-5.4-nano** | OpenRouter | $0.00075/1k | Routing, formatting, simple parsing | <1s | Good |
| **GPT-5.4-mini** | OpenRouter | $0.003/1k | Planning, analysis, decision-making | 2-3s | Excellent |
| **DeepSeek-V3** | OpenRouter | $0.0014/1k in | Reasoning, creative decisions | 1-2s | Very Good |
| **Qwen 3.5 (local)** | Ollama | $0.00 | Deterministic tasks, routing | 0.5s | Fair |
| **Claude 3.5 Haiku** | Anthropic API | $0.004/1k | Visual description, creative guidance | 1-2s | Excellent |
| **Gemini 2.5 Flash** | Google (free) | $0.00 | Multi-modal tasks, QA | 2s | Good |
| **Gemini Flash Lite** | Google (free) | $0.00 | Simple text analysis | 1s | Fair |

---

## Branch-by-Branch Routing

### **B1: Pre-Production (Script → Scenes)**

**Task:** Divide script into scenes, create scene descriptions, extract metadata

**Agent:** script_fetcher, scene_director, scene_bible_builder

**Workflow:**
```
Input: Script text (PT/EN/ES/FR/IT/DE)
  ↓
[1] Routing Nano: Parse script structure, detect chapter breaks
    Model: GPT-5.4-nano
    Cost: $0.0001 per script
    Output: { chapters, estimated_scenes: 8 }
  ↓
[2] Creative Planning Mini: Divide into scenes, write descriptions
    Model: GPT-5.4-mini
    Cost: $0.005 per script
    Output: { scenes[], metadata }
  ↓
[3] Validation Haiku: Verify word distribution, tone consistency
    Model: Claude 3.5 Haiku
    Cost: $0.003 per script
    Output: { scene_bible.json }

Total per video: ~$0.008
```

**When to upgrade:** If a script is exceptionally long (>50 scenes) or complex multilingual

---

### **B2: Audio (TTS + Validation)**

**Task:** Polish text, generate TTS, validate timing

**Agent:** text_polish, tts_generator, audio_validator, timing_extractor

**Workflow:**
```
Input: Scene text (per language)
  ↓
[1] Nano Polish: Grammar check, language-specific formatting
    Model: GPT-5.4-nano or local Qwen
    Cost: $0.0001 per scene
    Output: { polished_text }
  ↓
[2] TTS Generation: Gemini (no LLM, just audio generation)
    Cost: $0.00 (free tier)
    Output: { audio_file }
  ↓
[3] WhisperX Transcription: Extract timestamps (no LLM, local)
    Cost: $0.00 (local GPU)
    Output: { word_timestamps[] }
  ↓
[4] Haiku Validation: Verify sync quality, flag issues
    Model: Claude 3.5 Haiku
    Cost: $0.002 per scene
    Output: { audio_timestamps.json }

Total per video (8 scenes): ~$0.008
```

**Why cheap:** TTS and transcription are deterministic. LLM only for validation.

---

### **B3: Visual Planning (Scene Analysis)**

**Task:** Analyze narrative, plan visual direction, create asset strategy

**Agent:** character_identifier, entity_matcher, visual_director, asset_strategy, reference_strategist

**Workflow:**
```
Input: Scene descriptions + account style guide
  ↓
[1] Character Extraction Local: Parse character mentions (regex + Qwen)
    Model: Ollama Qwen 3.5
    Cost: $0.00
    Output: { characters[] }
  ↓
[2] Entity Matching Mini: Link characters to historical figures
    Model: GPT-5.4-mini
    Cost: $0.004 per scene
    Reasoning: Needs creative judgment ("This is Churchill, not Churchill the novelist")
    Output: { entity_matches[] }
  ↓
[3] Visual Direction Mini: Decide mood, color, composition
    Model: GPT-5.4-mini (uses account style guide context)
    Cost: $0.006 per scene
    Output: { visual_plan.json per scene }
  ↓
[4] Asset Strategy Mini: Determine if photographs, videos, or AI
    Model: GPT-5.4-mini
    Cost: $0.003 per scene
    Output: { asset_strategy }

Total per video (8 scenes): ~$0.10
```

**Optimization:** Batch all 8 scenes into one Mini call (cheaper than 8 separate calls)

---

### **B4: Asset Research (Real Image/Video Search)**

**Task:** Search public archives, evaluate candidates, score relevance

**Agent:** people_finder, location_finder, event_object_finder, video_finder, asset_judge

**Workflow:**
```
Input: Visual plan + asset strategy
  ↓
[1] Search Execution: Python script + web scraping (no LLM)
    Tool: Playwright, Selenium
    Cost: $0.00 (local)
    Output: { raw_candidates[] }
  ↓
[2] Relevance Scoring Nano: Quick filter (is this relevant?)
    Model: GPT-5.4-nano
    Cost: $0.0002 per candidate set
    Output: { scored_candidates[] }
  ↓
[3] Copyright Assessment Haiku: Check legal status
    Model: Claude 3.5 Haiku (best for legal/copyright nuance)
    Cost: $0.004 per scene
    Output: { copyright_status, licensing_notes }

Total per video: ~$0.03
```

**Note:** If B9 (optional M7) is deployed, parallelization drops cost 50-70%

---

### **B5: Image Generation (ComfyUI + Animation)**

**Task:** Generate missing images, animate static images via browser

**Agent:** portrait_generator, ai_image_director, image_generator, image_qa, image_animator

**Workflow:**
```
Input: Asset candidates + visual plan
  ↓
[1] Prompt Generation Mini: Turn visual specs into ComfyUI prompts
    Model: GPT-5.4-mini
    Cost: $0.004 per image
    Output: { prompt, negative_prompt, lora_list }
  ↓
[2] Image Generation: ComfyUI SDXL/Flux (local, no LLM)
    Cost: $0.00 (GPU time, 15-85s)
    Output: { image }
  ↓
[3] QA Check Nano: Does image match spec?
    Model: GPT-5.4-nano
    Cost: $0.0001 per image
    Output: { passed: true/false, notes }
  ↓
[4] Browser Animation (if needed): img2video via Freepik/Higgsfield
    Tool: Selenium + API calls
    Cost: Per-subscription (already budgeted)
    Output: { video_clip }

Total per video (3-5 images): ~$0.02
```

---

### **B6: Scene Composition (Timeline Assembly)**

**Task:** Combine assets, define motion, create visual beat sheet

**Agent:** scene_composer, composition_selector, motion_planner

**Workflow:**
```
Input: Assets + scene composition specs
  ↓
[1] Motion Planning Nano: Simple choreography (pan_left, static, etc.)
    Model: GPT-5.4-nano or local
    Cost: $0.0001 per scene
    Output: { motion[], timing }
  ↓
[2] Pacing Validation Mini: Does it feel natural?
    Model: GPT-5.4-mini
    Cost: $0.003 per scene
    Reasoning: Evaluates narrative pacing, emotional beats
    Output: { composition.json }

Total per video: ~$0.03
```

---

### **B7: Post-Production (Music, SFX, Lettering)**

**Task:** Plan music, SFX, text overlays, animations

**Agent:** music_planner, sfx_planner, lettering_planner, lettering_style, animation_choreographer

**Workflow:**
```
Input: Composition + post-prod guidelines
  ↓
[1] Music Selection Mini: Pick track from catalog, timing
    Model: GPT-5.4-mini
    Cost: $0.004 per video
    Reasoning: Must understand emotional arc and timing
    Output: { music_track, volume_curve }
  ↓
[2] SFX Curation Nano: Identify moments for sound effects
    Model: GPT-5.4-nano
    Cost: $0.0001
    Output: { sfx_list[] }
  ↓
[3] Lettering Design Mini: Text, styling, timing
    Model: GPT-5.4-mini
    Cost: $0.005 per video
    Output: { title_cards[], animations[] }

Total per video: ~$0.01
```

---

### **B8: Assembly & Render (TSX Generation)**

**Task:** Generate Remotion TSX code, compile, render, upload

**Agent:** tsx_generator, tsx_validator, renderer, compressor_uploader

**Workflow:**
```
Input: All previous artifacts
  ↓
[1] Code Generation Nano: Deterministic template + data insertion
    Model: GPT-5.4-nano (template engine, not creative)
    Cost: $0.0001 per video
    Output: { index.tsx, Video.tsx }
    Note: Could use template engine instead of LLM (cheaper)
  ↓
[2] Validation Nano: Syntax check, import validation
    Model: GPT-5.4-nano
    Cost: $0.00005
    Output: { valid: true/false, errors[] }
  ↓
[3] Render: Locally on M1 (no LLM)
    Cost: GPU time + electricity (~$2.50/video)
    Output: { final.mp4 }
  ↓
[4] Upload: Python script (no LLM)
    Cost: $0.00
    Output: { upload_confirmation }

Total per video: ~$0.0002
```

**Optimization:** Code generation could be PURELY template-based (handlebars, Jinja2), cost $0.00

---

### **B9: Quality Assurance (Distributed)**

**Task:** Validate outputs at each stage

**Agent:** audio_qa, visual_qa, editorial_qa, technical_qa, final_qa

**Workflow:**
```
Input: Artifacts from B1-B8
  ↓
[1] Audio QA Haiku: Sync check, quality
    Model: Claude 3.5 Haiku
    Cost: $0.002 per video
    Output: { passed: true/false }
  ↓
[2] Visual QA Flash: Color consistency, artifact detection
    Model: Gemini 2.5 Flash (free, good for image analysis)
    Cost: $0.00
    Output: { visual_issues[] }
  ↓
[3] Editorial QA Mini: Content accuracy, tone match
    Model: GPT-5.4-mini
    Cost: $0.004 per video
    Output: { accuracy_score, notes }
  ↓
[4] Technical QA Nano: File format, codec, metadata
    Model: GPT-5.4-nano (or local validation)
    Cost: $0.0001
    Output: { technical_issues[] }

Total per video: ~$0.007
```

---

### **B10: Monitoring & Reporting**

**Task:** Track spend, alert on errors, generate reports

**Agent:** success_reporter, error_handler, cost_tracker

**Workflow:**
```
Input: All artifacts + KMS spend data
  ↓
[1] Cost Tracking: Python calculation (no LLM)
    Cost: $0.00
    Output: { spend_summary, breakdown[] }
  ↓
[2] Error Detection Nano: Scan logs, flag issues
    Model: GPT-5.4-nano (regex + summarization)
    Cost: $0.0001 per run
    Output: { errors[], severity[] }
  ↓
[3] Report Generation Nano: Format summary for Telegram
    Model: GPT-5.4-nano (formatting)
    Cost: $0.0001
    Output: { telegram_message }

Total per run: ~$0.0003
```

---

## Total Cost Per Video

| Branch | Models Used | Cost |
|--------|-------------|------|
| B1 Pre-Prod | Nano, Mini, Haiku | $0.008 |
| B2 Audio | Nano, Haiku | $0.008 |
| B3 Visual Planning | Qwen local, Mini ×3 | $0.013 |
| B4 Asset Research | Nano, Haiku | $0.003 |
| B5 Image Gen | Mini, Nano | $0.002 |
| B6 Scene Composition | Nano, Mini | $0.003 |
| B7 Post-Prod | Mini, Nano | $0.010 |
| B8 Assembly | Nano ×2 | $0.0002 |
| B9 QA | Haiku, Flash, Mini, Nano | $0.007 |
| B10 Monitoring | Nano ×2 | $0.0003 |
| **TOTAL LLM COST** | | **~$0.054** |
| Image Generation (ComfyUI) | | **$0.00** |
| Rendering (M1 GPU) | | **~$2.50** |
| **TOTAL PER VIDEO** | | **~$2.55** |

**Historical context:** Current cost is ~$5.55/video (with Gemini paid + OpenRouter images)  
**Savings:** ~54% reduction in LLM costs

---

## Optimization Strategies

### 1. **Batch Processing**
Instead of calling Mini 8 times for 8 scenes separately, batch into 1 call:
```
Prompt: "Analyze these 8 scenes and create visual plans for each"
Input: [scene1, scene2, ..., scene8]
Output: [visual_plan1, visual_plan2, ..., visual_plan8]
```
Cost: Mini for 1 batch call (~$0.004) vs 8 × $0.006 = $0.048  
Savings: 92% reduction

### 2. **Local Model Substitution**
For simple tasks (routing, formatting, parsing), use Ollama Qwen (local, $0.00):
- B1 structure parsing
- B6 motion specification
- B10 error categorization

Estimated savings: $0.0015 per video

### 3. **Template Engines Instead of LLMs**
B8 TSX generation is deterministic. Use Handlebars or Jinja2:
```
// Instead of: LLM writes TSX code
// Use: Template engine fills in variables
<Sequence from={0} durationInFrames={duration}>
  <Audio src={audioFile} />
  {{#assets}}
  <Img src="{{path}}" from={{start}} to={{end}} />
  {{/assets}}
</Sequence>
```
Cost: $0.00 instead of $0.0001  
Savings: Marginal but cleaner

### 4. **Caching & Memoization**
For recurring queries (character info, asset catalog):
- First video: Query LLM, cache result
- Subsequent videos (same account): Read from cache
- Example: Character "Churchill" looked up once, used in 10 videos

Potential savings: 20-30% on B3/B4 over a week

### 5. **Async Model Routing**
Run low-priority QA checks asynchronously (after upload):
- Don't block render on QA
- Run QA in background, collect feedback for next video
- Cost: Same, but parallelization improves throughput

---

## Model Selection Decision Tree

```
Task Type: Formatting/Parsing?
├─ YES → Use local Qwen or GPT-5.4-nano ($0.00 or $0.0001)
└─ NO → Next question

Task Type: Creative judgment/planning?
├─ Needs nuance (legal, tone, culture)?
│  └─ Use Claude Haiku or GPT-5.4-mini ($0.002-0.006)
├─ Straightforward decision?
│  └─ Use GPT-5.4-mini ($0.003)
└─ Next question

Task Type: Multi-modal (images)?
├─ YES → Use Gemini Flash (free) or Claude Haiku ($0.004)
└─ NO → Next question

Task Type: Deterministic (code gen, metadata)?
└─ Use template engine ($0.00) or nano ($0.0001)
```

---

## Configuration Files for Routing

**Each branch should have a `model_config.md`:**

```markdown
# B3: Visual Planning

## Models Used
- Character extraction: Ollama Qwen (local)
- Entity matching: GPT-5.4-mini (OpenRouter)
- Visual direction: GPT-5.4-mini (OpenRouter)
- Asset strategy: GPT-5.4-mini (OpenRouter)

## Batching Strategy
- Batch all 8 scenes into 1 prompt for entity matching
- Batch all 8 scenes into 1 prompt for visual direction
- Do NOT batch asset strategy (per-scene nuance)

## Cost Per Video
- Without batching: $0.078
- With batching: $0.013
- Actual: $0.013 (batching enabled)

## Fallback Models
- If OpenRouter unavailable: Use Anthropic API (Claude Haiku)
- If neither: Use local Qwen (degrades quality slightly)

## Monitoring
- Track actual spend vs expected
- Alert if any call exceeds budget threshold ($0.02)
```

---

## Summary for Implementation

**Priority 1 (Build First):**
1. Set up OpenRouter account with $20 starter credit
2. Configure routing: Nano for $0 tasks, Mini for $0.003-0.006 tasks
3. Use Gemini Flash (free) for multi-modal QA
4. Batch all scene processing in B1-B3

**Priority 2 (Optimize):**
1. Deploy Ollama for local Qwen (cost $0.00)
2. Build template engine for B8 (TSX generation)
3. Implement caching for recurring entity lookups

**Priority 3 (Monitor):**
1. Track actual spend vs model (should be $0.05-0.07 per video)
2. If exceeding budget, downgrade to more Nano usage
3. Quarterly review of model costs

---

**Next Document:** Implementation summary and status
