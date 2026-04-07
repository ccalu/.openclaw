# Branch 5 (Image Generation / img2video) — Tools, Skills & Integrations Research

**Date:** 26 March 2026 | **Researcher:** Haiku Subagent | **Focus:** Implementable OpenClaw tools for Branch 5

---

## Overview

Branch 5 (Image Generation) is responsible for:
1. **portrait_generator** — Generate character portraits for consistency
2. **ai_image_director** — Create detailed briefs for image generation
3. **image_generator** — Convert briefs to static images (ComfyUI: SDXL/Flux)
4. **image_qa** — Validate image quality, style match, technical specs
5. **image_animator** — Animate approved images via browser (img2video platforms)

**Current State:** ComfyUI local (SDXL/Flux) working. Browser animation workflow (Freepik/Higgsfield) not yet integrated.

**Key Constraint:** Economical workflow — minimize API costs, maximize local execution.

---

## Local Docs Read

From `C:\Users\User-OEM\Desktop\content-factory\auto_content_factory\docs/`:

- ✅ `04_BRANCH_ARCHITECTURE.md` — B5 structure: 5 agents, image gen + animation
- ✅ `03_PIPELINE_MAP.md` — Bloco 2 (15 steps): character pipeline, visual analysis, composition, direction, prompts, generation
- ✅ `00_CONTEXT.md` — Crisis: GCP suspended, migrated to local ComfyUI (SDXL/Flux) + OpenRouter fallback
- ✅ `06_MODEL_STRATEGY.md` — Sub-agent routing: Flash Lite for simple tasks, Haiku/mini for medium, Sonnet for complex
- ✅ `05_MULTI_MACHINE_ARCHITECTURE.md` — M1-M6 setup, ComfyUI exists on M1, no remote yet
- ✅ `09_HIERARCHY_AND_STRUCTURE.md` — B5 role: image generation, includes image_animator for browser-based animation
- ✅ `07_BRAINDUMP_OPENCLAW.md` — KMS for key rotation, dataset system for real images, local models installed
- ✅ `01_FRAMEWORK_RESEARCH.md` — OpenClaw 2026.3.22: multi-model, custom skills, security model

**Not read (outside scope):** KnowledgeBase courses (too deep), key_management_system configs (restricted).

---

## Problem Statement: B5 Gaps

### Current Workflow (Manual)
```
visual_plan.json (from B3)
    ↓
[Agent manually triggers ComfyUI via UI or script]
    ↓
generated_images/ (output)
    ↓
[No structured QA check]
    ↓
[image_animator has no platform connector for Freepik/Higgsfield]
    ↓
Image animation blocked
```

### Required Workflow (Autonomous)
```
visual_plan.json (from B3)
    ↓
[image_director creates generation brief]
    ↓
[image_generator → ComfyUI API call (async) → progress tracking]
    ↓
generated_images/ (with metadata)
    ↓
[image_qa → validate & score]
    ↓
[image_animator → browser automation (Freepik/Higgsfield) → mp4/webm]
    ↓
approved_animations/ (or fallback to static)
```

### Missing Infrastructure

1. **ComfyUI Integration**
   - ComfyUI API wrapper skill (OpenClaw → ComfyUI local via FastAPI)
   - Async job tracking (queue, polling, callback)
   - LoRA selection logic per account config
   - Sampler/quality parameter mapping

2. **Image QA Automation**
   - Vision-based quality scoring (style consistency, aesthetics, technical specs)
   - Face detection (character portrait validation)
   - Motion-readiness assessment (image suitability for animation)

3. **Browser Automation for img2video**
   - Freepik API integration (if available) or Selenium browser driver
   - Higgsfield API integration (if available) or browser automation
   - Output validation (video codec, frame count, duration matching audio)
   - Fallback strategy when animation fails

4. **Orchestration & Monitoring**
   - Job tracking across agents (status: queued → processing → done → approved/rejected)
   - Cost tracking (API calls, GPU time, storage)
   - Error recovery (retry logic, fallback chains)

---

## Concrete Tools & Skills Worth Building

### TIER 1: Essential (Implement First)

