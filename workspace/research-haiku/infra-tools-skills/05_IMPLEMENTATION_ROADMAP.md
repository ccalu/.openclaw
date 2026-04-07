# Haiku Research: Implementation Roadmap

**Status:** Research Complete  
**Date:** 2026-03-26  
**Purpose:** Translate research into actionable next steps  
**Owner:** Lucca + Claude Code

---

## Executive Summary

Based on analysis of Content Factory's video-editing department architecture (4-level agent hierarchy, 10 branches, ~42 agents), research identifies **4 critical infrastructure pieces** needed for safe, scalable multi-machine orchestration:

### Must-Do (Blocking)
1. **Git-based config versioning** — enables multi-machine sync, prevents config drift
2. **Hybrid Git+Local artifact coordination** — scene_bible.json and friends become single source of truth
3. **Remote-exec SSH skill** — M1 gateway can dispatch jobs to M2-M6 for ComfyUI/rendering
4. **Cost circuit breaker** — safety guardrail ($500/day hard stop)

### Nice-to-Have (Optimizations)
5. Config validation (CI/CD)
6. Monitoring dashboard
7. Browser automation (img2video)
8. Dedicated browser node (M7)
9. Cost attribution per account

---

## What Was Read

**Local docs in C:\Users\User-OEM\Desktop\content-factory\auto_content_factory\docs:**
- 00_CONTEXT.md — API crisis, pipeline structure, OpenClaw setup
- 03_PIPELINE_MAP.md — 50 operations, 20 creative decisions per video
- 04_BRANCH_ARCHITECTURE.md — 10 branches, ~42 agents, one team/multiple clients
- 05_MULTI_MACHINE_ARCHITECTURE.md — M1 gateway + M2-M6 nodes via SSH/Tailscale
- 06_MODEL_STRATEGY.md — GPT-5.4 Pro main, sub-agents via OpenRouter/Anthropic/local
- 07_BRAINDUMP_OPENCLAW.md — Context, KMS, dataset system, pipeline blocks
- 08_SECURITY_HARDENING.md — openclaw.json: workspaceOnly, exec security, deny_paths
- 09_HIERARCHY_AND_STRUCTURE.md — 4-level pyramid, incremental rollout, 2→5→12→43

**Intentionally skipped:** KnowledgeBase/ (course content, not project-specific)

---

## What's in This Research Package

### Document 01: DOCS_READ.md
- List of all docs read, key extracts, gaps identified
- Constraints (storage, multi-machine, creative direction, cost control)

### Document 02: RECOMMENDED_TOOLS_SKILLS.md
- 10 concrete tools/skills with business case
- **Priority table:** Must-do (1-5) vs Nice-to-have (6-10)
- **Critical path:** Git config → Local artifacts → Remote-exec → Cost breaker
- Cost/effort/impact estimates

### Document 03: ARTIFACT_CONTRACTS.md
- JSON schemas for 8 core artifacts
- Scene Bible (B1 output) → Audio Timestamps (B2) → Visual Plan (B3) → Assets (B4/B5) → Composition (B6) → Post-Prod (B7) → Manifest (B8)
- Data validation rules, immutability patterns
- How B9 (QA) and B10 (Monitoring) consume artifacts

### Document 04: CHEAP_MODEL_WORKFLOWS.md
- Model routing: nano ($0.0001) for formatting, mini ($0.003) for planning, haiku ($0.004) for nuance
- Per-branch cost breakdown: ~$0.054 in LLM costs per video
- Batching, caching, template engines to optimize costs
- Model selection decision tree

### Document 05: IMPLEMENTATION_ROADMAP.md (this file)
- Summary, next steps, success criteria
- Who does what, timeline estimates
- Decision points for Lucca

---

## Decisions Required from Lucca

### Decision 1: Storage Strategy
**Question:** Should configs (accounts/, branches/) be in GitHub or local-only?

**Recommendation:** GitHub (git-based, version control, audit trail, multi-machine sync)

