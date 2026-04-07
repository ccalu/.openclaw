"""S4 Target Builder -- consolidates S3 compiled entities into S4 research targets.

Transforms raw S3 entities into consolidated, contextualized, auditable targets:
1. DETERMINISTIC: collect entities, normalize strings, detect obvious overlaps
2. LLM: semantic consolidation (merge, contextualize labels, classify searchability)
3. DETERMINISTIC: validate output, preserve provenance, enforce schema

Uses GPT-5.4-nano for the consolidation step. No entity is silently removed —
non-retrievable targets are preserved with handling_mode=skip_visual_retrieval.
"""
import json
import sys
from pathlib import Path

from openai import OpenAI

from artifact_io import read_json, write_json, write_markdown, utc_now
from paths import intake_path, sanitize_target_id
from schema_validator import validate_artifact_strict

# Entity type mapping: S3 entity_type -> S4 target_type
ENTITY_TYPE_MAP = {
    "person": "person_historical",
    "location": "location_historical",
    "environment": "environment_reference",
    "architectural_complex": "architectural_anchor",
    "interior_venue": "interior_space",
    "object": "object_artifact",
    "artifact": "object_artifact",
    "vehicle": "object_artifact",
    "prop": "object_artifact",
    "symbolic_event": "symbolic_sequence",
    "event": "event_reference",
    "symbolic_action": "symbolic_sequence",
    "atmospheric_phenomenon": "event_reference",
    "landscape_feature": "environment_reference",
    "interior_element": "interior_space",
    "gaming_object": "object_artifact",
    "building_material": "object_artifact",
    "architectural_element": "object_artifact",
}

RESEARCH_MODES_BY_TYPE = {
    "person_historical": ["factual_evidence", "visual_reference"],
    "location_historical": ["factual_evidence", "visual_reference"],
    "environment_reference": ["visual_reference", "stylistic_inspiration"],
    "architectural_anchor": ["factual_evidence", "visual_reference", "stylistic_inspiration"],
    "interior_space": ["visual_reference", "stylistic_inspiration"],
    "object_artifact": ["visual_reference", "factual_evidence"],
    "symbolic_sequence": ["stylistic_inspiration", "contextual_reference"],
    "event_reference": ["factual_evidence", "contextual_reference"],
}

PRIORITY_BY_TYPE = {
    "architectural_anchor": "critical",
    "person_historical": "high",
    "location_historical": "high",
    "interior_space": "high",
    "environment_reference": "medium",
    "object_artifact": "medium",
    "event_reference": "medium",
    "symbolic_sequence": "low",
}

MODEL = "gpt-5.4-nano"
OPENAI_API_KEY = "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"


# ---------------------------------------------------------------------------
# Phase 1: DETERMINISTIC — collect and normalize
# ---------------------------------------------------------------------------

def _collect_entities(compiled_data: dict) -> list:
    """Flatten all entity categories from compiled_entities into a single list."""
    ce = compiled_data.get("compiled_entities", {})
    entities = []

    for e in ce.get("human_subjects", []):
        entities.append({
            "entity_id": e.get("entity_id", ""),
            "entity_type": e.get("entity_type", "person"),
            "source_category": "human_subjects",
            "canonical_label": e.get("canonical_label", ""),
            "scene_ids": e.get("scene_ids", []),
            "visual_relevance_note": e.get("visual_relevance_note", ""),
        })

    for e in ce.get("environment_locations", []):
        etype = e.get("type", "environment")
        entities.append({
            "entity_id": e.get("location_id", e.get("entity_id", "")),
            "entity_type": etype,
            "source_category": "environment_locations",
            "canonical_label": e.get("name", e.get("canonical_label", "")),
            "scene_ids": e.get("scene_refs", e.get("scene_ids", [])),
            "visual_relevance_note": e.get("visual_relevance_note", ""),
        })

    for e in ce.get("object_artifacts", []):
        entities.append({
            "entity_id": e.get("entity_id", ""),
            "entity_type": e.get("entity_type", "object"),
            "source_category": "object_artifacts",
            "canonical_label": e.get("canonical_label", ""),
            "scene_ids": e.get("scene_ids", []),
            "visual_relevance_note": e.get("visual_relevance_note", ""),
        })

    for e in ce.get("symbolic_events", []):
        etype = e.get("type", "symbolic_event")
        entities.append({
            "entity_id": e.get("event_id", e.get("entity_id", "")),
            "entity_type": etype,
            "source_category": "symbolic_events",
            "canonical_label": e.get("name", e.get("canonical_label", "")),
            "scene_ids": e.get("scene_refs", e.get("scene_ids", [])),
            "visual_relevance_note": e.get("interpretation", e.get("visual_relevance_note", "")),
        })

    return entities


