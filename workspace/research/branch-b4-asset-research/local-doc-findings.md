# Local doc findings — Branch 4 Asset Research

## Docs read
- `README.md`
- `docs/00_CONTEXT.md`
- `docs/01_FRAMEWORK_RESEARCH.md`
- `docs/04_BRANCH_ARCHITECTURE.md`
- `docs/07_BRAINDUMP_OPENCLAW.md`
- `docs/09_HIERARCHY_AND_STRUCTURE.md`

## What the current architecture already says

### Role of Branch 4
Branch 4 is explicitly the execution branch responsible for **finding real images and real video** after Branch 3 has decided what should be shown.

Key implication: B4 should **not invent visual strategy**. It should execute a visual plan and return candidates plus evidence/metadata.

### Inputs / outputs implied by the docs
- Upstream input: `visual_plan.json` from Branch 3
- Downstream output: `asset_candidates.json`
- Shared state touched: likely `shared/asset_registry/`

That suggests B4 should behave like a retrieval + ranking + rights-checking layer.

### Existing envisioned B4 agents
From `04_BRANCH_ARCHITECTURE.md` and `09_HIERARCHY_AND_STRUCTURE.md`:
- `people_finder` — real photos of people
- `location_finder` — real photos/videos of places
- `event_object_finder` — events, objects, documents
- `video_finder` — real footage, b-roll, historical footage
- `asset_judge` — scores relevance, quality, copyright

### Important design clues from the local docs
1. **Plan-before-execute**
   The docs explicitly state visual planning must happen before asset research. So B4 should receive structured search intents, not raw scripts.

2. **Historical / documentary bias**
   The current business context includes WWII / dark history style channels, and the current dataset system already integrates:
   - Library of Congress
   - Europeana
   - Smithsonian
   - Wikimedia

   So B4 should be designed first for documentary-grade retrieval, not generic stock-first retrieval.

3. **Mixed real + AI stack**
   The architecture separates:
   - B4 = find real assets
   - B5 = generate/animate AI assets

   This is good and should be preserved. B4 should also emit a confidence signal indicating when retrieval failed and escalation to B5 is justified.

4. **Browser automation is already anticipated elsewhere**
   Local docs mention testing browser automation for img2video and specifically cite Freepik/Higgsfield on the B5 side. For B4, browser automation is probably useful only for sources with weak APIs, login walls, or high-value manual-like retrieval flows.

## Architectural inference for B4
B4 should probably be split conceptually into 4 layers:
1. **Intent normalization** — convert scene-level search request into typed search packets
2. **Source retrieval** — query APIs / web sources / browser flows
3. **Asset adjudication** — relevance + authenticity + rights + technical utility
4. **Registry + handoff** — persist approved candidates and route either to composition or to fallback generation

## Recommended data contract direction
Each asset candidate should carry at least:
- `scene_id`
- `search_intent_id`
- `asset_type` (`image`, `video`, `document_scan`, etc.)
- `subject_type` (`person`, `location`, `event`, `object`)
- `source_name`
- `source_url`
- `preview_url`
- `download_url` if available
- `license_label`
- `rights_status` (`public_domain`, `cc`, `editorial_only`, `unknown`, `paid_stock`, etc.)
- `creator`
- `date`
- `geo`
- `relevance_score`
- `quality_score`
- `authenticity_score`
- `usability_score`
- `risk_flags`
- `reason_selected`

## Main local conclusion
The local docs already define the skeleton of B4 correctly. The missing piece is the **retrieval strategy stack**: which sources are API-first, which are browser-assisted, how licensing is normalized, and how B4 cheaply decides “good enough real asset found” vs “escalate to B5 or hybrid workflow”.