#### 1. **comfyui-bridge** (OpenClaw Skill)
**Purpose:** Enable B5 agents to queue, execute, and monitor ComfyUI jobs locally  
**Type:** Custom skill (no community dependency)

**What it does:**
- Accepts JSON workflow (prompt + generation parameters)
- Posts to ComfyUI WebSocket API (localhost:8188 or remote)
- Tracks job status in real-time (queued → executing → done)
- Retrieves generated images + metadata
- Handles errors, retries, timeouts
- Reports cost (GPU time, memory, if applicable)

**Inputs:**
```json
{
  "workflow_id": "portrait_v1",
  "prompt": "detailed character description...",
  "sampler": "DPMSolverMultistep",
  "cfg_scale": 7.5,
  "steps": 20,
  "lora": ["FilmGrain", "Monochrome"],
  "seed": 12345,
  "timeout_sec": 120
}
```

**Outputs:**
```json
{
  "status": "completed",
  "image_path": "/generated_images/video_001_scene_03_portrait.png",
  "metadata": {
    "width": 768,
    "height": 768,
    "seed": 12345,
    "generation_time_sec": 18.4,
    "model": "Juggernaut XL"
  }
}
```

**Implementation Notes:**
- Wraps existing ComfyUI Python client (comfy_client.py)
- Caches workflow templates per account
- Integrates with KMS for provider selection (local > OpenRouter)
- Handles queue depth monitoring

---

#### 2. **image-qa** (OpenClaw Skill + Agent)
**Purpose:** Validate generated/sourced images before downstream use  
**Type:** Custom skill + Haiku/Flash Lite agent

**What it does:**
- Vision model evaluates image against criteria (style, quality, relevance, technical)
- Detects faces in portraits (matches character specs)
- Scores motion-readiness (can this image be animated?)
- Flags issues (over-compression, style mismatch, censored content)
- Generates JSON report with accept/reject + remediation

**Inputs:**
```json
{
  "image_path": "/generated_images/vid_001_scene_03.png",
  "image_type": "portrait|scene|reference",
  "expected_style": "monochrome_1940s_film",
  "character_spec": {
    "name": "Winston Churchill",
    "age_range": "60-70",
    "key_features": ["distinctive scowl", "cigar"]
  },
  "motion_intent": true
}
```

**Outputs:**
```json
{
  "overall_score": 8.5,
  "verdict": "approved",
  "dimensions": {
    "style_match": 9,
    "quality": 8,
    "motion_readiness": 8,
    "character_accuracy": 8,
    "technical": 8
  },
  "flags": [],
  "remediation": null
}
```

**Model Selection:**
- Vision task → Claude Haiku (faster, cheaper) or Gemini Flash Lite
- Scoring + reasoning → Haiku
- Fallback: vision-enabled local model via Ollama (not critical path)

---

#### 3. **browser-animator** (OpenClaw Skill)
**Purpose:** Automate img2video workflows via browser platforms (Freepik/Higgsfield)  
**Type:** Custom skill (browser automation + API wrapper)

**Two Strategies:**

**A. API-First (Preferred if Freepik/Higgsfield expose APIs)**
```json
{
  "platform": "freepik|higgsfield",
  "image_path": "/approved_images/portrait_001.png",
  "motion_params": {
    "effect": "subtle_pan|zoom_in|3d_look",
    "duration_sec": 3.5,
    "transition": "fade"
  },
  "audio_duration_sec": 3.5,
  "output_format": "mp4"
}
```

**B. Browser Automation (Fallback using Selenium/Playwright)**
```
1. Open Freepik UI in headless browser
2. Upload image
3. Select animation preset
4. Configure timing to match audio
5. Export MP4
6. Validate output (codec, duration, file size)
```

**Outputs:**
```json
{
  "animation_path": "/animations/vid_001_scene_03_animated.mp4",
  "duration_sec": 3.5,
  "codec": "h264",
  "size_mb": 2.4,
  "status": "completed|timeout|api_error"
}
```