def _extract_video_context(compiled_entities_path: Path) -> dict:
    """Extract video context from directory name and S3 source package."""
    # Walk up from compiled_entities to find the video directory
    # compiled_entities = .../s3_visual_planning/compiled/compiled_entities.json
    video_dir = compiled_entities_path.parent.parent.parent.parent.parent
    video_dir_name = video_dir.name.replace("_", " ").replace("-", " — ") if video_dir.exists() else ""

    # Try to read S3 source package for scene snippets
    source_pkg_path = compiled_entities_path.parent.parent / "inputs" / "s3_source_package.json"
    scene_snippets = []
    if source_pkg_path.exists():
        source_pkg = read_json(source_pkg_path)
        for s in source_pkg.get("scenes", [])[:15]:
            scene_snippets.append(s.get("text", ""))

    return {
        "video_title": video_dir_name,
        "scene_snippets": scene_snippets,
    }


def _detect_obvious_overlaps(entities: list) -> list[tuple[int, int]]:
    """Deterministic pre-pass: detect entities with identical or near-identical labels."""
    overlaps = []
    for i in range(len(entities)):
        for j in range(i + 1, len(entities)):
            label_i = entities[i]["canonical_label"].lower().strip()
            label_j = entities[j]["canonical_label"].lower().strip()
            if label_i == label_j:
                overlaps.append((i, j))
    return overlaps


# ---------------------------------------------------------------------------
# Phase 2: LLM — semantic consolidation
# ---------------------------------------------------------------------------

def _consolidate_with_llm(entities: list, video_context: dict, usage_out: dict) -> list[dict]:
    """Use GPT-5.4-nano to consolidate entities into targets.

    Returns list of consolidated target groups with:
    - group_id, contextualized_label, source_entity_ids, merged_scene_ids,
      preferred_target_type, searchability, skip_reason, retrieval_hint
    """
    # Build compact entity list for the LLM
    entity_summaries = []
    for i, e in enumerate(entities):
        summary = {
            "idx": i,
            "entity_id": e["entity_id"],
            "label": e["canonical_label"],
            "type": e["entity_type"],
            "category": e["source_category"],
            "scenes": len(e["scene_ids"]),
            "note": e["visual_relevance_note"][:150] if e["visual_relevance_note"] else "",
        }
        entity_summaries.append(summary)

    # Build scene context
    scene_context = ""
    if video_context.get("scene_snippets"):
        snippets = video_context["scene_snippets"][:10]
        scene_context = "\n".join(f"  Scene {i+1}: {s[:120]}" for i, s in enumerate(snippets) if s)

    prompt = f"""You are a target consolidation engine for a documentary video asset research pipeline.

VIDEO CONTEXT:
  Title: {video_context.get('video_title', 'unknown')}
{f'  Script preview:{chr(10)}{scene_context}' if scene_context else ''}

ENTITIES FROM S3 (each extracted by a different operator — may overlap):
{json.dumps(entity_summaries, indent=2, ensure_ascii=False)}

YOUR JOB:
1. **MERGE** entities that refer to the same visual subject (e.g. "Hotel Quitandinha" appearing as location AND object → 1 target)
2. **CONTEXTUALIZE** each label so it's unambiguous for Google Image search (e.g. "Lago artificial" → "Lago artificial do Hotel Quitandinha, Petrópolis", "Cassino" → "Cassino do Hotel Quitandinha")
3. **CLASSIFY searchability**: can this target produce useful image search results?
   - "retrievable": concrete visual subject (person, building, place, object)
   - "retrievable_generic": not the specific thing but similar images exist (e.g. "marble corridors" — not THE hotel's but similar ones work)
   - "non_retrievable": purely abstract concept with no visual search equivalent (e.g. "O complexo como aposta nacional")

RULES:
- Every source entity_id MUST appear in exactly one group (no entity lost)
- Merging is only for entities that depict the SAME visual subject from different categories
- Do NOT merge entities that are merely related (e.g. "roulette wheel" and "casino chips" are related but distinct targets)
- The contextualized_label must work as a Google Images search anchor
- For non_retrievable targets, provide a clear skip_reason

OUTPUT FORMAT (JSON):
{{
  "groups": [
    {{
      "group_id": 1,
      "contextualized_label": "Hotel Quitandinha fachada Petrópolis",
      "source_entity_indices": [0, 5],
      "preferred_type": "architectural_anchor",
      "searchability": "retrievable",
      "skip_reason": null,
      "retrieval_hint": "Search for the specific building"
    }}
  ]
}}

Respond ONLY with valid JSON."""

    client = OpenAI(api_key=OPENAI_API_KEY)

    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_completion_tokens=4096,
            response_format={"type": "json_object"},
        )
        # Track usage
        if resp.usage:
            usage_out["input_tokens"] = usage_out.get("input_tokens", 0) + (resp.usage.prompt_tokens or 0)
            usage_out["output_tokens"] = usage_out.get("output_tokens", 0) + (resp.usage.completion_tokens or 0)
            usage_out["calls"] = usage_out.get("calls", 0) + 1

        result = json.loads(resp.choices[0].message.content)
        groups = result.get("groups", [])
        print(f"[target_builder] LLM consolidated {len(entities)} entities into {len(groups)} groups")
        return groups

    except Exception as e:
        print(f"[target_builder] LLM consolidation failed: {e}, falling back to 1:1 mapping")
        return []


