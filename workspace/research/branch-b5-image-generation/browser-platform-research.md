# Browser Platform Research — Freepik, Higgsfield, and adjacent img2video options

## Key finding

For the Content Factory use case, browser-first platforms are most useful in B5 for **motion generation from approved stills**, not for replacing the full local still-image stack.

Best framing:
- **local ComfyUI** = cheap still generation backbone
- **browser platforms** = motion layer, specialty models, and fallback capacity

## Freepik

### Why it matters
Freepik is especially relevant because it acts as a **browser meta-platform** with many underlying video models exposed behind one UI and one credit system.

### What the docs/search results indicate
From Freepik docs/help:
- AI Video Generator can generate from text or visual references
- reference mode supports uploading image(s), start/end frames, or reference videos depending on the model
- there is a quick **1-click video** path and a more configurable editor path
- templates exist, which may help standardize repeatable flows
- credit costs vary heavily by model, duration, and resolution
- some plans advertise broad/unlimited generation on selected models, but exact coverage must be verified account-by-account at deployment time

### Strategic advantage for B5
Freepik is likely the strongest **first browser target** because it provides:
- one login surface
- multiple vendor models behind one platform
- image-to-video and motion-reference modes
- relatively fast experimentation without building separate automations per provider first

### Operational implications
A single OpenClaw browser automation layer could:
- upload approved image
- select target model
- set duration / resolution / aspect
- add prompt
- optionally add movement reference video
- submit job
- poll page state
- download result
- register clip metadata

### Relevant surfaced models on Freepik
Freepik help/docs surfaced support for models such as:
- Google Veo variants
- Kling variants including motion control
- MiniMax / Hailuo variants
- Runway variants
- Sora variants
- Wan variants including **Wan 2.2 Animate Move**
- others

This is strategically important: one browser integration may expose many generation backends.

### Important caution
Freepik credit pricing is dynamic and model-specific. Research data confirms broad ranges rather than a stable flat cost. B5 should treat Freepik as:
- operationally convenient
- commercially flexible
- but cost-variable

So B5 needs spend guards and model routing rules.

## Higgsfield

### Why it matters
Higgsfield appears differentiated by **camera-motion expressiveness** and an interface built around cinematic motion presets.

### What surfaced in research
Search/fetch results indicate:
- image upload + prompt based animation
- support for cinematic camera controls/presets
- many predefined moves: crash zoom, crane, arc, dolly, whip pan, hyperlapse, hero cam, etc.
- positioned as an all-in-one image/video generation environment

### Strategic advantage for B5
Higgsfield seems valuable when the job is not just “make image move” but specifically:
- add cinematic camera grammar
- create stylized motion from a still
- increase perceived editorial sophistication cheaply

This makes Higgsfield a likely **premium motion path** for scenes where motion design matters more than strict factual realism.

### Main limitation
The accessible fetched pricing/details were weaker than Freepik’s public docs. So current confidence is higher on product positioning than on exact cost structure.

## Adjacent platforms worth keeping as future adapters

These appeared repeatedly in search results and Freepik model listings:
- **Kling** — commonly seen as cost-efficient / strong value for image-to-video and motion control
- **Hailuo / MiniMax** — often positioned as low-cost motion generation
- **Runway** — strong quality, often costlier, useful as premium fallback
- **Wan / Wan Animate Move** — relevant for image + motion-reference workflows
- **Sora** — useful benchmark / premium option, likely not the cheap default

## Recommended browser-platform strategy for B5

### Tier 1 — first integrations
1. **Freepik**
   - best initial browser target
   - broad model access through one login/UI
   - most useful for pragmatic multi-model experimentation
2. **Higgsfield**
   - best second browser target
   - likely strongest for cinematic movement presets and creative motion control

### Tier 2 — model-specific direct adapters later
Only build separate direct automations later if data proves clear ROI, e.g.:
- Kling direct
- Runway direct
- Hailuo direct

Otherwise Freepik may already cover much of the needed surface.

## OpenClaw browser implications

OpenClaw docs indicate:
- the agent can control an isolated managed browser profile
- browser actions can be proxied to a **node host** on the machine that has the browser
- dedicated browser profiles can isolate automation from personal browsing
- remote gateway + node topology is a natural fit for browser automation workloads on other machines

### Implication for Content Factory
B5 browser automation should likely not depend on Tobias/main-agent machine state. Better design:
- run browser sessions on designated node host(s)
- each node keeps dedicated automation browser profile(s)
- gateway routes browser work to those nodes
- credentials stay isolated to the browser profile, not mixed with personal browsing

### Why this matters
Browser img2video work is fragile compared with local ComfyUI:
- login state matters
- CAPTCHAs / UI drift can happen
- downloads must be handled reliably
- concurrent jobs can interfere if sharing one profile

Therefore a **remote browser node** per automation lane is cleaner than ad hoc local browsing.

## Cheap pipeline conclusion

For a cheap-but-powerful B5 stack:
- Use **ComfyUI local** for the still frame whenever possible
- Use **Freepik browser workflow** as the default multi-model animation layer
- Use **Higgsfield** selectively for high-value cinematic motion shots
- Reserve more expensive direct tools only as fallback or for premium scenes
