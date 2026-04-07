# Web findings — Branch 4 Asset Research

## 1) Relevant OpenClaw capability: browser automation exists, but should be selective
OpenClaw docs indicate a managed isolated browser profile with deterministic tab control, clicking, typing, snapshots, screenshots, PDFs, and optional multiple profiles.

Implication for B4:
- Browser automation is viable for asset retrieval workflows that require upload, login, or UI navigation.
- But API-first retrieval is still cheaper, simpler, and more scalable for archival/public-domain sources.
- Best use of browser automation in this department appears to be:
  - B5 `image_animator` flows (Freepik, Higgsfield, similar)
  - B4 fallback flows for sources with no usable API or where result quality via UI is much better than via API

## 2) Freepik is relevant, but more as B5/B4-hybrid than pure B4
Freepik publicly markets:
- text-to-video and image-to-video
- upload image start frame
- multiple underlying generation models (Google Veo, Kling, Runway, Seedance, Wan AI, PixVerse, MiniMax)
- API access for AI tools / creative assets

Interpretation:
- Freepik is strong as a **hybrid retrieval + transformation surface**.
- For pure B4 real-asset retrieval, it is less central than archival/public-domain sources.
- It matters when the system has a historically grounded image but wants motion added cheaply.

## 3) Higgsfield is relevant for cinematic animation control, not primary archival retrieval
Higgsfield emphasizes camera-control presets and cinematic motion controls (dolly, crane, crash zoom, whip pan, bullet time, etc.).

Interpretation:
- Higgsfield belongs mainly in B5 `image_animator` or a cross-branch finishing workflow.
- It is useful when a still image from B4 is good enough editorially but needs motion to feel premium.
- It is not itself a core real-footage source.

## 4) Best cheap scalable source strategy = API-first archival/public-domain stack
Most promising sources for cheap real assets:

### A. Library of Congress
- Has official JSON/YAML API surfaces.
- Strong for historical US photos, prints, manuscripts, some moving image material.
- Good metadata quality.
- Useful for WWII / history channels.

### B. Europeana
- Public APIs/search surfaces emphasize open-license filtering and media/technical metadata.
- Strong for European cultural heritage material.
- Valuable when US-centric archives miss the target.

### C. Wikimedia Commons
- MediaWiki API is open and self-documenting.
- Can expose metadata including license-related information.
- Very broad coverage, including images and some video/audio.
- But metadata quality and copyright certainty can be noisier than top-tier archives, so stronger judging is needed.

### D. Internet Archive / Prelinger-adjacent workflows
- Internet Archive exposes metadata and search APIs and is suitable for moving-image search/download workflows.
- Especially strong for old footage, ephemeral films, public-domain / quasi-public historical media.
- However, rights status can be mixed; do not assume all Prelinger-linked material is public domain.

## 5) Rights normalization is mandatory
Big research takeaway: source metadata is heterogeneous. "Found" is not the same as "safe to use".

B4 therefore needs a rights normalization layer mapping raw source metadata into internal buckets such as:
- `public_domain`
- `cc_by`
- `cc_by_sa`
- `cc0`
- `editorial_only`
- `licensed_stock`
- `unknown_review_required`
- `restricted_no_download`

## 6) Recommended retrieval policy by cost/quality
### Tier 1 — always try first
API/public-domain/open sources:
- Library of Congress
- Europeana
- Wikimedia Commons
- Internet Archive
- existing internal dataset connectors

### Tier 2 — use when Tier 1 is weak
Higher-noise but broad web retrieval / browser-assisted search:
- museum collections with permissive download pages
- public news archive pages
- government archives
- YouTube/Vimeo for reference discovery only unless rights are explicitly clear

### Tier 3 — paid / transformed fallback
- paid stock vendors if permitted by account constraints
- Freepik/API/browser hybrid for creative transformation
- B5 generation / animation when authentic real retrieval fails

## 7) Where browser automation is actually high leverage for B4
Good browser-automation candidates:
- collecting assets from archive UIs with filters not exposed cleanly in APIs
- handling multi-step download flows
- visual verification of page context / captions / date / provenance
- login-gated stock libraries, if ever approved later

Bad browser-automation candidates:
- high-volume generic archival search that APIs can do cheaper
- rights interpretation that still requires explicit metadata reasoning
- anything requiring brittle UI loops when an API exists

## 8) Recommended cheap scalable workflow pattern
For each scene intent:
1. Query internal dataset connectors and API-first public sources.
2. Aggregate top-N candidates with metadata.
3. Run asset judging/ranking.
4. If no candidate passes threshold:
   - try browser-assisted retrieval for narrow difficult cases
   - otherwise escalate to B5 for still generation or animation
5. Save approved candidates plus rights rationale into asset registry.
