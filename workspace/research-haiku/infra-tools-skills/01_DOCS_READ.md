# Haiku Research: Docs Read

**Subagent:** haiku-infra-tools-skills  
**Date:** 2026-03-26  
**Focus:** OpenClaw infrastructure/tooling for Content Factory video-editing department

## Docs Read (In Priority Order)

### Core Infrastructure

1. **00_CONTEXT.md** (Content Factory context)
   - Pipeline: 3 blocks (Script → TTS → Image Gen → Video Render)
   - Current state: Automated but "rigid" — fixed prompts, no per-video creativity
   - API situation: Google GCP Service Accounts suspended (19-25 Mar 2026), migrated to key rotation + OpenRouter + local models
   - Key players: Lucca, Micha, João Gabriel, Cellibs
   - OpenClaw setup: Tobias (CEO agent) installed, GPT-5.4 Pro via OAuth, security hardened

2. **03_PIPELINE_MAP.md** (Full pipeline operations)
   - 20 creative decisions per video (candidate agent tasks)
   - ~50 deterministic/creative operations mapped
   - Identified gaps: scheduling, QA post-render, monitoring, intelligent upload, evolution

3. **05_MULTI_MACHINE_ARCHITECTURE.md** (Hardware/distribution)
   - Design: 1 Gateway (M1) + 5 Node Hosts (M2-M6)
   - M1 specs: Ryzen 9 5950X (16-core), 128GB RAM, RTX 4070 Super
   - Proposed: SSH tunnels or Tailscale between machines
   - Conclusion: M1 Gateway is lightweight enough to also run production

4. **09_HIERARCHY_AND_STRUCTURE.md** (Agent hierarchy)
   - 4-level pyramid: CEO (Tobias) → Production Manager → Branch Managers (B1-B10) → ~42 Individual Agents
   - Each level has isolated workspace (no nesting, communication via artifacts)
   - 10 branches: Pre-prod, Audio, Visual Plan, Asset Research, Image Gen, Scene Comp, Post-prod, Assembly/Render, QA, Monitoring
   - Incremental rollout: 2 agents → 5 → 12 → 43

5. **08_SECURITY_HARDENING.md** (Security config)
   - openclaw.json: `workspaceOnly: true`, exec `security: "allowlist"`, deny_paths for sensitive dirs
   - Gateway ALWAYS on 127.0.0.1 (never expose)
   - Zero third-party skills (ClawHub/npm disabled)
   - Deny list: gemini_api_keys/, .env, .ssh/, AppData/, .pem/.key files, machine_config.yaml

6. **07_BRAINDUMP_OPENCLAW.md** (High-level context)
   - Current goal: Transform rigid pipeline → autonomous creative agents
   - KMS system: Manages 90+ API keys, automatic rotation, cost tracking
   - Dataset system: Research real images from public archives
   - Multi-language support: PT, EN, ES, FR, IT, DE, more

7. **06_MODEL_STRATEGY.md** (LLM routing)
   - Main (Tobias): GPT-5.4 Pro via OAuth ($200/mo)
   - Sub-agents: GPT-nano/mini, Haiku, Sonnet, Flash Lite via OpenRouter/Anthropic API
   - Local models: Ollama for Qwen (cost-zero)
   - Image gen: ComfyUI local (SDXL/Flux)
   - Budget: ~$270-320/month total

8. **04_BRANCH_ARCHITECTURE.md** (Branch design)
   - One team, multiple clients (configs per account in accounts/ dir)
   - Scene Bible as central artifact (created by B1, read by all)
   - QA distributed (not post-render only)
   - Monitoring as independent branch (alerts, costs, errors)

## Key Constraints Extracted

### Storage & Coordination
- **Scene Bible** = central JSON per video (created by B1, consumed by all)
- **Asset Registry** = shared artifact tracking found/generated images
- **Character Bible** = shared knowlege base of recurring personas
- Shared folders: `shared/scene_bible/`, `shared/asset_registry/`, `shared/character_bible/`

### Multi-Machine Reality
- M2-M6 need SSH server + Python + ComfyUI (if GPU-equipped)
- M1 Gateway runs OpenClaw + coordinates via SSH dispatch
- No centralized database — all coordination via artifact files (JSON, markdown)
- Parallelization needed: image gen, asset research, QA checks

### Creative Direction
- Branches 3-7 are **planning/creative** (output = JSON specs)
- Branches 2,4,5,8 are **execution** (consume specs, produce assets)
- Branch 9 is **validation** (distributed throughout pipeline)
- Branch 10 is **monitoring** (no creative work, alerts + cost tracking)

### API Cost Control
- KMS already handles: key rotation, provider fallback, rate limiting, cost tracking
- New agents must respect: cost per video (~$5.55 for images on OpenRouter), circuit breakers
- Local models save cost (ComfyUI SDXL = $0/image vs Gemini paid)

## Not Read (Intentionally Skipped)

- KnowledgeBase/ (course content, Alex Finn lessons) — framework knowledge, not project-specific
- 01_FRAMEWORK_RESEARCH.md, 02_GPT_BRAINSTORM_ANALYSIS.md — high-level philosophies, not implementation details
- .pytest_cache/, README.md — not relevant to infra/tools

## Gaps in Current Docs (Research Opportunities)

1. **Git/GitHub workflow** — how are configs versioned? (accounts/, branch prompts)
2. **Browser automation** — how will image_animator (img2video) integrate? (Freepik/Higgsfield)
3. **Shared storage strategy** — Google Drive vs GitHub vs local workspace? How do M2-M6 access shared artifacts?
4. **Cron scheduling** — how are production runs triggered? (PM agent on schedule vs manual)
5. **Cost circuit breakers** — where are hard stops? ($500? $1000/day?)
6. **Monitoring/alerting** — Slack? Telegram? Dashboard?

---

**Next Step:** Recommendations for concrete tools/skills/integrations to address these gaps.