# ---------------------------------------------------------------------------
# Phase 3: DETERMINISTIC — validate, build intake, preserve provenance
# ---------------------------------------------------------------------------

def _validate_consolidation(groups: list, entities: list) -> list[dict]:
    """Validate LLM output: ensure all entities are accounted for, no invalid indices."""
    seen_indices = set()
    valid_groups = []

    for g in groups:
        indices = g.get("source_entity_indices", [])
        # Validate indices
        valid_indices = [i for i in indices if isinstance(i, int) and 0 <= i < len(entities)]
        if not valid_indices:
            continue

        seen_indices.update(valid_indices)
        valid_groups.append({
            "contextualized_label": g.get("contextualized_label", ""),
            "source_entity_indices": valid_indices,
            "preferred_type": g.get("preferred_type", ""),
            "searchability": g.get("searchability", "retrievable"),
            "skip_reason": g.get("skip_reason"),
            "retrieval_hint": g.get("retrieval_hint", ""),
        })

    # Ensure every entity is represented — add orphans as individual groups
    all_indices = set(range(len(entities)))
    orphans = all_indices - seen_indices
    for idx in sorted(orphans):
        e = entities[idx]
        print(f"[target_builder] WARNING: entity {e['entity_id']} ({e['canonical_label']}) not in any LLM group, adding as solo target")
        valid_groups.append({
            "contextualized_label": e["canonical_label"],
            "source_entity_indices": [idx],
            "preferred_type": "",
            "searchability": "retrievable",
            "skip_reason": None,
            "retrieval_hint": "",
        })

    return valid_groups


def _map_target_type(entity_type: str) -> str:
    return ENTITY_TYPE_MAP.get(entity_type, "object_artifact")


def _pick_best_type(entities_in_group: list) -> str:
    """Pick the most specific target_type from a group of merged entities."""
    type_priority = [
        "architectural_anchor", "person_historical", "location_historical",
        "interior_space", "environment_reference", "object_artifact",
        "event_reference", "symbolic_sequence",
    ]
    mapped_types = [_map_target_type(e["entity_type"]) for e in entities_in_group]
    for t in type_priority:
        if t in mapped_types:
            return t
    return mapped_types[0] if mapped_types else "object_artifact"


def _research_needs(target_type: str, canonical_label: str) -> list:
    """Generate research needs based on target type."""
    if target_type == "architectural_anchor":
        return [
            f"Historical photographs of {canonical_label}",
            f"Architectural details and floor plans of {canonical_label}",
            f"Construction history and timeline of {canonical_label}",
            f"Modern reference photos showing current state of {canonical_label}",
        ]
    elif target_type == "person_historical":
        return [
            f"Historical portraits or photographs of {canonical_label}",
            f"Biographical context and era details for {canonical_label}",
        ]
    elif target_type in ("location_historical", "environment_reference"):
        return [
            f"Historical and modern photographs of {canonical_label}",
            f"Geographic and cultural context of {canonical_label}",
        ]
    elif target_type == "interior_space":
        return [
            f"Interior photographs of {canonical_label}",
            f"Architectural style and decorative details of {canonical_label}",
        ]
    elif target_type == "object_artifact":
        return [
            f"Reference images of {canonical_label}",
            f"Historical context and visual details of {canonical_label}",
        ]
    elif target_type in ("symbolic_sequence", "event_reference"):
        return [
            f"Visual references for {canonical_label}",
            f"Historical or cultural context of {canonical_label}",
        ]
    return [f"Visual references for {canonical_label}"]


