# Context

## Two Operating Regimes
- **Reference-supported scenes** (~47%): Have S4 assets with semantic metadata. Design families that leverage these references.
- **Low/zero-reference scenes** (~53%): No S4 assets. Design atmospheric/creative families grounded in the video's world.

## Asset Family Types (V1)
- `hero` — primary visual anchor of the scene
- `support` — secondary visual elements that complement the hero
- `detail` — close-up or specific elements that add depth
- `atmospheric` — mood/environment without specific subject
- `transition` — visual bridges between scenes
- `fallback` — minimum viable visual if other families fail

## Grounding Levels
- `high` — tightly anchored to S4 references (identity, architecture)
- `medium` — reference-guided but allows creative variation
- `low` — creative freedom within the video's visual world
