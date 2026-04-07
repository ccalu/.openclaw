# S4 Troubleshooting Guide

---

## 429 Rate Limit Storms (Gemini/KMS)

**Symptom:** Visual evaluation phase runs for 30+ minutes, logs show endless `RATE_LIMIT (free429=N, t1_429=N)` messages, no targets complete.

**Cause:** Too many Gemini Vision calls relative to available RPM. With 35 targets × ~15 images × batches of 5 = ~100+ calls, and Gemini free tier at ~20 RPD/key, even 90 keys aren't enough for vision calls with image data.

**Resolution:** S4 V3 switched to GPT-5.4-nano (5000 RPM). If you must use Gemini, reduce to Semaphore(1) and accept 30+ minute runs.

**Prevention:** Before choosing a vision provider, check actual RPM at your expected call volume. Don't trust theoretical capacity.

---

## Label Ambiguity → Wrong Search Results

**Symptom:** Target "Cassino" returns images of the city Cassino in Italy. "Gramado frontal" returns images of the city Gramado in Brazil.

**Cause:** S3 entities have category-specific labels without video context. The query generator searches for the literal label.

**Resolution:** Target consolidation contextualizes labels: "Cassino" → "Cassino do Hotel Quitandinha, Petropolis". Video context is injected into queries.

**Prevention:** Always run target consolidation (Wave 2 of the pipeline). Check the target_builder_report.md for contextualized labels before running the asset pipeline.

---

## False Unresolved in Pack (Legacy Format Mismatch)

**Symptom:** Pack shows all targets as "unresolved" and 0 assets, but assets/ directories have real images.

**Cause:** Coverage analyst and pack compiler reading `evaluated_candidate_set.json` (old format) instead of `asset_materialization_report.json` (new format). The old format doesn't exist in V3.

**Resolution:** Updated coverage_analyst.py and pack_compiler.py to read new format first, fall back to legacy. Both files were rewritten on 06 Apr 2026.

**Prevention:** When replacing an artifact format, always update ALL consumers before declaring the migration complete.

---

## OpenClaw Session Accumulation

**Symptom:** OpenClaw actor produces confused or wrong output. References data from a previous video. Context seems polluted.

**Cause:** OpenClaw sessions accumulate across runs. An actor that processed video A still has that context when processing video B.

**Resolution:** supervisor_shell.py runs `openclaw sessions cleanup --enforce` for all S4 agents before each run.

**Prevention:** Always clean sessions before starting a new video. The cleanup is automatic in supervisor_shell.py but may timeout (15s per agent). Timeouts are non-blocking — the pipeline continues.

---

## OpenClaw Actor Ignores Helper

**Symptom:** Target builder produces 8 targets with curated labels instead of the expected 26 from consolidation. The OpenClaw actor did its own logic instead of calling target_builder.py.

**Cause:** LLM actors in OpenClaw sometimes decide to "help" by doing the work internally instead of calling the Python helper. This is especially common with target_builder and web_investigator.

**Resolution:** Move the phase to helper-direct in supervisor_shell.py — call Python directly via subprocess instead of dispatching to an OpenClaw actor.

**Prevention:** Default to helper-direct for any phase that requires deterministic Python logic. Only use OpenClaw actors for phases where the LLM genuinely needs creative judgment (coverage assessment, pack compilation).

---

## Windows-Specific Issues

### .cmd Extension for OpenClaw CLI
**Symptom:** `FileNotFoundError: openclaw` or `firecrawl` not found in subprocess calls.

**Fix:** Use `openclaw.cmd` instead of `openclaw` in subprocess calls on Windows.

### Unicode in print()
**Symptom:** `UnicodeEncodeError: 'charmap' codec can't encode character` when printing arrows (→) or special chars.

**Fix:** Use ASCII equivalents in print statements (`->` instead of `→`). Loguru handles UTF-8 fine; it's only Python's default `print()` that fails with Windows cp1252.

### Path Encoding
**Symptom:** Paths with accented characters (Petrópolis) cause issues in some tools.

**Fix:** Always use `Path.resolve()` and pass paths as strings to subprocess. Avoid em-dashes in directory names.

---

## Visual Quality Still Poor Despite Pipeline Success

**Symptom:** Pipeline completes, images are downloaded, but approved images aren't relevant to the target.

**Possible causes:**
1. **Video context not extracted** — check runtime/video_context.json exists and has meaningful content
2. **Queries too generic** — check search_queries.json for each target. If queries don't mention the specific subject, the context injection may have failed
3. **Evaluator too lenient** — check asset_materialization_report.json entries. If all images score 7+, the evaluator system prompt may need tightening
4. **Serper results are poor** — some targets genuinely have no good images on Google Images

**Diagnosis:** Open a few images from assets/ manually. If they look irrelevant, check the corresponding _asset_materialization_report.json for the evaluator's reasoning.
