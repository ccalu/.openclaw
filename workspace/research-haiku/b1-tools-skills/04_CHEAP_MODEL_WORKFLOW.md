# Branch 1 Cheap Model Workflow

## Goal
Process scripts through B1 (Pre-Production) at minimal cost while maintaining quality for downstream branches.

**Target cost:** $0.10-0.30 per video for full B1 pipeline (screenplay division + validation + continuity extraction)

---

## Model Selection Matrix

### Task 1: Script Validation (Before Division)

**Model:** Claude Haiku 4.5 (via Anthropic API)  
**Cost:** ~$0.005 per validation  
**Why Haiku:**
- Lightweight validation (character encoding, placeholders, sanity checks)
- Fast inference
- Reliable for structured checks
- Cheap compared to GPT-4

**Input Token Budget:** ~500 tokens (script + validation rules)  
**Output Token Budget:** ~300 tokens (JSON report)  
**Cost per call:** (500 + 300) × $0.80/$1M = ~$0.0006 (Haiku pricing)

---

### Task 2: Screenplay Division (Core Work)

**Model:** GPT-4.1-mini (via KMS OpenAI fallback)  
**Cost:** ~$0.08-0.12 per video  
**Why GPT-4.1-mini:**
- Existing in v3 pipeline (proven prompts, tuning)
- Handles scene splitting better than cheaper models
- Balances cost vs quality
- Managed via KMS (key rotation, cooldown handling)

**Input Token Budget:** ~1500 tokens (script + video context + constraints)  
**Output Token Budget:** ~800 tokens (JSON scenes)  
**Cost per call:** (1500 + 800) × $0.15/$1M = ~$0.000345 × 2 batches = ~$0.0007 per batch

**Batching Strategy:**
- Split long scripts into 2-4 batches (parallel processing via Semaphore(8))
- Each batch ~800 words
- Total screenplay cost: ~$0.08-0.10 per video

---

### Task 3: Continuity Extraction (Lightweight)

**Model:** Claude Haiku 4.5 or local Ollama  
**Cost:** ~$0.005-0.01 per video  
**Why Haiku/Ollama:**
- Entity extraction is rule-based + light semantic understanding
- No complex reasoning needed
- Haiku is fast and cheap

**Alternative:** Use local Ollama with Qwen-3.5 (free, instant)

**Input:** scene_bible.json (structured data)  
**Output:** continuity_extract.json (entity registry)  
**Cost if Haiku:** ~$0.008  
**Cost if Ollama:** $0

---

### Task 4: Narrative Arc Validation (Optional, Conditional)

**Model:** GPT-4.1-mini (only if quality score < 0.80)  
**Cost:** ~$0.03 (conditional execution)  
**Why conditional:**
- Most scripts don't need this check
- Only trigger if script_validator warns about pacing issues
- Reduces average cost

---

## Orchestration Workflow (Haiku as Coordinator)

Use a cheap coordinator agent (Haiku) to decide which tasks to run:

```
START
  ├─ Haiku: Quick validation check (~$0.005)
  │   ├─ If PASS → proceed
  │   └─ If FAIL → halt, report to PM
  │
  ├─ GPT-4.1-mini: Screenplay division (~$0.10)
  │   └─ Output: raw scene list
  │
  ├─ Haiku: Continuity extraction (~$0.008)
  │   └─ Output: character/location registry
  │
  ├─ Haiku: Quality scoring (~$0.005)
  │   ├─ If score >= 0.85 → done (cost: $0.118)
  │   └─ If score < 0.85 → escalate to GPT-4.1-mini arc check (~$0.03)
  │
  └─ Aggregate → scene_bible.json, continuity_extract.json
```

**Average cost per video:** $0.118 (happy path) to $0.148 (with arc check)

---

## Budget Allocation for B1

### Monthly Volume Assumption
- **40 videos/week** × 4 weeks = **160 videos/month**

### Cost Breakdown

| Task | Cost/Video | 160/month | Monthly |
|------|-----------|-----------|---------|
| Script validation | $0.005 | 160 | $0.80 |
| Screenplay division | $0.10 | 160 | $16.00 |
| Continuity extraction | $0.008 | 160 | $1.28 |
| Quality check (Haiku) | $0.005 | 160 | $0.80 |
| Arc validation (30% of vids) | $0.03 | 48 | $1.44 |
| **Subtotal (B1 tasks)** | **$0.148** | **160** | **$20.32** |
| **KMS overhead** | ~5% | - | **$1.02** |
| **TOTAL B1** | - | - | **~$21.34** |

---

## Model Routing Rules

### If KMS GPT-4.1-mini Fails
**Fallback chain:**
1. GPT-4.1-mini via OpenRouter ($0.15/1M tokens, same cost)
2. Claude Sonnet via Anthropic API ($3/$15 per 1M tokens) — more expensive
3. Gemini 2.5 Flash via KMS (free tier)

**Decision logic:**
- Try KMS first (cost: $0.10)
- If rate-limited, retry with exponential backoff (KMS handles internally)
- If KMS exhausted, fall back to OpenRouter (cost: same, slower)
- Log fallback to B10 (Monitoring)

---

## Optimization Strategies

### Strategy 1: Batch Validation Across Multiple Videos
Instead of validating 1 script at a time, batch 10 scripts in single Haiku call:
- Input: 10 scripts
- Cost: ~$0.03 instead of $0.05 (saves $0.02 = 40% reduction)
- Trade-off: Latency (must wait for all 10)

**When to use:** Overnight batch processing, not urgent videos

---

### Strategy 2: Skip Optional Checks for High-Confidence Scripts
- Track script quality score over time per account
- If account has >95% pass rate, skip arc validation for routine scripts
- Still validate occasionally (2-3 per week) to catch drift

