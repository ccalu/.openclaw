# External patterns relevant to org design

## 1) Supervisor/worker is the right backbone

Across Anthropic, OpenAI, and LangChain material, the recurring production-safe pattern is hierarchical orchestration:
- one lead agent owns planning and final synthesis
- specialized subagents handle bounded subtasks
- subagents run in parallel where independence exists

Why this fits Content Factory:
- video production has clear stage gates and artefacts
- many subtasks are naturally specialist and parallelizable
- creative control should stay concentrated at upper layers while lower layers execute bounded work

## 2) Context engineering matters more than adding more agents

Strong consensus across sources:
- agent quality depends heavily on what each agent can see
- too many tools/prompts in one context reduces routing quality
- subagents save tokens and improve decision quality by narrowing context

Implication:
- keep Tobias strategic only
- keep PM focused on queue/priorities/dependencies
- keep each Branch Manager focused on one branch contract
- keep specialists blind to the broader org

## 3) Mix LLM routing with deterministic code gates

Best-practice pattern:
- use LLMs for ambiguous planning, classification, creative judgment
- use deterministic code for state transitions, schemas, validation, retries, and stage gating

Implication for this org:
- PM/BMs can use LLM judgment to choose paths
- but job state should still move via explicit statuses like `queued -> running -> blocked -> passed -> failed`
- Branch 8 and parts of QA should be heavily deterministic

## 4) Cheap-model-first cascade is standard

External routing guidance consistently recommends a cascade:
- smallest/cheapest model first for parsing, routing, formatting, extraction
- escalate only on ambiguity, low confidence, or failed quality checks

Implication:
- most level-4 workers should default to cheap models or local models
- Branch Managers should escalate selectively for creative or high-stakes decisions
- Tobias should rarely be used as a worker model

## 5) Parallel breadth beats sequential monoliths for research/search-style tasks

Anthropic specifically reports gains from parallel subagents with separate context windows.

Implication for editing org:
- asset research should parallelize by source/type
- QA can parallelize across modalities (audio/visual/editorial/technical)
- post-production planning can split into music/SFX/lettering/animation and merge later

## 6) Shared memory should be artefact-based, not chat-based

Common pattern:
- workers should exchange structured artefacts, not long conversational history
- managers synthesize and compress

Implication:
- branch inputs/outputs should be JSON or tightly-scoped markdown contracts
- avoid passing entire conversation logs downstream
- maintain one canonical artefact per stage
