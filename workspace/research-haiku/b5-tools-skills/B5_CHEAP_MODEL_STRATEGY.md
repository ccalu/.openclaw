# Branch 5 — Economical Model & Implementation Strategy

**Focus:** Minimize API costs for image generation, QA, and animation while maintaining quality.

---

## Current Cost Baseline (Before Optimization)

| Task | Provider | Model | Cost/Image | Status |
|------|----------|-------|-----------|--------|
| Generate (SDXL/Flux) | OpenRouter | SDXL/Flux API | $1.50–3.00 | Fallback only |
| Generate (Local) | ComfyUI | SDXL/Flux local | $0 | **Already deployed** |
| Image QA | Gemini | Flash Lite (free tier) | $0–0.01 | Available, unused |
| Image QA (premium) | Anthropic | Claude Haiku | $0.002–0.005 | Available, cheap |
| Animation | Freepik/Higgsfield | API/Browser | $0.50–2.00 | Not integrated |
| **Total/video (50 images)** | Mixed | | **$5.55–10.00** | **Crisis mode** |

---

## Proposed Optimization Strategy

### Strategy 1: Prioritize Local-First (80% cost reduction)

**Principle:** Use ComfyUI local for 95%+ of generation, API only for overflow/experimentation.

**Implementation:**

```
Image generation request
    ↓
[Check ComfyUI queue depth and GPU availability]
    ↓
If available: ComfyUI local  ($0) → ~15-20s per image
    ↓
If queue > 4 jobs: Fallback to OpenRouter  ($1.50–3.00)
    ↓
Track: actual usage ratio (target: >95% local)
```

**Metrics to Track:**
- Successful generations via ComfyUI: aim for 95%+
- API fallbacks: should be <5% (overflow only)
- GPU utilization: target 60–80% sustained
- Cost per 50 images: **$0–0.15** (from $5.55)

**How:** Implement queue depth check in `comfyui-bridge` skill before accepting jobs.

---

### Strategy 2: Haiku for Quality Checks (96% cheaper than Sonnet)

**Principle:** Use Claude Haiku for image QA scoring, save Sonnet for creative decisions only.

**Breakdown:**

| QA Task | Model | Cost/Score | Tokens | Rationale |
|---------|-------|-----------|--------|-----------|
| Style match | Haiku | $0.002 | 150–200 | Classification task |
| Technical quality | Haiku | $0.002 | 100–150 | Binary grading |
| Aesthetic | Haiku | $0.003 | 200–300 | Subjective, but Haiku sufficient |
| Face quality (portrait) | Flash Lite | $0 | 300–400 | Free tier, good for vision |
| Motion readiness | Haiku | $0.002 | 100–150 | Binary assessment |
| **Total per image** | Mixed | **$0.009–0.012** | ~900–1100 | **~$0.50 per 50 images** |

**Routing Logic (OpenClaw agent):**

```python
def select_qa_model(task_type):
    if task_type == "face_detection":
        return "gemini_flash_lite"  # Free, good vision
    elif task_type == "motion_readiness":
        return "haiku"  # Fast, cheap
    elif task_type == "aesthetic_judgment":
        return "haiku"  # Subjective but sufficient
    elif task_type == "technical_quality":
        return "haiku"  # Binary grading
    else:
        return "haiku"  # Default to cheapest
```

**Cost Example (50-image batch):**
- 5 portraits × 5 Haiku calls each = 25 Haiku calls @ $0.002/call = $0.05
- 45 scene images × 3 Haiku calls each = 135 Haiku calls @ $0.002/call = $0.27
- **Total: ~$0.32 per batch** (vs $50+ with Sonnet)

---

### Strategy 3: Freepik/Higgsfield API (If Available) or Selenium Fallback

**Current State:** img2video (Freepik/Higgsfield) not integrated. Two options:

#### Option A: Partnership API (Preferred)
- Freepik/Higgsfield may offer bulk API for partner developers
- Cost per animation: **$0.50–1.00** (estimated from public pricing)
- Integration: `browser-animator` skill with API wrapper
- Timeline: Requires vendor negotiation (weeks)

#### Option B: Selenium Browser Automation (Fallback)
- Use headless Chrome with Selenium to automate UI clicks
- No API key needed, but more fragile (web UI changes break it)
- Cost: **$0** (but slower, ~30s per animation)
- Risk: Freepik/Higgsfield may block automated access
- Implementation: 2–3 days

#### Option C: Hybrid (Recommended for Now)
- Start with Selenium fallback (Option B, quick)
- If animation fails → return static image (B6 handles it gracefully)
- Later, negotiate API partnership with Freepik (Option A)
- Cost profile: **$0 (Selenium)** → **$0.50 (API, post-partnership)**

**Recommended Implementation:** Start with **Option C (Selenium + static fallback)**.

---

## Per-Agent Model Selection

### B5 Agent 1: portrait_generator
**Role:** Create character portrait generation briefs  
**Input:** Character description (from B3)  
**Output:** Portrait generation request

