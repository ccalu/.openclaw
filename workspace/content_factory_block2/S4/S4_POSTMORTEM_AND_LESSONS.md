# S4 Postmortem and Lessons

**Date:** 06 Apr 2026  
**Sector:** S4 Asset Research  
**Pilot:** Account 006 PT — Hotel Quitandinha

---

## Three Architectural Eras

### Era 1: Brave Search + Textual Classification (04 Apr)

**Stack:** Brave Search for URL discovery, textual heuristic classification, Firecrawl for download.

**What happened:** The pipeline found URLs via Brave Search, classified them without seeing the images (purely textual metadata), then downloaded from those URLs. Results were terrible — generic stock photos, logos, irrelevant content. The fundamental flaw: no component ever SAW the images.

**Result:** Phase 6 (asset materialization) proved the textual pipeline cannot produce production-quality visual assets. Decision by Lucca + Tobias: aggressive refactor of the pipeline middle.

### Era 2: Gemini Vision via KMS (06 Apr morning)

**Stack:** Serper.dev for Google Images, Gemini Vision via KMS cascade (3-flash → 3.1-flash-lite → 2.5-flash), shared modules copied from dataset_system.

**What happened:** Serper worked well (found real images). But Gemini via KMS produced cascades of 429 errors. With 35 targets × ~56 images each × batches of 5 = ~394 Gemini Vision calls needed. Even with Semaphore(4) and KMS key rotation, the rate limits were exhausted across all tiers. The pipeline ran for 30+ minutes and never completed the visual evaluation step.

**Root cause:** Gemini free tier has ~20 RPD/key, tier1 keys had wrong model names initially, and even with 90+ keys the volume was too high for vision calls with image data.

**Key learning:** Provider selection should be based on operational reality (RPM, reliability at your actual volume), not theoretical capacity or cost.

### Era 3: GPT-5.4-nano via OpenAI (06 Apr afternoon) — CURRENT

**Stack:** GPT-5.4-nano for query generation + visual evaluation, Serper.dev for Google Images, pHash dedup, video context injection, target consolidation.

**What happened:** 5,000 RPM, 50,000 images/min, 10M free tokens/day. Zero 429s. Pipeline completes in ~3 minutes. Cost: $0.14/video.

**Why it worked:** The rate limits are so generous that our ~110 calls per video are trivial. No cascade, no key rotation, no KMS — just one API key.

---

## Decisions Reverted

| Decision | Original | Reverted To | Why |
|----------|----------|-------------|-----|
| LLM provider | Gemini via KMS cascade | GPT-5.4-nano direct | 429 storms, KMS complexity, wrong model names |
| Visual evaluation | Textual classification | Vision model (sees images) | Textual can't judge visual quality |
| Download approach | Individual (Firecrawl) | Parallel (aiohttp + Serper) | Speed, reliability, dedup |
| Target generation | 1:1 entity-to-target | LLM consolidation | Duplicates, ambiguity, irretrievable targets |
| Actor materialization | 7 OpenClaw actors | 2 actors + helpers | Actors mangled paths, invented logic |
| Query generation | Python templates | LLM with video context | Generic queries miss the specific subject |

---

## Signals We Should Have Seen Earlier

1. **Textual classification was always wrong** — if no component sees the image, quality is random. We should have started with vision from day one.

2. **7 actors was over-materialization** — by Phase 3, web_investigator and research_worker had already been moved to helper-direct because LLM actors mangle paths. That was the signal: if actors keep failing at deterministic tasks, the sector is over-materialized.

3. **Gemini RPM was always too low for batch vision** — the dataset_system works because it processes 1 entity at a time with ~20-40 images. Scaling to 35 targets × 56 images was always going to hit rate limits. We should have checked RPM before committing.

4. **Labels from S3 are category-specific, not video-aware** — when S3's environment_location_extractor says "Cassino", it means "casino" as a location type. But the query generator needs "Casino do Hotel Quitandinha". The S3→S4 boundary needed intelligence from the start.

---

## Cost Comparison

| Approach | Duration | Cost | Completed? |
|----------|----------|------|-----------|
| Gemini/KMS (35 targets) | 30+ min | $0.00 (all free tier) | No — 429 storms |
| GPT-5.4-nano (28 targets) | ~3 min | $0.14 | Yes — zero errors |

The "free" approach cost hours of debugging and never produced results.
The $0.14 approach works every time in 3 minutes.

---

## What Worked Well

- **Supervisor shell checkpoint-resume** — proven across all 3 eras. Interruption and restart works correctly.
- **pHash deduplication** — consistently removes 5-15% of near-duplicate images.
- **Schema validation at every gate** — caught format mismatches immediately.
- **Serper.dev Google Images** — reliable, fast, good quality results.
- **Video context injection** — dramatically improved query relevance and evaluator accuracy.
- **Target consolidation** — reduced 35 targets to 20-28, eliminated duplicates and ambiguity.
- **Dual-format fallback** in coverage/pack — allowed smooth migration without breaking consumers.
