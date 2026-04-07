# S4 Reusable Patterns for S5/S6

Patterns extracted from S4 development that should accelerate future sector implementation.

---

## 1. Target Consolidation Pattern

**When to use:** When S3 outputs entities from multiple operators that may overlap semantically.

**Pattern:**
1. Collect all entities from S3 compiled_entities (flat list)
2. Deterministic pre-pass: normalize strings, detect exact label matches
3. LLM call: merge overlapping entities, contextualize labels for the specific video, classify searchability
4. Deterministic validation: ensure all entity_ids preserved, no orphans, schema valid

**Why it matters:** Without consolidation, "Cassino" becomes a search for the Italian city, "Lago artificial" returns generic lakes, and duplicate entities waste retrieval budget.

**Replication checklist:**
- [ ] Does this sector consume S3 entities?
- [ ] Could entities from different S3 operators refer to the same visual subject?
- [ ] Do entity labels need video-specific context to be unambiguous?
- [ ] Are some entities inherently non-retrievable for this sector's purpose?

---

## 2. Helper-Direct Substitution Pattern

**When to use:** When an OpenClaw actor consistently fails at deterministic tasks (path derivation, file I/O, schema-constrained output).

**Pattern:** Replace `_dispatch_operator()` call in supervisor_shell with `subprocess.run([sys.executable, helper_script, ...])`.

**Warning signs that an actor needs helper-direct:**
- Actor writes files to wrong paths
- Actor invents its own logic instead of calling the Python helper
- Actor drops prefixes from filenames (e.g., `t` from `t004`)
- Actor produces valid-looking but semantically wrong output
- Actor works on first run but fails on second (session contamination)

**Rule of thumb:** If a phase requires deterministic Python logic (file I/O, schema validation, API calls with specific parameters), use helper-direct. Only use OpenClaw actors for phases requiring genuine creative judgment.

---

## 3. Provider Selection by Operational Reality

**When to use:** When choosing which LLM/API to use for a sector's core calls.

**Pattern:** Check actual RPM/RPD at your expected call volume BEFORE committing to a provider.

**Decision matrix:**

| Factor | Check |
|--------|-------|
| RPM at your volume | Will N calls/min hit the limit? |
| Free tier capacity | Is the free tier enough for your daily volume? |
| Rate limit behaviour | 429 with retry-after? Or hard block? |
| Vision support | Does it accept base64 images in the content array? |
| JSON mode | Does it support response_format: json_object? |
| Key management | Single key sufficient? Or need rotation? |

**S4 lesson:** Gemini was theoretically cheaper but operationally unusable at our volume. GPT-5.4-nano costs $0.14/video but completes in 3 minutes with zero errors.

---

## 4. Video Context Injection

**When to use:** When any sector needs to make decisions that depend on the video's subject, era, or style.

**Pattern:**
1. Read the S3 source_package (first 15-20 scenes)
2. Read the video directory name as additional hint
3. One LLM call to extract structured context: title, subject, era, style, key_locations, visual_era_guidance
4. Inject this context into all downstream prompts

**Why it matters:** Without context, queries are generic ("artificial lake") and evaluators accept wrong-era content (modern architecture for a 1940s documentary). With context, queries are anchored ("lago artificial Hotel Quitandinha Petropolis") and evaluators reject anachronistic content.

**Cost:** 1 LLM call, ~3-4 seconds, negligible tokens.

---

## 5. Dual-Format Fallback

**When to use:** When replacing an artifact format and consumers may encounter either old or new format.

**Pattern:**
```python
new_path = asset_report_path(sr, tid)
if new_path.exists():
    data = read_json(new_path)
    # process new format
else:
    # fallback to legacy
    legacy_path = evaluated_set_path(sr, tid)
    data = read_json(legacy_path)
    # process legacy format
```

**Rule:** Always update ALL consumers before declaring a format migration complete. The fallback is a bridge, not a permanent solution.

---

## 6. Over-Materialization Warning Signs

**When to use:** During sector planning, before committing to actor count.

**Warning signs that a sector is over-materialized:**
- More than 3-4 actors planned for a sector
- Multiple actors that do primarily file I/O or API calls (not creative judgment)
- Actor names that describe deterministic operations (e.g., "downloader", "validator", "builder")
- Previous sector (S3) already had actors moved to helper-direct

**Healthier pattern:** Start with 2-3 actors max. Use helper-direct for deterministic work. Only materialize actors for phases that genuinely benefit from LLM creative judgment.

**S4 lesson:** Started with 7 actors (SM + 6 operators). Ended with 2 actors + 5 helpers. The 5 helper-direct moves were all forced by operational failures, not planned. Next time, start closer to the final topology.

---

## 7. Session Cleanup Before Each Run

**When to use:** Any sector using OpenClaw actors across multiple videos.

**Pattern:** Before the first phase, run `openclaw sessions cleanup --enforce --agent <agent_id>` for each agent in the sector.

**Why:** OpenClaw sessions accumulate context across runs. An actor that processed video A retains that context when processing video B, leading to confused outputs or wrong path references.

---

## Quick Decision Checklist for New Sectors

Before materializing actors for a new sector, answer:

1. How many phases need genuine LLM creative judgment? → Those get actors
2. How many phases are deterministic Python (file I/O, API calls, transforms)? → Those get helper-direct
3. What's the expected call volume for external APIs? → Check RPM before choosing provider
4. Does this sector consume S3 entities? → Consider target consolidation
5. Do prompts need video-specific context? → Add context extraction step
6. Are there artifact format changes in flight? → Add dual-format fallback