**Model:** Haiku  
**Why:** Formatting task, simple prompt engineering  
**Cost:** ~$0.002 per portrait  
**Concurrency:** Can batch (10–20 at once)

---

### B5 Agent 2: ai_image_director
**Role:** Convert visual_plan → generation briefs  
**Input:** Scene narrative + mood  
**Output:** Detailed generation prompt + parameters

**Model:** Haiku (default) → Claude Sonnet (if complexity high)  
**Why:** Haiku sufficient for prompt generation; escalate to Sonnet only if generation quality is low  
**Cost:** ~$0.005 per brief (Haiku); $0.05 per brief (Sonnet)  
**Toggle:** Add flag `prompt_quality_check` — if true, use Sonnet; else Haiku

```python
if brief.creative_complexity > 7:
    model = "sonnet"  # Complex scenes need better composition
else:
    model = "haiku"   # Standard scenes
```

---

### B5 Agent 3: image_generator
**Role:** Execute ComfyUI generation  
**Input:** Generation request  
**Output:** Image path + metadata

**Model:** None (deterministic execution)  
**Tool:** comfyui-bridge skill  
**Cost:** $0 (local) or $1.50–3.00 (API fallback)  
**Target:** 95%+ local execution

---

### B5 Agent 4: image_qa
**Role:** Validate generated images  
**Input:** Image path + criteria  
**Output:** QA report + approval

**Model:** Haiku (primary) + Flash Lite (vision, optional)  
**Why:** Haiku fast for scoring; Flash Lite free for face detection  
**Cost:** ~$0.009 per image  
**Concurrency:** Batch 5–10 images in parallel

```python
def image_qa_agent(images):
    results = []
    for img in batch(images, size=5):
        # Parallel calls
        if "portrait" in img.type:
            haiku_score = haiku.evaluate(img, criteria="portrait")
            flash_vision = flash_lite.detect_faces(img)
            results.append(combine_scores(haiku_score, flash_vision))
        else:
            haiku_score = haiku.evaluate(img, criteria="scene")
            results.append(haiku_score)
    return results
```

---

### B5 Agent 5: image_animator
**Role:** Animate approved images  
**Input:** Image path + audio duration  
**Output:** Animated video (mp4) or static fallback

**Model:** None (browser automation or API)  
**Tool:** browser-animator skill  
**Cost:** $0 (Selenium) or $0.50–1.00 (Freepik API)  
**Fallback:** Return static frame if animation fails

---

## Cost Projection: 1 Video (50 Images)

### Baseline (Today — GCP Crisis)
```
50 images × $5.55/video = $277.50/month (unsustainable)
```

### Optimized (Proposed)

| Component | Model | Qty | Cost/Unit | Total |
|-----------|-------|-----|-----------|-------|
| Portrait generation | Haiku | 3 | $0.002 | $0.006 |
| Scene generation briefs | Haiku | 47 | $0.005 | $0.235 |
| Image QA (portraits) | Haiku+Flash | 3 | $0.009 | $0.027 |
| Image QA (scenes) | Haiku | 47 | $0.008 | $0.376 |
| Image generation (local) | ComfyUI | 50 | $0 | $0 |
| Image generation (API fallback) | OpenRouter | 2–3 | $2.00 | $0–6.00 |
| Animation (Selenium) | Selenium | 10–15 | $0 | $0 |
| Animation (API) | Freepik | 0 | $0 | $0 |
| **Total (pessimistic)** | | | | **~$6.64** |
| **Total (optimistic, all local)** | | | | **~$0.64** |

**Realistic monthly cost (50 videos):**
- **$32–332/month** (wide range, depends on overflow)
- **Target: <$100/month** (with >90% local execution)
- **Previous cost: >$277/month** (GCP crisis baseline)

**ROI:** Implementation cost (~$4,000 in developer time for skills) pays back in 2–3 months.

---

## Implementation Phasing for Cost Optimization

### Phase 1: Baseline (Week 1–2)
- Deploy `comfyui-bridge` (enable local generation)
- Deploy `image-qa` with Haiku routing
- Track actual costs in shared/cost_registry
- **Expected savings:** $3–4/video (eliminate API generation)

### Phase 2: Efficiency (Week 3–4)
- Optimize ComfyUI queue (parallel batching)
- Implement per-agent model selection (Haiku for simple, Sonnet for complex)
- A/B test Haiku vs Flash Lite for QA
- **Expected savings:** $0.20–0.50/video (better model routing)

### Phase 3: Animation (Week 5–6)
- Deploy `browser-animator` with Selenium
- Implement graceful fallback (static if fails)
- Cost: $0 (Selenium) or negotiate API
- **Expected savings:** $0.50–1.00/video (eliminate SaaS platform fees, if any)

### Phase 4: Monitoring (Week 7–8)
- Real-time cost tracking in B10 (Monitoring)
- Alerts if cost/video exceeds budget
- Automated model selection tuning
- **Ongoing:** Keep costs low through monitoring

