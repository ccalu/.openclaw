# B5 Architecture Notes from Local Docs

## What the local architecture already says

Branch 5 is explicitly defined as:
- **Image Generation**
- responsibility: **generate AI images + animate approved images via browser (img2video)**
- type: **execution branch**

Current proposed B5 agents in the docs:
1. `portrait_generator` — character portraits
2. `ai_image_director` — generation brief construction
3. `image_generator` — ComfyUI SDXL/Flux static generation
4. `image_qa` — image quality verification
5. `image_animator` — animate approved images via browser (Freepik, Higgsfield, etc.)

## Position in the global pipeline

B5 sits after:
- B1 Pre-Production
- B2 Audio
- B3 Visual Planning

B5 receives planning intent from **B3 Visual Planning**. This matters because B5 should not decide the whole editorial strategy by itself; it should execute an already selected visual direction.

B5 outputs then feed:
- B6 Scene Composition
- later B7/B8 downstream

## Architectural implications

### 1. B5 is not just “prompt -> image”
The local docs imply two distinct execution surfaces inside B5:
- **local deterministic/local-GPU generation** via ComfyUI
- **browser-mediated remote generation/animation** via web platforms

That means B5 is operationally hybrid:
- local infra path for cheap static generation
- browser SaaS path for motion generation and specialty models

### 2. Static and motion should be separated
The current docs include only one `image_animator`, but the actual workload is likely two-step:
- create/select approved still image
- convert to motion clip using the right platform/model

This suggests animation should not be a thin afterthought. It is a distinct execution surface with different costs, failure modes, and tooling.

### 3. B5 depends on shared artifacts
Based on the architecture docs, B5 should read/write structured artifacts such as:
- `scene_bible`
- asset strategy / visual plan
- generated asset registry
- reusable character portraits / consistency references

### 4. B5 must coordinate with B4 rather than replace it
The overall architecture separates:
- **B4 Asset Research** = real photos / real footage
- **B5 Image Generation** = synthetic stills + synthetic motion

This is good and should remain. It prevents B5 from swallowing all visual tasks and keeps the decision boundary clear:
- B3 decides what kind of asset is needed
- B4 supplies real assets when best
- B5 supplies synthetic assets when best

### 5. B5 is cost-sensitive by design
Local docs already point toward:
- ComfyUI local for zero-marginal-cost stills
- browser platforms for img2video / web video tools

So B5 should be optimized for **routing**:
- cheapest acceptable path first
- expensive browser video only when motion adds enough value

## Tensions / gaps in current docs

### Gap A — no explicit router inside B5
The docs name agents, but not the routing logic that decides:
- local ComfyUI vs web platform
- Freepik vs Higgsfield vs other browser providers
- still-only vs animate
- portrait workflow vs scene image workflow

### Gap B — QA stops too early
`image_qa` is named, but motion QA is not explicit. Browser img2video outputs have separate failure modes:
- face drift
n- identity loss
- bad camera motion
- temporal warping
- lip-sync artifacts when motion-reference modes are used
- prompt non-compliance

### Gap C — browser state/account handling is implicit, not designed
If B5 relies on web platforms, then session persistence, profiles, rate control, retries, and account segregation become first-class concerns.

### Gap D — no explicit artifact schema for motion jobs
B5 likely needs at least:
- `image_generation_request.json`
- `image_generation_result.json`
- `animation_job.json`
- `animation_result.json`
- QA reports with pass/fail + reasons

## Bottom line from local docs

The architecture already correctly recognizes that modern AI editing quality requires **both** local still generation and **browser-based image animation/video models**. The main missing piece is not conceptual — it is operational decomposition:
- routing
- browser automation surface
- motion QA
- artifact schemas
- failure recovery