**If you approve:**
- Task: Create private GitHub repo `auto_content_factory`
- Lucca: 5 min (create repo)
- Claude Code: 2 hours (move code + implement pre-commit hooks)
- Cost: $0/month (free private repo)
- Benefit: Version control, deployment safety, easy rollback

---

### Decision 2: Artifact Coordination
**Question:** How should B1-B8 pass JSON artifacts (scene_bible.json, asset_registry.json)?

**Recommendation:** Local workspace on M1, git-commit periodically (batched, not per-artifact)

**If you approve:**
- Structure: `~/.openclaw/workspace/production/run_<video_id>/`
- Artifacts: scene_bible.json (immutable), asset_registry.json (append-only)
- Git sync: Every 5 videos (batched) to avoid commit spam
- Implementation: 1 hour (Lucca approval + Claude Code: directory setup)

---

### Decision 3: Multi-Machine Job Dispatch
**Question:** Can M1 gateway dispatch work to M2-M6 via SSH?

**Recommendation:** Yes, build a **remote-exec skill**

**If you approve:**
- SSH setup: M2-M6 need OpenSSH + authorized_keys (Windows native)
- Skill: `remoteExec({ target: 'M3', script: 'portrait_gen.py', input: {...} })`
- Usage: B5 (portrait gen), B4 (asset search), B8 (rendering fallback)
- Implementation: Lucca (2-3 days) + Claude Code
- Benefit: Parallelizes CPU-heavy work, spreads load

---

### Decision 4: Cost Safety
**Question:** Should there be a hard stop at $500/day spend?

**Recommendation:** Yes, cost circuit breaker (cron-based monitoring)

**If you approve:**
- Cron job every 30 min: check KMS spend vs thresholds
- WARNING: $100/day (log to Telegram)
- SOFT: $250/day (slow down, warn Lucca)
- HARD: $500/day (pause B5 image gen, pause B4 asset search, alert Tobias)
- EMERGENCY: $1000/day (full stop, manual review)
- Implementation: 1 day (Lucca or Haiku)
- Benefit: Protects from API cost runaway

---

### Decision 5: Model Budget for Sub-Agents
**Question:** Target budget for LLM costs per video?

**Recommendation:** ~$0.05 (batching + cheap models)

**Current estimated:** $0.054 with optimizations

**If approved:**
- Use OpenRouter (GPT-5.4-nano, mini)
- Use Anthropic API (Claude Haiku) as secondary
- Use Google Gemini Flash (free) for multi-modal
- Use Ollama local (Qwen) for deterministic tasks
- Avoid GPT-5.4 full model for sub-agents
- Implementation: Routing rules in each branch (2 days Claude Code)

---

### Decision 6: Browser Node for Parallelization
**Question:** Deploy optional M7 for parallel asset search?

**Recommendation:** Not yet. Start with sequential on M2, upgrade if bottleneck appears

**If you change mind later:**
- M7: Dedicated VM or physical machine
- Purpose: Run 20 Chrome instances in parallel (asset research)
- Tools: Browserless.io ($20-50/mo) or local Chrome + Playwright
- Expected: 2-3x speedup for B4 asset research
- Cost: ~$50/mo or $0 (self-hosted)
- Can add in Phase 2 (after basic infrastructure works)

---

## Immediate Next Steps (Week 1)

### Step 1: GitHub Repo Setup (Lucca, 30 min)
```bash
# Create private repo "auto_content_factory"
# Add co-founders as collaborators
# Give Claude Code read/write access
```

### Step 2: Directory Structure (Claude Code, 2 hours)
```
auto_content_factory/
├── accounts/           # Versioned configs
├── branches/           # Shared branch definitions
├── shared/             # Runtime artifacts (created by agents)
├── docs/               # Existing docs
├── .pre-commit-hook    # Validate YAML + scan for secrets
└── .github/workflows/  # GitHub Actions CI (optional)
```

