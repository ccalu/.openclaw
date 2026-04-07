# Final Report — Branch 5 (Image Generation + img2video/browser workflows)

## Executive summary

The local architecture is already pointing in the right direction: Branch 5 should be a **hybrid execution branch** that combines:
- **local still-image generation** via ComfyUI/Flux/SDXL
- **browser-mediated motion generation** via web platforms such as Freepik and Higgsfield

The strongest practical conclusion is:
- **do not use browser tools to replace local still generation**
- **use browser platforms mainly as the motion layer on top of approved stills**

## Most important findings

1. **B5 should be treated as two surfaces, not one**
   - still image generation
   - image-to-video animation

2. **Freepik is the best first browser target**
   - one login surface
   - many underlying video models behind one UI/credit system
   - explicit support for image references, prompt-based video generation, and motion-reference workflows

3. **Higgsfield is a strong second browser target**
   - especially valuable for cinematic camera-move presets and stylized motion
   - likely best for higher-value shots where movement quality matters more than lowest cost

4. **OpenClaw’s browser/node architecture fits this well**
   - browser automation can run on dedicated node hosts
   - isolated browser profiles reduce risk and operational mess
   - this is better than coupling browser work to the main gateway/operator environment

5. **Current B5 spec is missing routing + motion QA**
   - there is no explicit internal router for local vs browser vs provider choice
   - there is no explicit `motion_qa` role, even though video outputs have distinct failure modes

## Recommended B5 structure

Keep the existing spirit, but evolve B5 toward:
- `portrait_generator`
- `image_generation_router` **(new)**
- `ai_image_director`
- `image_generator`
- `image_qa`
- `image_animator`
- `motion_qa` **(new)**

## Recommended platform strategy

### Default cheap path
1. Generate still locally in ComfyUI
2. QA the still
3. Animate only selected scenes
4. Use **Freepik** as default browser animation layer
5. Use **Higgsfield** selectively for cinematic shots
6. If motion fails or is too expensive, fall back to static still + motion in composition/post

### Why this is strong
It preserves the cost advantage of local generation while capturing the creative upside of browser img2video tools.

## Relevant implementation implications

- B5 likely needs dedicated artifact schemas for generation requests/results and animation jobs/results
- browser automation should run on dedicated node/browser lanes with isolated profiles
- provider choice should be policy-driven, not hidden inside one giant prompt
- spend guards and retry ladders should be explicit

## Files created in this folder

1. `README.md`
2. `b5-architecture-notes.md`
3. `browser-platform-research.md`
4. `recommended-agent-decomposition.md`
5. `sources.md`
6. `final-report.md`
