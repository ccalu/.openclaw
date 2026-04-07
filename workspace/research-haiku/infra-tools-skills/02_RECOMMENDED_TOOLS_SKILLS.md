# Haiku Research: Recommended Tools & Skills for Content Factory

**Status:** Actionable recommendations for OpenClaw infrastructure  
**Date:** 2026-03-26  
**Audience:** Lucca + Tobias, Lucca + Claude Code (implementation)

---

## 1. SHARED STORAGE STRATEGY (Git-based)

### Decision: GitHub as Source of Truth for Configs

**Why GitHub over Google Drive or local-only?**
- Version control + history for all configs (accounts/, branch prompts, style guides)
- Multi-machine synchronization (M2-M6 pull latest configs via git)
- Audit trail (who changed what, when)
- CI/CD integration potential (pre-flight validation of configs)
- Supports branching (test new styles before merge to main)

**Implementation:**
```
Repository structure:
auto_content_factory/
├── accounts/           # Versioned per-account configs
│   ├── 003_wwii/
│   │   ├── style_guide.md
│   │   ├── visual_rules.md
│   │   ├── loras.yaml
│   │   ├── catalogs/
│   │   └── prompts/
│   └── ...
├── branches/           # Shared branch definitions
│   ├── 01_pre_production/
│   │   └── agent_prompts.md
│   └── ...
└── shared/             # Runtime artifacts (created by agents)
    ├── scene_bible/
    ├── character_bible/
    └── asset_registry/
```

**Git Workflow:**
- Main branch: stable, production-ready configs
- Develop branch: testing new styles/prompts
- Feature branches: per-new-account or per-style-experiment
- Pre-commit hooks: validate YAML syntax, check for secrets (API keys)

**Cost:** $0 (GitHub free for private repos)

---

## 2. SHARED ARTIFACT STORAGE (Workspace-based)

### Decision: Hybrid Git + Local Workspace

**For slow-changing data (configs):** Git (auto-pulled at agent start)  
**For fast-changing data (artifacts):** Local workspace on M1, sync to M2-M6 via job output

**How artifacts flow:**
1. B1 (Pre-prod) creates scene_bible.json → saved to local workspace + committed to git
2. B2-B10 read scene_bible.json from workspace (faster than git for each agent)
3. B4 (Asset Research) appends to asset_registry.json → committed periodically
4. Each branch's output becomes next branch's input (pipeline)

**Implementation:**
```
~/.openclaw/workspace/production/
├── configs/              # Git-synced (read-only in agents)
│   ├── accounts/
│   └── branches/
├── run_<video_id>/       # Per-video artifacts
│   ├── scene_bible.json
│   ├── visual_plan.json
│   ├── asset_registry.json
│   ├── music_plan.json
│   └── final.mp4
└── cache/                # Asset cache, generated images
```

**Git hooks for auto-sync:**
- Pre-agent-start: `git pull --rebase` in configs/
- Post-artifact: `git add` + `git commit` for scene_bible.json, asset_registry.json (periodic, batched)

**Cost:** $0

---

## 3. MULTI-MACHINE JOB DISPATCH (SSH-based Skill)

### Decision: Custom OpenClaw Skill for Remote Execution

**Problem:** M1 agents need to trigger jobs on M2-M6 (ComfyUI, rendering, parallel asset search)

**Solution:** Build a **remote-exec skill** that:
1. Takes: `target_machine`, `command`, `payload_json`, `expected_output_path`
2. SSH into M2-M6, execute Python script
3. Polls for completion (or uses callback)
4. Retrieves output JSON/images
5. Returns to calling agent

**Skill Signature:**
```javascript
// Usage in branch agents:
const result = await remoteExec({
  target: 'M3',
  script: 'portrait_generator.py',
  input: { characters: [...], style_guide: {...} },
  outputPath: 'C:\\shared\\cache\\portraits\\',
  timeout: 600
});
```

