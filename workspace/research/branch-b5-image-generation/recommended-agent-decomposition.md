# Recommended Agent / Skill Decomposition for Branch 5

## Recommendation: expand B5 from 5 agents to 7 logical roles

The current 5-agent design is directionally correct but too compressed for reliable browser-video execution.

## Proposed roles

### 1. `portrait_generator`
Purpose:
- generate canonical portraits for recurring characters
- create consistency anchors for later scene generation / animation

Inputs:
- character bible
- entity match outputs
- account style guide

Outputs:
- portrait set
- canonical refs
- portrait metadata

### 2. `image_generation_router`  **(new)**
Purpose:
- decide the cheapest acceptable execution path
- separate local still generation from browser animation routing

Decides:
- ComfyUI vs browser platform
- still-only vs animate
- Freepik vs Higgsfield vs fallback
- quality tier, duration, aspect, motion mode

This should be a planning/routing micro-agent inside B5.

### 3. `ai_image_director`
Purpose:
- convert B3 visual intent into a generation brief
- define composition, lens feel, subject, era/style, action, lighting
- produce prompt package plus negative constraints / reference instructions

### 4. `image_generator`
Purpose:
- execute local still generation on ComfyUI / Flux / SDXL
- produce candidates and metadata

Should stay local-first for cost reasons.

### 5. `image_qa`
Purpose:
- score still images before any animation spend happens

Checks:
- composition compliance
- subject correctness
- visual clarity
- style match
- historical plausibility where relevant
- artifact detection

### 6. `image_animator`
Purpose:
- execute browser-based img2video jobs on approved stills
- interface with Freepik/Higgsfield/etc.

Important: this agent should be execution-only, not policy-setting.

### 7. `motion_qa`  **(new)**
Purpose:
- validate generated motion clips before sending them to B6

Checks:
- identity preservation
- temporal stability
- motion relevance to scene intent
- absence of grotesque warps/flicker
- camera move quality
- duration usefulness

## Optional eighth role if scale increases

### 8. `browser_session_operator` or platform-specific skill layer
If browser fragility becomes high, split browser execution into:
- `image_animator` = high-level job orchestration
- platform skill/adapter = low-level UI automation per provider

This is likely the right long-term design.

## Skill decomposition recommendation

Instead of putting all browser knowledge into one agent prompt, create reusable skills/adapters:

### Skill A — `comfyui-still-generation`
- run local workflows
- upload refs if needed
- capture output paths and metadata

### Skill B — `freepik-video-generator`
- login/session assumptions
- upload image/references
- choose model
- choose settings
- submit/download
- structured failure taxonomy

### Skill C — `higgsfield-motion`
- upload still
- choose prompt/camera preset
- export result
- capture preset metadata

### Skill D — `motion-qa-rubric`
- standard scoring schema for short AI clips
- pass/fail + reasons + retry guidance

## Suggested artifact schema

### `image_generation_request.json`
- scene_id
- asset_role
- account
- style guide version
- references
- prompt package
- target aspect
- quality tier
- needs_animation: true/false

### `image_generation_result.json`
- provider
- model
- local/remote path
- prompt hash
- cost estimate / credits if known
- QA score
- pass/fail

### `animation_job.json`
- source_image
- provider target
- target duration
- aspect
- motion prompt
- camera preset
- movement reference video (optional)
- budget ceiling

### `animation_result.json`
- clip path
- provider
- model
- elapsed time
- credits/cost if known
- motion_qa summary
- retry recommendation

## Operational policy recommendation

### Default policy
1. Generate still locally first
2. Run still QA
3. Animate only if:
   - scene value justifies motion
   - still passed QA strongly
   - budget threshold allows it
4. Motion QA before registry handoff

### Retry policy
- first retry: tweak prompt/settings in same platform
- second retry: switch model within same platform if available
- third retry: switch platform
- if still bad: fall back to static still + motion plan in B6/Remotion

## Why this decomposition is better

It keeps B5 aligned with the architecture’s core principle:
- editorial planning remains upstream
- B5 executes generation and animation efficiently
- browser complexity is isolated
- cost control becomes explicit
- QA exists for both still and motion outputs
