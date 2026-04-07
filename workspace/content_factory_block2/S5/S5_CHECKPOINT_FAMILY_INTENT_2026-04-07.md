# S5 Checkpoint — Family Intent Clarification

_Status: checkpoint note_  
_Date: 2026-04-07_  
_Owner: Tobias_

---

## 1. Why this checkpoint exists

During deeper discussion of S5 scene-kit design, an important weakness became clear:

- `family_type` alone is not sufficiently actionable
- categories like `hero`, `support`, `detail`, `atmospheric`, and `transition` are useful
- but they remain too vague for S6 if they are not paired with a more concrete mission

This checkpoint records the resulting clarification.

---

## 2. Core conclusion

Each asset family in S5 should be understood through the combination of:
- `family_type`
- `family_intent`

Where:
- `family_type` = the broad category of the family
- `family_intent` = the concrete mission of that family inside the scene kit

This became necessary because broad family labels alone do not tell S6 what kind of assets it must actually materialize.

---

## 3. Why this matters

Without `family_intent`, a family like `support` can become too vague.

Examples of ambiguity:
- support for what?
- support for whom?
- support of factual identity, institutional context, architecture, emotional tone, symbolic layer, or editorial progression?

The family must be concrete enough that S6 can generate the right assets before S7 ever touches the scene.

So the family grammar should not rely on broad type labels alone.

---

## 4. Correct formulation

The family should be read like this:

- `family_type` tells the system what broad class of family this is
- `family_intent` tells the system what this family must achieve for the scene

Examples:
- `family_type: hero`
  - `family_intent: identify the central political actor of the prohibition decision`

- `family_type: support`
  - `family_intent: provide institutional and decision-context visuals around the prohibition`

- `family_type: detail`
  - `family_intent: reinforce the gambling/casino reality being prohibited`

- `family_type: support`
  - `family_intent: establish Hotel Quitandinha as the real architectural object of the ambition`

- `family_type: atmospheric`
  - `family_intent: create the emotional and symbolic visual field of decay and instability`

---

## 5. Strategic implication

This clarification strengthens the S5→S6 boundary significantly.

It means S5 is not just naming vague buckets.
It is specifying concrete family missions that S6 can act on.

That preserves:
- factual grounding
- clarity of generation intent
- usefulness of the kit downstream

while still avoiding premature final composition choices.

---

## 6. Relationship to S7

This checkpoint does **not** change the core rule that:
- S5 does not choose the final composition of the scene
- S7 still resolves the final edit-level arrangement

What it changes is upstream clarity.

S5 now becomes more capable of defining the scene kit in a way that is:
- concrete enough for S6
- still open enough for S7

---

## 7. Summary

The key clarification is:

> `family_type` alone is too weak.  
> The real production-facing language of an S5 asset family is `family_type + family_intent`.

This should now be treated as a central design rule of the S5 scene-kit grammar.