**Implementation Details:**
- Uses OpenSSH on Windows (M2-M6)
- SSH keys: stored in KMS or local ~/.ssh/ (never in agents' workspace)
- Output location: shared folder or retrieved back to M1
- Fallback: if M3 unreachable, try M4, M5, etc.

**Why custom over existing tools?**
- OpenClaw's built-in `exec` is local-only (runs on M1)
- We need cross-machine job dispatch
- KMS-aware (knows which machines have which capabilities)

**Cost:** $0 (custom skill)  
**Implementation:** ~2-3 days (Lucca + Claude Code)

---

## 4. BROWSER AUTOMATION FOR IMG2VIDEO (Selenium Skill)

### Decision: Custom Skill for Image Animation

**Problem:** B5 needs to animate static images via Freepik/Higgsfield APIs (img2video services)

**Current limitation:** No built-in browser automation in OpenClaw for Web APIs that require login/session

**Solution:** Build a **browser-animation skill** that:
1. Logs into Freepik/Higgsfield (credentials from KMS)
2. Uploads image → triggers animation job
3. Polls for completion
4. Downloads MP4 → stores in asset_registry

**Skill Signature:**
```javascript
const animatedClip = await browserAnimate({
  imageUrl: 'C:\\cache\\portrait.jpg',
  service: 'freepik', // or 'higgsfield'
  animationStyle: 'cinematic_pan', // per style_guide
  duration: 5,
  timeout: 300 // seconds
});
// Returns: { videoPath, quality, metadata }
```

**Implementation:**
- Use Selenium WebDriver (Python) or Playwright (Node.js)
- Store session tokens in KMS (not workspace)
- Rate-limit API calls (Freepik/Higgsfield have quotas)
- Fallback: if animation fails, use static image

**Cost:** Freepik/Higgsfield subscription (already budgeted?)  
**Implementation:** ~5-7 days (more complex than remote-exec)

---

## 5. COST CIRCUIT BREAKER (Cron-based Monitoring)

### Decision: Standalone Cost Tracker Cron Job

**Problem:** Agents don't inherently know about daily/monthly spend caps

**Solution:** Build a **cost-watcher cron job** (runs every 30 min) that:
1. Queries KMS for accumulated spend (APIs, rendering, storage)
2. Compares against thresholds:
   - WARNING: $100/day
   - SOFT: $250/day (slow down, warn Lucca)
   - HARD: $500/day (pause new jobs, alert Tobias)
   - EMERGENCY: $1000/day (emergency stop, manual review)
3. Posts alerts to Telegram (@TobiasM1bot)
4. Can programmatically pause B5 (image gen) and B4 (asset search) if HARD reached

**Implementation:**
```cron
# Every 30 minutes
*/30 * * * * openclaw cron run cost-watcher
```

**Skill Artifact:**
```json
{
  "name": "cost-watcher",
  "type": "cron",
  "schedule": "*/30 * * * *",
  "model": "gpt-5.4-nano",
  "action": "check_spend_vs_thresholds",
  "alert_channel": "telegram",
  "action_on_hard": "pause_generation_jobs"
}
```

**Cost:** $0.01/run (nano model, 30x/day)  
**Implementation:** ~1 day (Tobias or Haiku)

---

## 6. CONFIG VALIDATION & PRE-FLIGHT CHECKS (GitHub Actions CI)

### Decision: GitHub Actions Workflow

**Problem:** Bad configs (typos in prompts, missing keys, invalid YAML) cause agent failures downstream

**Solution:** GitHub Actions workflow that:
1. On every commit to accounts/ or branches/:
   - Validate YAML syntax
   - Check for API key leaks (pre-commit hook anti-pattern)
   - Validate prompt templates (length, required fields)
   - Check LoRA paths exist (for image gen)
   - Run linter on markdown

2. Comment on PR with validation results
3. Block merge if validation fails

**Config:**
```yaml
# .github/workflows/validate-configs.yml
on: [push, pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: |
          python scripts/validate_configs.py accounts/ branches/
          grep -r 'sk-' . && exit 1 || true  # Reject API key commits
```

**Cost:** $0 (GitHub Actions free tier includes 2000 min/month)  
**Implementation:** ~3-4 hours (scripting)

---

## 7. MONITORING DASHBOARD (Simple JSON API)

### Decision: REST API Endpoint (M1 Gateway) + Static Dashboard

**Problem:** B10 (Monitoring) has no clear way to expose real-time status

**Solution:** Expose a simple REST API on M1 Gateway that returns:
```json
{
  "current_job_id": "video_12345",
  "progress": "B5/10 (Image Gen, 67%)",
  "spend_today": "$127.55",
  "next_milestone": "B6 Scene Composition (ETA 2h)",
  "active_agents": 8,
  "errors": [],
  "last_completed_video": "video_12343 (2h ago)"
}
```

**Dashboard options:**
1. Static HTML file (simplest) — served from Gateway port 18790
2. Grafana + JSON datasource (if Lucca wants historical graphs)
3. Discord rich embed (message refresh every 5 min in Telegram topic)

**Implementation:**
- Expose via OpenClaw's built-in HTTP server
- JSON source: artifact files + KMS spend query
- Refresh: every 30s (cheap, local)

**Cost:** $0  
**Implementation:** ~1-2 days

---

## 8. PRODUCTION MANAGER AGENT LAUNCHER (Skill)

### Decision: Scheduling Skill + Cron Trigger

**Problem:** Production Manager (Level 2) needs to run on a schedule (e.g., 8 AM daily) to:
1. Read pending videos from Micha's sheet
2. Prioritize by urgency
3. Dequeue first X videos
4. Dispatch to B1-B10

**Solution:** Build a **scheduler skill** that:
1. Runs on cron: `0 8 * * *` (8 AM daily, configurable)
2. Fetches job queue from sheet (or local JSON)
3. Dispatches TOP 3 jobs to Production Manager agent
4. Production Manager orchestrates the 10 branches

**Cron Config:**
```yaml
name: pm-daily-dispatch
schedule: "0 8 * * *"  # 8 AM
agent: production_manager
action: dispatch_daily_batch
batch_size: 3
```

**Cost:** $0.02 (nano model × 3 runs/day if needed)  
**Implementation:** ~2 days (integrated with B1-B10)

---

## 9. BROWSER NODE FOR PARALLEL ASSET SEARCH (Hardware)

### Decision: Optional M7 Browser Node

**Problem:** B4 (Asset Research) needs to scrape Library of Congress, Europeana, Smithsonian simultaneously

**Current:** Sequential scraping (slow)  
**Better:** Parallel Chrome instances on dedicated machine

**Option A (cheap):** Run Playwright on M2 during off-hours, parallelize 4 Chrome processes  
**Option B (ideal):** Dedicated M7 (VM or actual machine) running 20 Chrome instances in parallel via Browserless.io API

**Recommendation:** Start with Option A, upgrade to Option B if asset search becomes bottleneck

**Cost:**
- Option A: $0 (use existing M2, off-peak CPU)
- Option B: $20-50/mo (Browserless.io SaaS) OR ~$50/mo (dedicated VM with Chrome)

**Implementation:** ~3-5 days (Playwright task scheduling)

---

## 10. COST ATTRIBUTION PER ACCOUNT (KMS Enhancement)

### Decision: Tag All API Calls with Account ID

**Problem:** KMS tracks total spend, but no breakdown by account (003_wwii vs 005_dark_history)

**Solution:** Modify KMS to track:
```json
{
  "api_call_id": "gemini_01234",
  "account_id": "003",
  "branch_id": "B5",
  "model": "Gemini Flash",
  "tokens_in": 2048,
  "tokens_out": 512,
  "cost": 0.01,
  "timestamp": "2026-03-26T14:37:00Z"
}
```

Then generate reports:
- Daily spend per account
- Monthly ROI per account (video quality × views / spend)
- Which accounts are profitable?

**Implementation:** Modify KMS logging + add B10 cost-report agent

**Cost:** $0 (configuration change)  
**Implementation:** ~2 days

---

## Summary Table

| # | Tool/Skill | Type | Priority | Cost | Effort | Impact |
|---|---|---|---|---|---|---|
| 1 | Git-based Config Storage | Infra | 🔴 HIGH | $0 | 2 days | Enables version control, multi-machine sync |
| 2 | Hybrid Git+Local Artifacts | Infra | 🔴 HIGH | $0 | 1 day | Solves artifact coordination |
| 3 | Remote-Exec SSH Skill | Skill | 🔴 HIGH | $0 | 2-3 days | Enables M2-M6 job dispatch |
| 4 | Browser-Animation Skill | Skill | 🟠 MEDIUM | Freepik $ | 5-7 days | Enables img2video (quality boost) |
| 5 | Cost Circuit Breaker | Cron | 🔴 HIGH | $0 | 1 day | Safety guardrail on spend |
| 6 | Config Validation (GitHub Actions) | CI/CD | 🟠 MEDIUM | $0 | 3-4 hrs | Prevents bad configs reaching agents |
| 7 | Monitoring Dashboard | API | 🟠 MEDIUM | $0 | 1-2 days | Visibility into production |
| 8 | Production Manager Scheduler | Skill | 🟠 MEDIUM | $0 | 2 days | Enables daily batch triggering |
| 9 | Browser Node (M7) | Hardware | 🟡 LOW | $0-50 | 3-5 days | Parallelizes asset search (nice-to-have) |
| 10 | Cost Attribution per Account | Enhancement | 🟡 LOW | $0 | 2 days | Financial clarity per client |

**Critical Path (must do first):**
1. Git config storage (#1)
2. Local artifact coordination (#2)
3. Remote-exec skill (#3)
4. Cost circuit breaker (#5)

**Can follow after:**
4. Production Manager scheduler (#8)
5. Config validation (#6)
6. Monitoring dashboard (#7)

---

**Next Document:** Artifact/Contract Specifications