### Step 3: Workspace Sync Setup (Claude Code, 1 hour)
```
~/.openclaw/workspace/production/
├── configs/            # Auto-pulled from git (read-only in agents)
├── run_<video_id>/     # Per-video artifacts
└── cache/              # Asset caching
```

### Step 4: Cost Breaker Cron (Haiku or Lucca, 1 day)
```yaml
# ~openclaw/crons/cost_watcher.md
name: cost-watcher
schedule: "*/30 * * * *"  # Every 30 min
model: gpt-5.4-nano
action: check_spend_vs_thresholds
alert_channel: telegram
threshold_hard: 500  # $500/day
```

### Step 5: Remote-Exec Skill Planning (Claude Code, 1 day)
```javascript
// Define skill interface
// Plan SSH key management
// Map which agents use it (B5, B4, B8)
// Test on M1→M2 first
```

**Total Week 1:** ~4-5 days (mostly Claude Code + Lucca approval gates)

---

## Medium-Term (Weeks 2-4)

### Production Manager Agent (Tobias + Claude Code, 2-3 days)
- First true level-2 sub-agent
- Reads job queue, prioritizes, dispatches to B1-B10
- Runs on cron: 8 AM daily (configurable)
- Reports to Tobias on completion

### B1-B5 Agents (Claude Code, ~2 weeks)
- B1 (Pre-prod): scene_fetcher, scene_director, scene_bible_builder
- B2 (Audio): text_polish, tts_generator, audio_validator, timing_extractor
- B3 (Visual): character_identifier, entity_matcher, visual_director (batched calls)
- B4 (Asset): people_finder, location_finder, asset_judge
- B5 (Image Gen): portrait_generator, ai_image_director, image_qa

### Testing & Iteration
- Run 5-10 test videos end-to-end
- Validate artifact contracts
- Tune model costs
- Measure actual vs estimated spend

---

## Later Phases (Month 2+)

### Phase 2: B6-B10 Agents
- Scene composition, post-production, assembly, QA, monitoring
- 20-25 agents total

### Phase 3: Full Autonomy
- Production Manager runs 24/7
- Auto-dispatch 10+ videos/day
- Self-monitoring via B10

### Phase 4: Creative Iteration
- Agents adapt per-video (not rigid templates)
- A/B testing on quality improvements
- Cost attribution per account

---

## Success Criteria

### Criteria 1: Multi-Machine Sync Works
- M1 creates video → artifacts committed to git
- M2-M6 pull latest configs, use them
- No manual sync needed
- **Metric:** 0 config mismatch errors

### Criteria 2: Cost Control
- Actual spend: $2.50-3.00 per video (down from $5.55)
- No overspends >$500/day
- Circuit breaker alerts work
- **Metric:** $0.05 LLM + $2.50 GPU/render = $2.55/video

### Criteria 3: Artifact Integrity
- scene_bible.json never corrupted
- B1-B8 pipeline completes without data loss
- B9 QA catches errors
- **Metric:** 100% artifact validation pass rate

### Criteria 4: Agent Autonomy
- Production Manager (B0) runs on schedule
- Dispatches to B1-B10 without manual intervention
- Handles common failures gracefully
- **Metric:** 95%+ successful video completions

### Criteria 5: Safety Guardrails
- Cost exceeds $500/day → B5/B4 auto-paused
- Bad configs → CI/CD blocks deployment
- Secrets never leak (pre-commit hooks work)
- **Metric:** 0 security incidents, 0 credential exposures

---

## Files to Create (Claude Code)

### New Skill: `remote-exec`
```
~/.openclaw/skills/remote-exec/
├── SKILL.md         (documentation)
├── src/
│   ├── index.js     (OpenClaw plugin)
│   └── executor.py  (SSH dispatcher)
└── references/
    └── ssh-keymanagement.md
```

### New Skill: `cost-watcher`
```
~/.openclaw/skills/cost-watcher/
├── SKILL.md
└── src/
    └── index.js     (cron handler)
```

