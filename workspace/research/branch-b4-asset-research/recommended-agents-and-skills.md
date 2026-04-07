# Recommended agents and skills — Branch 4 Asset Research

## Recommended branch-manager view of B4
Current 5-agent idea is directionally right, but for scalable retrieval B4 will likely need either internal sub-steps or extra helper skills.

## Keep the visible B4 agents
- `people_finder`
- `location_finder`
- `event_object_finder`
- `video_finder`
- `asset_judge`

## Add internal helper capabilities (as skills or hidden helpers)

### 1. `query_normalizer` skill
Purpose:
- Convert Branch 3 visual plan into source-specific search packets.

Input example:
- person name
- aliases
- date range
- geography
- event
- desired medium (`photo`, `footage`, `document`)
- must-have authenticity constraints

Output example:
- normalized keywords
- multilingual variants
- negative terms
- source routing hints
- expected license thresholds

Why it matters:
Without this, each finder agent duplicates search logic and becomes inconsistent.

### 2. `archive-search` skill
Purpose:
- Unified API-first search adapter for archival/public-domain sources.

Connectors to prioritize:
- existing internal dataset system
- Library of Congress
- Europeana
- Wikimedia Commons
- Internet Archive
- Smithsonian if available internally later

Why it matters:
One skill can hide source quirks and return a normalized candidate schema.

### 3. `rights-normalizer` skill
Purpose:
- Map heterogeneous license strings/fields into internal rights categories.

Why it matters:
This is core infra, not agent prompt logic.

### 4. `asset-deduper` skill
Purpose:
- Detect duplicate files / near-duplicates across archives and mirrored uploads.

Why it matters:
The same image often appears in multiple archives with different metadata quality.

### 5. `browser-retrieval` skill
Purpose:
- Controlled browser automation for archive sites or stock surfaces with weak APIs.

Suggested uses:
- interactive filtering
- reveal/download original file link
- capture provenance screenshot
- export citation metadata

Important constraint:
Use sparingly; only after API path underperforms.

### 6. `asset-proof-pack` skill
Purpose:
- For each approved asset, save machine-readable proof package:
  - source page URL
  - license snippet
  - provenance fields
  - snapshot/screenshot references
  - retrieval timestamp

Why it matters:
This becomes future QA/legal infrastructure.

## Finder agent recommendations

### `people_finder`
Best for:
- historical figures
- portraits
- press photos
- age/era matching

Should prioritize:
- authority metadata
- alias matching
- date consistency
- face count / prominence

### `location_finder`
Best for:
- city, battlefield, building, landmark, street, region

Should prioritize:
- geo and date matching
- wide vs detail shot classification
- whether the location visually matches the intended scene era

### `event_object_finder`
Best for:
- newspapers, maps, vehicles, weapons, uniforms, letters, posters, artifacts

Should prioritize:
- object specificity
- contextual captions
- close-up vs wide documentary utility

### `video_finder`
Best for:
- archival footage
- documentary b-roll
- public domain motion assets

Should prioritize:
- shot usability (stability, duration, visible subject)
- downloadable derivatives
- known rights status
- segmentability into clips

### `asset_judge`
Should not just rank by beauty.
It should score at least:
- relevance to scene intent
- authenticity / historical plausibility
- legal clarity
- technical usability for edit
- uniqueness / non-redundancy

## Proposed routing logic
- If intent is person-centric and identity matters -> `people_finder`
- If intent is place-centric -> `location_finder`
- If intent is artifact/event-centric -> `event_object_finder`
- If motion is explicitly desired and real footage is preferred -> `video_finder`
- All outputs must pass through `asset_judge`

## Concrete skills that look worth creating
1. `loc-archive-search`
2. `europeana-search`
3. `wikimedia-commons-search`
4. `internet-archive-footage`
5. `rights-normalizer`
6. `archive-browser-retrieval`
7. `asset-proof-pack`
8. `asset-deduper`

## Best systems recommendation
The cheap scalable design is:
- **API-first retrieval stack** for B4
- **browser-assisted exceptions** for hard cases
- **B5 animation/generation handoff** when real assets are insufficient
- **proof-pack + rights normalization** as permanent infrastructure

This avoids overusing expensive brittle browser loops while still leaving room for premium workflows.