---

## Guardrails: Quality vs Cost Trade-off

**Rule 1: Never sacrifice quality for cost**

```python
if qa_score < min_threshold:
    # Reject and regenerate, even if costs increase
    action = "regenerate"
else if qa_score < preferred_threshold and cost_avoidance_available:
    # Accept but flag for human review
    action = "accept_with_flag"
    alert("Lucca: Image below preferred quality, accepted due to time/cost")
```

**Rule 2: Batch similar tasks to avoid model-switching overhead**

```python
# Bad: Alternate between Haiku and Sonnet
for image in images:
    model = choose_model(image)  # Expensive context switching

# Good: Group by model
haiku_images = [i for i in images if i.complexity < 5]
sonnet_images = [i for i in images if i.complexity >= 5]
results = {}
results.update(batch_evaluate(haiku_images, "haiku"))
results.update(batch_evaluate(sonnet_images, "sonnet"))
```

**Rule 3: Track cost per agent per month**

```json
{
  "month": "2026-03",
  "agents": {
    "portrait_generator": {"cost_usd": 0.15, "calls": 150},
    "image_qa": {"cost_usd": 31.50, "calls": 3500},
    "image_animator": {"cost_usd": 0.00, "calls": 500},
    "image_generator": {"cost_usd": 12.00, "calls": 2500}
  },
  "total": 43.65,
  "videos_produced": 50,
  "cost_per_video": 0.87,
  "notes": "Well below $5.55 baseline"
}
```

---

## Open Questions & Decisions Needed

### Q1: Freepik/Higgsfield API Availability
- **Action:** Lucca or Micha to contact Freepik and Higgsfield directly
- **Timeline:** ASAP (impacts animation cost structure)
- **Options:**
  - A) Public API available → use direct API integration
  - B) Partnership API available → negotiate pricing
  - C) No API → use Selenium fallback + static images

### Q2: Acceptable QA Score Threshold
- **Current assumption:** >7.0/10 = approved
- **Reality check:** What Lucca observes in actual videos
- **Action:** Run Phase 1 pilot, gather real QA scores, calibrate

### Q3: Haiku vs Flash Lite Trade-off
- **Assumption:** Haiku $0.002 vs Flash Lite $0 (free tier)
- **Reality check:** Does Flash Lite quota cover B5 workload?
- **Action:** Calculate: 50 videos × 50 images × 3 calls = 7,500 free calls/month needed. Check Gemini free tier limits.

### Q4: ComfyUI Overflow Strategy
- **Assumption:** 95%+ local execution target
- **Reality check:** What's acceptable queue wait time?
- **Action:** Monitor M1 GPU utilization; if >90%, enable OpenRouter fallback

---

## Cost Monitoring Dashboard (Proposed)

**Location:** `shared/cost_registry.json` (updated by B10 Monitoring)

```json
{
  "period": "2026-03-26",
  "b5_metrics": {
    "generation": {
      "local_comfyui": {
        "count": 48,
        "cost": 0.0,
        "avg_time_sec": 17.2
      },
      "openrouter_fallback": {
        "count": 2,
        "cost": 3.00,
        "avg_time_sec": 4.3
      }
    },
    "qa": {
      "haiku": {
        "count": 250,
        "cost": 0.50,
        "avg_time_sec": 2.3
      },
      "flash_lite": {
        "count": 50,
        "cost": 0.0,
        "avg_time_sec": 1.8
      }
    },
    "animation": {
      "selenium": {
        "count": 15,
        "cost": 0.0,
        "success_rate": 0.87
      },
      "fallback_static": {
        "count": 2,
        "cost": 0.0,
        "note": "Selenium timeout"
      }
    }
  },
  "b5_total_cost": 3.50,
  "b5_videos": 1,
  "alerts": [
    {
      "level": "warning",
      "message": "Selenium animation timeout for 2 images. Consider fallback threshold.",
      "remediation": "Check ComfyUI output size; large images take longer to process in browser."
    }
  ]
}
```

---

## Summary: Cheap Model Strategy

| Optimization | Model | Cost Reduction | Effort | Priority |
|---|---|---|---|---|
| Local ComfyUI (production) | N/A | **$5.40/video** | ✅ Done | P0 |
| Haiku for QA (vs Sonnet) | Haiku | **$0.50/video** | 1d | P0 |
| Flash Lite for vision (free tier) | Flash Lite | **$0.05/video** | 1d | P1 |
| Selenium animation (vs SaaS) | Selenium | **$0.50–1.00/video** | 3d | P1 |
| Model routing (auto-select) | Haiku+Sonnet | **$0.20/video** | 2d | P2 |
| Batch processing | N/A | **$0.10/video** | 1d | P2 |
| **Total combined** | | **~$6.75/video saved** | 8d | |

**Expected outcome:** $5.55/video → **$0.50–1.50/video** ✅

**Monthly impact (50 videos):** $277.50 → **$25–75** 🎯