### New Artifact Validator (pre-commit hook)
```
auto_content_factory/
├── .pre-commit-hook  (Python script)
└── scripts/
    └── validate_configs.py
```

### New Cron Job
```
~/.openclaw/crons/
└── cost-watcher.yaml
```

---

## Open Questions for Lucca

1. **SSH keys:** Where should M2-M6 SSH keys be stored? (KMS? Local ~/.ssh?)
2. **Scheduling:** Should Production Manager run 8 AM daily, or always-running queue?
3. **GitHub visibility:** Should this repo be shareable with contractors later, or strictly internal?
4. **Browser node:** Is parallel asset search worth $50/mo or should we stick to sequential?
5. **Monitoring:** Slack, Telegram, or just OpenClaw web UI?

---

## How This Enables the Vision

The Content Factory's goal: **Autonomous creative agents, each video unique, not templated.**

This infrastructure enables that by:

1. **Coordination:** Artifact contracts (scene_bible.json, asset_registry.json) let agents reason about each other's outputs
2. **Scale:** Multi-machine dispatch (remote-exec) lets work run in parallel
3. **Safety:** Cost breaker + QA distributed throughout pipeline
4. **Flexibility:** Cheap models ($0.05/video) means agents can be more sophisticated without breaking budget
5. **Iteration:** Git + versioning means experiments (new prompts, new branches) can be tested safely

---

## Summary Table: What to Build

| Component | Priority | Effort | Cost | Owner | Timeline |
|-----------|----------|--------|------|-------|----------|
| Git config storage | 🔴 HIGH | 2h | $0 | Claude Code | Week 1 |
| Local artifact sync | 🔴 HIGH | 1h | $0 | Claude Code | Week 1 |
| Cost circuit breaker | 🔴 HIGH | 8h | $0 | Lucca/Haiku | Week 1 |
| Remote-exec skill | 🔴 HIGH | 2-3d | $0 | Claude Code | Week 1-2 |
| Production Manager agent | 🟠 MED | 2-3d | $0.02 | Claude Code | Week 2 |
| B1-B5 agents | 🟠 MED | 2w | $0.05 | Claude Code | Week 2-4 |
| Config validation (CI/CD) | 🟡 LOW | 3-4h | $0 | Claude Code | Week 2 |
| Monitoring dashboard | 🟡 LOW | 1-2d | $0 | Lucca/Claude | Week 3 |
| Browser img2video | 🟡 LOW | 5-7d | TBD | Claude Code | Week 4+ |

---

## Final Notes

### What This Isn't
- Not a complete implementation (you'll need Claude Code to build)
- Not a guarantee of success (artifacts/contracts still need testing)
- Not a final architecture (expect iteration based on real-world use)

### What This Is
- Research on what OpenClaw infrastructure Content Factory needs
- Concrete specifications (JSON contracts, model routing, cost breakdown)
- A roadmap to get from "planning stage" to "autonomous agents"
- De-risking by identifying gaps early (multi-machine sync, cost control)

### Why It Matters
Once these pieces are in place, each new branch/agent becomes **much simpler** to build — they just read JSON, do their job, write JSON. No coordination headaches.

---

## Contact & Next Steps

**Research completed by:** Haiku-infra-tools-skills subagent  
**Date:** 2026-03-26 14:37 GMT-3  
**Status:** Ready for review + implementation planning

**Next:** Lucca reviews, approves decisions (1-5 above), Claude Code starts building.

---

**Files created:**
- 01_DOCS_READ.md
- 02_RECOMMENDED_TOOLS_SKILLS.md
- 03_ARTIFACT_CONTRACTS.md
- 04_CHEAP_MODEL_WORKFLOWS.md
- 05_IMPLEMENTATION_ROADMAP.md (this file)

All files in: `C:\Users\User-OEM\.openclaw\workspace\research-haiku\infra-tools-skills\`
