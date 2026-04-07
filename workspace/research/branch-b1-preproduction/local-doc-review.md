# Local doc review — Branch 1 Pre-Production

## Docs read

1. `C:\Users\User-OEM\Desktop\content-factory\auto_content_factory\docs\03_PIPELINE_MAP.md`
2. `C:\Users\User-OEM\Desktop\content-factory\auto_content_factory\docs\04_BRANCH_ARCHITECTURE.md`
3. `C:\Users\User-OEM\Desktop\content-factory\auto_content_factory\docs\09_HIERARCHY_AND_STRUCTURE.md`
4. `C:\Users\User-OEM\Desktop\content-factory\auto_content_factory\docs\00_CONTEXT.md`
5. `C:\Users\User-OEM\Desktop\content-factory\auto_content_factory\docs\07_BRAINDUMP_OPENCLAW.md`
6. `C:\Users\User-OEM\Desktop\content-factory\auto_content_factory\docs\02_GPT_BRAINSTORM_ANALYSIS.md`
7. `C:\Users\User-OEM\Desktop\content-factory\auto_content_factory\docs\01_FRAMEWORK_RESEARCH.md`
8. `C:\Users\User-OEM\Desktop\content-factory\auto_content_factory\README.md`

## What these docs say about Branch 1

### Core scope
Branch 1 is explicitly defined as:
- `script -> scenes -> scene_bible`
- a planning branch, not a rendering/execution branch
- the producer of the central artifact that downstream branches consume

### Existing pipeline mapping
From `03_PIPELINE_MAP.md`:
- Script fetch from Google Sheet is deterministic
- Script cleaning is deterministic
- Scene division / screenplay is creative
- Scene division currently already exists in the old pipeline (`parallel_screenplay.py`, GPT-4.1-mini)
- The current system validates per-scene word count after scene splitting

Implication: B1 should not try to replace the existing deterministic plumbing first. It should sit on top of it and improve the creative/planning layer.

### Target branch architecture
From `04_BRANCH_ARCHITECTURE.md` and `09_HIERARCHY_AND_STRUCTURE.md`:
- B1 agents currently envisioned:
  - `script_fetcher`
  - `scene_director`
  - `scene_bible_builder`
- The shared artifact is `shared/scene_bible/`
- Branch managers coordinate agents; individual agents do one narrow job each
- Context isolation matters: each agent should only load local docs/prompts relevant to its own task

### Role of the scene bible
The docs repeatedly position `scene_bible` as the central artifact for the whole pipeline.
That means B1 is more important than a normal upstream step: it defines the semantic contract that B2/B3/B6 and QA will rely on.

### Key design principles already documented
From `02_GPT_BRAINSTORM_ANALYSIS.md`:
- Separate planning from execution
- Keep deterministic infrastructure as the ground truth layer
- Use persistent external state (`scene_bible`, `character_bible`, `asset_registry`)
- Creativity should happen in stages, not in one giant prompt
- Prefer comparative judgment over unconstrained invention

These principles fit B1 especially well.

## Practical conclusions for B1

1. **B1 should be artifact-first**
   The main output is not prose. It is a structured, versioned `scene_bible.json` plus a human-readable markdown summary.

2. **B1 should stay narrow**
   It should answer:
   - what are the scenes?
   - what is each scene trying to do narratively?
   - what must downstream branches know about each scene?

   It should not decide detailed image sourcing, music, animation, or rendering.

3. **B1 should preserve deterministic checks**
   Even if scene splitting is creative, validation should remain deterministic:
   - word count limits
   - ordering
   - coverage of full script
   - no dropped paragraphs
   - stable IDs

4. **B1 should produce reusable semantic fields**
   The docs imply downstream branches need more than “scene text”. Good B1 output should include narrative purpose, emotional tone, priority level, likely visual requirements, and continuity anchors.

5. **B1 is a strong candidate for cheap model routing**
   Most of the work is text decomposition and schema filling. That is cheaper than later multimodal branches.