def build_intake(
    compiled_entities_path: Path,
    sector_root: Path,
    job_id: str,
    video_id: str,
    account_id: str,
    language: str,
    *,
    filter_entity_id: str = "",
) -> Path:
    """Build S4 research intake with target consolidation.

    Phase 1 (deterministic): collect entities, normalize, detect overlaps
    Phase 2 (LLM): semantic consolidation, contextualization, searchability
    Phase 3 (deterministic): validate, build intake, preserve provenance
    """
    compiled = read_json(compiled_entities_path)
    entities = _collect_entities(compiled)

    if filter_entity_id:
        entities = [e for e in entities if e["entity_id"] == filter_entity_id]

    print(f"[target_builder] collected {len(entities)} entities from S3")

    # Phase 1: deterministic pre-analysis
    overlaps = _detect_obvious_overlaps(entities)
    if overlaps:
        labels = [f"{entities[i]['canonical_label']}={entities[j]['canonical_label']}" for i, j in overlaps]
        print(f"[target_builder] detected {len(overlaps)} exact label overlaps: {', '.join(labels)}")

    video_context = _extract_video_context(compiled_entities_path)

    # Phase 2: LLM consolidation
    usage = {}
    groups = _consolidate_with_llm(entities, video_context, usage)

    if not groups:
        # Fallback: 1:1 mapping (no consolidation)
        print("[target_builder] using fallback 1:1 mapping (no consolidation)")
        groups = [
            {
                "contextualized_label": e["canonical_label"],
                "source_entity_indices": [i],
                "preferred_type": "",
                "searchability": "retrievable",
                "skip_reason": None,
                "retrieval_hint": "",
            }
            for i, e in enumerate(entities)
        ]

    # Phase 3: deterministic validation
    groups = _validate_consolidation(groups, entities)

    # Build research targets
    research_targets = []
    skipped_targets = []
    all_scene_ids = set()
    target_counter = 0

    for group in groups:
        target_counter += 1
        tid = f"t{target_counter:03d}"
        indices = group["source_entity_indices"]
        group_entities = [entities[i] for i in indices]

        # Merge scene_ids from all source entities
        merged_scenes = []
        for e in group_entities:
            for sid in e.get("scene_ids", []):
                if sid not in merged_scenes:
                    merged_scenes.append(sid)
        all_scene_ids.update(merged_scenes)

        # Pick best type
        preferred = group.get("preferred_type", "")
        if preferred and preferred in PRIORITY_BY_TYPE:
            target_type = preferred
        else:
            target_type = _pick_best_type(group_entities)

        # Contextualized label
        label = group.get("contextualized_label", "")
        if not label:
            label = group_entities[0]["canonical_label"]

        # Source entity IDs and categories
        source_ids = [e["entity_id"] for e in group_entities]
        source_categories = list(set(e["source_category"] for e in group_entities))

        # Searchability
        searchability = group.get("searchability", "retrievable")
        handling_mode = "visual_retrieval"
        skip_reason = None
        priority = PRIORITY_BY_TYPE.get(target_type, "medium")

        if searchability == "non_retrievable":
            handling_mode = "skip_visual_retrieval"
            skip_reason = group.get("skip_reason", "abstract or non-depictable target")
            priority = "low"

        target = {
            "target_id": tid,
            "canonical_label": label,
            "target_type": target_type,
            "source_entity_ids": source_ids,
            "source_categories": source_categories,
            "scene_ids": merged_scenes,
            "research_modes": RESEARCH_MODES_BY_TYPE.get(target_type, ["visual_reference"]),
            "priority": priority,
            "searchability": searchability,
            "handling_mode": handling_mode,
            "skip_reason": skip_reason,
            "retrieval_hint": group.get("retrieval_hint", ""),
            "research_needs": _research_needs(target_type, label),
            "notes": "; ".join(e.get("visual_relevance_note", "") for e in group_entities if e.get("visual_relevance_note")),
        }

        research_targets.append(target)
        if searchability == "non_retrievable":
            skipped_targets.append(target)

    # Build scene index
    scene_index = []
    for sid in sorted(all_scene_ids):
        linked = [t["target_id"] for t in research_targets if sid in t["scene_ids"]]
        scene_index.append({
            "scene_id": sid,
            "linked_target_ids": linked,
            "notes": "",
        })

    # Stats
    active_targets = [t for t in research_targets if t["handling_mode"] != "skip_visual_retrieval"]
    merged_count = sum(1 for g in groups if len(g["source_entity_indices"]) > 1)

    intake_data = {
        "contract_version": "s4.research_intake.v1",
        "sector": "s4_asset_research",
        "metadata": {
            "job_id": job_id,
            "video_id": video_id,
            "account_id": account_id,
            "language": language,
            "generated_at": utc_now(),
            "generated_from": str(compiled_entities_path.resolve()),
        },
        "source_refs": {
            "compiled_entities_path": str(compiled_entities_path.resolve()),
        },
        "research_targets": research_targets,
        "scene_index": scene_index,
        "intake_notes": [
            f"Target consolidation: {len(entities)} entities -> {len(research_targets)} targets ({merged_count} merges, {len(skipped_targets)} skipped)",
            f"Active targets: {len(active_targets)}, Skipped: {len(skipped_targets)}",
            f"OpenAI usage: {usage.get('calls', 0)} calls, {usage.get('input_tokens', 0)} in / {usage.get('output_tokens', 0)} out",
        ],
        "warnings": [],
    }

    validate_artifact_strict(intake_data, "research_intake")

    out = intake_path(sector_root)
    write_json(out, intake_data)

    # Write report
    _write_report(
        sector_root, intake_data, research_targets, scene_index,
        entities, groups, skipped_targets, usage,
        job_id, video_id, account_id, language, merged_count,
    )

    print(f"[target_builder] wrote intake: {out}")
    print(f"[target_builder] {len(entities)} entities -> {len(active_targets)} active targets + {len(skipped_targets)} skipped ({merged_count} merges)")
    if usage:
        cost = (usage.get("input_tokens", 0) / 1e6 * 0.20) + (usage.get("output_tokens", 0) / 1e6 * 1.25)
        print(f"[target_builder] OpenAI usage: {usage.get('calls', 0)} calls, {usage.get('input_tokens', 0):,} in / {usage.get('output_tokens', 0):,} out, ${cost:.4f}")

    return out