**Implementation Notes:**
- Requires investigation: Does Freepik have API? Does Higgsfield?
- If no public API: Selenium + image recognition (detect button positions)
- Timeout handling: 30s per animation job
- Fallback: return static image if animation fails (don't block B6)

---

### TIER 2: High-Value (Implement Second)

#### 4. **image-director-brief** (OpenClaw Agent)
**Purpose:** Convert visual_plan.json → generation brief  
**Type:** Haiku/GPT-mini agent (formatting + structure)

**Input from B3:**
```json
{
  "scene_id": "001_03",
  "duration_sec": 4.2,
  "narrative": "Churchill addressing Parliament...",
  "mood": "tense, formal, wartime resolve",
  "composition": "wide shot, low angle, dramatic lighting",
  "characters": [
    {"name": "Winston Churchill", "emotion": "stern", "pose": "standing"}
  ],
  "setting": "House of Commons, 1940s"
}
```

**Output (generation brief):**
```json
{
  "generation_type": "scene",
  "prompt": "A dignified formal scene in the House of Commons...",
  "negative_prompt": "modern, cartoonish, oversaturated",
  "style_guidance": "monochrome_film_grain_1940s",
  "sampler": "DPMSolverMultistep",
  "cfg_scale": 7.5,
  "steps": 20,
  "lora": ["FilmGrain_Redmond", "Monochrome_Halsman"],
  "seed": null,
  "priority": "high"
}
```

**Model:** Haiku (understands structure, maps mood→prompt)

---

#### 5. **portrait-consistency-check** (OpenClaw Skill)
**Purpose:** Ensure character portraits are visually consistent across scenes  
**Type:** Vision-based comparison skill

**Inputs:**
- Portrait 1 (scene A)
- Portrait 2 (scene B)
- Character name

**Logic:**
- Extract facial features (embeddings)
- Compare similarity (cosine distance)
- Flag if deviation > threshold (costume change, age progression acceptable)
- Report style consistency (lighting, background, pose variety)

**Output:**
```json
{
  "character": "Winston Churchill",
  "portrait_pairs": [
    {
      "img1": "scene_01.png",
      "img2": "scene_03.png",
      "similarity": 0.89,
      "verdict": "consistent",
      "notes": "different lighting, acceptable"
    }
  ]
}
```

**Use:** Before animating, ensure portraits won't look jarring in final video.

---

#### 6. **cost-tracker-b5** (OpenClaw Skill)
**Purpose:** Monitor spend on image generation (ComfyUI GPU time, API fallbacks)  
**Type:** Logging + analytics

**Tracks:**
- ComfyUI jobs: GPU time, model, VRAM, duration
- API calls (OpenRouter fallback): cost per image
- Storage: generated images size, archive
- Quality metrics: approval rate, remediation rate

**Reports to B10 (Monitoring branch)** and logs to shared/cost_registry.

---

### TIER 3: Polish & Optimization (Later)

#### 7. **lora-selector** (OpenClaw Agent)
**Purpose:** Choose optimal LoRAs per account/scene  
**Type:** Haiku agent + account config lookup

**Logic:**
- Read account config (loras.yaml)
- Match mood/style to available LoRAs
- Return ranked list with parameters

**Example:**
```json
{
  "mood": "wartime, monochrome, 1940s",
  "available_loras": [
    {"name": "FilmGrain_Redmond", "weight": 0.7},
    {"name": "Monochrome_Halsman", "weight": 0.9}
  ]
}
```

---

#### 8. **animation-fallback-handler** (OpenClaw Agent)
**Purpose:** Handle img2video timeouts gracefully  
**Type:** Decision agent

**Logic:**
- If animation fails after timeout:
  - Return static image (approved, ready for B6)
  - Log to error handler (B10)
  - Suggest manual override to Lucca via Telegram
  
**Keeps pipeline moving** without blocking.

---

## Recommended Artifacts & Contracts

### 1. **Image Generation Request** (B5 internal)
```
agents/branches/05_image_generation/contracts/generation_request.json
```
**Produced by:** ai_image_director  
**Consumed by:** image_generator  
**Schema:** See comfyui-bridge above

---

### 2. **Image QA Report** (B5 → B6)
```
agents/branches/05_image_generation/contracts/image_qa_report.json
```
**Example:**
```json
{
  "batch_id": "vid_001_scene_03",
  "images": [
    {
      "path": "/approved_images/vid_001_scene_03_portrait.png",
      "qa_score": 8.5,
      "verdict": "approved",
      "flags": [],
      "ready_for_animation": true
    }
  ],
  "summary": {
    "total": 1,
    "approved": 1,
    "rejected": 0,
    "remediation_needed": 0
  }
}
```

---

### 3. **Animation Output Spec** (B5 → B6)
```
agents/branches/05_image_generation/contracts/animation_output_spec.json
```
**Example:**
```json
{
  "scene_id": "001_03",
  "image_sources": [
    {
      "source_type": "generated",
      "path": "/approved_images/scene_portrait.png"
    }
  ],
  "animations": [
    {
      "image_id": "portrait_001",
      "animation_path": "/animations/scene_03_animated.mp4",
      "duration_sec": 3.5,
      "status": "completed",
      "fallback_to_static": false
    }
  ]
}
```

---

## Economical Workflow: Cheap Model Strategy

### Current Spend (Before Optimization)
- OpenRouter SDXL/Flux fallback: ~$5.55/video in images
- Gemini TTS: $0 (free tier + tier1)
- Gemini vision: $0 (tier1 free quota)

### Post-Optimization Spend
- ComfyUI local SDXL: **$0** (GPU already owned)
- Haiku/Flash Lite (QA + orchestration): **~$0.10/video** (5-10 calls × cheapest models)
- Browser animation (Freepik/Higgsfield): **$0-2.00/video** (depending on platform pricing)
- **Total: ~$0.10-2.10/video** (vs $5.55 today)

### Key Optimizations

1. **Local-first:** ComfyUI on M1 is production-ready. No API calls unless overflow.
2. **Batch QA:** Run image_qa in parallel across batch (Haiku is fast).
3. **Fallback chain:** Local → OpenRouter (only if ComfyUI capacity exceeded).
4. **Animation selection:** Prefer Freepik/Higgsfield API over platform SaaS if cost-effective.
5. **Monitoring:** Track actual costs per video in shared/cost_registry.

### Recommended Budget

| Component | Cost/Video | Note |
|-----------|-----------|------|
| Image generation (local) | $0 | ComfyUI SDXL/Flux |
| Image generation (fallback) | $1.50-3.00 | OpenRouter only if needed |
| Image QA | $0.05-0.10 | Haiku multi-turn |
| Animation (if Freepik API) | $0 | Custom skill |
| Animation (if browser) | $0.50-1.00 | Timeout risk, fallback to static |
| **Expected/video** | **~$0.50-1.50** | Conservative estimate |
| **Expected/month (50 videos)** | **~$25-75** | Huge win vs GCP crisis |

---

## Specific Integration Needs

### 1. ComfyUI Bridge — Technical Details

**Current State (M1):**
- ComfyUI running locally
- SDXL (Juggernaut XL): 6.7GB, ~15s/image
- Flux Dev Q6_K: 9.2GB, ~85s/image
- LoRAs installed: FilmGrain, Monochrome, Cinematic

**What's needed:**
- Python client for WebSocket API (ComfyUI has one, refactor it)
- Queue management (prevent overload)
- Workflow templating (per account, per style)
- Error recovery (corrupted output, OOM, timeout)

**How to integrate with OpenClaw:**
- Skill wraps Python client
- Agents call skill via OpenClaw's standard exec/process model
- Skill logs to JSON (for cost tracking)
- Supports async: agent spawns job, polls for status

---

### 2. Image QA Vision Model Selection

**Constraint:** Cost-effective per-image QA at scale (50-100 images/video)

**Options:**
- **Claude Haiku** (OpenClaw native): ~$0.002-0.004 per image, accurate
- **Gemini Flash Lite** (via KMS): $0 tier1 (free), fast
- **Ollama local** (llava-13b or similar): $0, slower (~5s per image)

**Recommendation:** Haiku for important checks (character faces), Flash Lite for general quality, Ollama as fallback.

---

### 3. Browser Automation: Freepik vs Higgsfield

**Investigation needed:**
- Does Freepik expose an image animation API? (Likely not public, requires partnership)
- Does Higgsfield have an API? (Unknown, research required)
- If neither: Use Selenium + browser automation (headless Chrome)

**For now, implement:**
- Generic `browser-animator` skill using Selenium
- Placeholder for Freepik/Higgsfield APIs (marked as "awaiting partnership")
- Fallback: return static image if animation fails (B6 handles it)

---

## Implementation Roadmap

### Phase 1 (Week 1-2): Foundation
- [ ] `comfyui-bridge` skill (wrap existing API)
- [ ] `image-qa` skill (vision + scoring)
- [ ] Test integration: B3 output → comfyui-bridge → image-qa → approval

### Phase 2 (Week 3-4): Automation
- [ ] `image-director-brief` agent (B3 → generation request)
- [ ] `portrait-consistency-check` skill
- [ ] Job tracking in shared/image_registry.json

### Phase 3 (Week 5-6): Animation
- [ ] `browser-animator` skill (Selenium, basic implementation)
- [ ] Test with Freepik/Higgsfield (or static fallback)
- [ ] `animation-fallback-handler` agent

### Phase 4 (Week 7-8): Optimization
- [ ] `cost-tracker-b5` logging
- [ ] `lora-selector` agent
- [ ] B5 fully autonomous, zero manual intervention

---

## Files to Create

```
agents/branches/05_image_generation/
├── skills/
│   ├── comfyui-bridge/
│   │   ├── SKILL.md
│   │   ├── client.py (wrapper)
│   │   └── workflows/ (templates per account)
│   ├── image-qa/
│   │   ├── SKILL.md
│   │   └── scorer.py (vision + logic)
│   └── browser-animator/
│       ├── SKILL.md
│       └── selenium_driver.py
├── agents/
│   ├── portrait_generator/
│   │   └── PROMPT.md
│   ├── ai_image_director/
│   │   ├── PROMPT.md
│   │   └── brief_generator.py (uses director agent)
│   ├── image_generator/
│   │   ├── PROMPT.md
│   │   └── (calls comfyui-bridge skill)
│   ├── image_qa/
│   │   ├── PROMPT.md
│   │   └── (calls image-qa skill)
│   └── image_animator/
│       ├── PROMPT.md
│       └── (calls browser-animator skill)
└── contracts/
    ├── generation_request.json
    ├── image_qa_report.json
    └── animation_output_spec.json
```

---

## Summary: Implementable Tools for B5

| Tool | Type | Priority | Est. Effort | Cost Impact |
|------|------|----------|-------------|-------------|
| comfyui-bridge | Skill | P0 | 1d | -$5/video |
| image-qa | Skill+Agent | P0 | 2d | -$0.10/video |
| image-director-brief | Agent | P1 | 1d | ~$0.05 |
| portrait-consistency-check | Skill | P1 | 1d | N/A (QA only) |
| browser-animator | Skill | P1 | 3d | -$1/video (vs SaaS) |
| lora-selector | Agent | P2 | 0.5d | N/A (optimization) |
| animation-fallback-handler | Agent | P2 | 0.5d | N/A (robustness) |
| cost-tracker-b5 | Skill | P2 | 1d | N/A (monitoring) |

**Total estimated effort:** 9-10 days  
**Total cost savings:** ~$4-5/video (~$200-250/month for 50 videos)  
**ROI:** Positive in month 1

---

## Conclusion

Branch 5 has all the pieces to become fully autonomous:
- ✅ ComfyUI local (ready to integrate)
- ✅ Image QA vision models (cheap + available)
- ⚠️ img2video browser automation (platform discovery needed)
- ✅ OpenClaw skill framework (ready for custom tools)

**Next immediate steps:**
1. Investigate Freepik/Higgsfield API availability
2. Implement comfyui-bridge as first skill
3. Add image-qa for quality gates
4. Test full workflow B3 → B5 → B6

**Blocker:** If no Freepik/Higgsfield API exists, implement Selenium fallback (more complex, but doable).