**Savings:** ~$0.03 per video on high-confidence accounts = ~$5/month

---

### Strategy 3: Local Continuation Extraction (Ollama)
Replace Haiku continuity extraction with local Ollama:
- Model: Qwen-3.5-9B (already available on M1)
- Cost: $0 (local inference)
- Speed: 2-3 sec per extraction
- Trade-off: ~5% less accuracy in alias detection

**Savings:** ~$0.008 per video = ~$1.28/month

**Breakeven:** If one Ollama inference fails per 100 videos, cost of re-running with Haiku = $0.008 (1% failure, 1 cost). Not worth it unless failures <1%.

**Recommendation:** Keep Haiku; Ollama as fallback for high-volume overflow.

---

## Cost Sensitivity Analysis

### If Video Volume Doubles (80 videos/week → 160/week)
- **Current cost:** $21.34/month (160 videos)
- **New cost:** $42.68/month (320 videos)
- **Per-video cost:** stays at $0.148

### If Model Prices Change
- **GPT-4.1-mini increases 50%:** +$8/month (expensive)
- **Haiku decreases 50%:** -$2/month (minimal impact, Haiku is already cheap)
- **KMS keys exhaust:** Fallback to OpenRouter (no cost change, just slower)

### If Validation Complexity Increases
- Add semantic checks (character name consistency): +$0.02 with Sonnet
- Add dialogue validation: +$0.03 with GPT-4.1-mini
- **Total could reach $0.20-0.25 per video**

---

## Implementation Schedule

### Week 1: MVP (Core Tasks Only)
```
script_validator (Haiku) → screenplay_divider (GPT-4.1-mini) → continuity_extractor (Haiku)
Cost: $0.118/video
```

### Week 2: Add Quality Gating
```
+ Quality score agent (Haiku)
+ Conditional arc validation (GPT-4.1-mini for low scores)
Cost: $0.148/video (average)
```

### Week 3: Optimize & Monitor
```
+ Batch validation for overnight processing
+ Fallback chain testing (if KMS fails)
+ Cost tracking per agent
Cost: $0.13-0.148/video (optimized)
```

### Week 4+: Scale
```
+ Ollama local extraction (if needed for high volume)
+ Cost monitoring via B10 (Monitoring branch)
+ Model swaps based on performance/cost
```

---

## Cost Monitoring Strategy

**Who:** B1 agent + B10 (Monitoring)  
**What to track:**
- Total tokens per screenplay division (input + output)
- Model used (GPT-4.1-mini vs fallback)
- Fallback rate (how often KMS exhausted)
- Cost per video (actual spend)
- Quality score distribution (to optimize arc validation trigger)

**Report:** Daily summary to Telegram @TobiasM1bot
```
B1 Cost Summary (Today)
━━━━━━━━━━━━━━━━━━━━━━
Scripts processed: 4
Screenplay cost: $0.36 (4 × $0.10)
Validation cost: $0.02
Extraction cost: $0.03
Arc checks: 0 (all > 0.85)
TOTAL: $0.41
Fallbacks: 0
Quality avg: 0.92 ✅
```

---

## Emergency Cost Controls

If costs spike unexpectedly:

1. **Haiku quota exceeded:** Switch to Ollama for extraction (free)
2. **GPT-4.1-mini overrun:** Use Gemini Flash fallback via KMS (free tier)
3. **All APIs failing:** Queue scripts for next day (batch processing)
4. **Emergency escalation:** Disable arc validation, skip non-critical videos

**Cost ceiling:** $50/month for B1 (hard limit before escalation)

---

## Long-Term Optimization Paths

### Path 1: Fine-tuned Smaller Model
- Fine-tune Qwen-3.5 on Content Factory screenplay examples
- Cost: $50 one-time (Ollama training)
- Result: Local model, $0 inference
- Timeline: Month 3+

### Path 2: Hybrid Extraction
- Use regex + Ollama for 80% of extractions (fast, free)
- Use Haiku only when confidence < 0.85 (5% of cases)
- Cost: $0.0004 per video
- Timeline: Week 3 (quick win)

### Path 3: Prompt Caching
- If using same system prompt for 100+ videos, use OpenAI prompt caching
- Saves 90% of context token cost
- Cost reduction: ~$0.05 per video after first run
- Timeline: Week 4+ (after system stabilizes)

---

## Comparison: Other Approaches Not Recommended

### Why not use Haiku for screenplay division?
- Haiku struggles with complex scene splitting
- Would need multiple retries for quality
- Hidden cost: 3-5× more API calls
- Not worth the $0.03 savings

### Why not use local Ollama for everything?
- Qwen-3.5 hallucinates on entity extraction
- Missing 20% of character aliases
- Downstream branches (B3/B4) waste time on failed lookups
- Real cost: downstream rework > $0.008 savings

### Why not use Gemini Flash for screenplay?
- Gemini APIs have lower rate limits
- KMS doesn't yet support Gemini rotation efficiently
- Would require rewriting screenplay agent prompts
- Risk: Unproven quality

---

## Summary

**Recommended B1 Model Stack:**
| Task | Model | Cost | Provider |
|------|-------|------|----------|
| Validation | Haiku 4.5 | $0.005 | Anthropic API |
| Screenplay | GPT-4.1-mini | $0.10 | KMS (OpenAI) |
| Extraction | Haiku 4.5 | $0.008 | Anthropic API |
| Quality Check | Haiku 4.5 | $0.005 | Anthropic API |
| Arc Validation (30%) | GPT-4.1-mini | $0.03 | KMS (conditional) |
| **TOTAL AVERAGE** | **-** | **$0.148** | **-** |

**For 160 videos/month: ~$23.68 (including 5% KMS overhead)**

**For 320 videos/month: ~$47.36 (scales linearly)**