def _write_report(
    sector_root, intake_data, research_targets, scene_index,
    entities, groups, skipped_targets, usage,
    job_id, video_id, account_id, language, merged_count,
):
    """Write markdown report with consolidation details."""
    report_path = sector_root / "intake" / "target_builder_report.md"
    lines = [
        "# S4 Target Builder Report — with Consolidation",
        "",
        f"- **Job**: {job_id}",
        f"- **Video**: {video_id}",
        f"- **Account**: {account_id}",
        f"- **Language**: {language}",
        f"- **Generated**: {intake_data['metadata']['generated_at']}",
        "",
        "## Consolidation Summary",
        "",
        f"- Entities from S3: {len(entities)}",
        f"- Targets after consolidation: {len(research_targets)}",
        f"- Active (will search): {len(research_targets) - len(skipped_targets)}",
        f"- Skipped (non-retrievable): {len(skipped_targets)}",
        f"- Merges performed: {merged_count}",
        "",
        "## Active Targets",
        "",
        "| ID | Label | Type | Sources | Scenes | Priority | Searchability |",
        "|---|---|---|---|---|---|---|",
    ]

    for t in research_targets:
        if t["handling_mode"] != "skip_visual_retrieval":
            lines.append(
                f"| {t['target_id']} | {t['canonical_label']} | {t['target_type']} "
                f"| {','.join(t['source_entity_ids'])} | {len(t['scene_ids'])} "
                f"| {t['priority']} | {t['searchability']} |"
            )

    if skipped_targets:
        lines.extend(["", "## Skipped Targets (non-retrievable)", ""])
        lines.append("| ID | Label | Sources | Skip Reason |")
        lines.append("|---|---|---|---|")
        for t in skipped_targets:
            lines.append(
                f"| {t['target_id']} | {t['canonical_label']} "
                f"| {','.join(t['source_entity_ids'])} | {t['skip_reason']} |"
            )

    lines.extend(["", f"## Scenes ({len(scene_index)})", ""])
    for s in scene_index[:20]:
        lines.append(f"- {s['scene_id']}: targets {s['linked_target_ids']}")
    if len(scene_index) > 20:
        lines.append(f"- ... and {len(scene_index) - 20} more scenes")

    write_markdown(report_path, "\n".join(lines))


def main():
    if len(sys.argv) != 7:
        raise SystemExit(
            "usage: target_builder.py <compiled_entities_path> <sector_root> "
            "<job_id> <video_id> <account_id> <language>"
        )
    build_intake(
        compiled_entities_path=Path(sys.argv[1]),
        sector_root=Path(sys.argv[2]),
        job_id=sys.argv[3],
        video_id=sys.argv[4],
        account_id=sys.argv[5],
        language=sys.argv[6],
    )


if __name__ == "__main__":
    main()
