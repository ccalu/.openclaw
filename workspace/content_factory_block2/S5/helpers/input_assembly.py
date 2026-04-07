"""S5 Input Assembly — build per-scene direction input packages.

Reads S3 source package, compiled entities, S4 research intake, and
S4 reference-ready asset pool. For each scene, assembles a normalized
input package combining deterministic linkage with LLM-derived summaries.

Usage:
    python input_assembly.py <source_package> <compiled_entities> <research_intake> <asset_pool> <sector_root> <job_id>
"""
import asyncio
import json
import sys
from pathlib import Path

from artifact_io import read_json, write_json, utc_now
from llm_client import create_client, call_llm, UsageTracker
from paths import scene_input_package_path, usage_path
from schema_validator import validate_artifact_strict

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

BATCH_SIZE = 5  # scenes per LLM call for summary derivation
ALLOWED_GENERATION_MODES = [
    "reference_guided_generation",
    "regeneration_from_reference",
    "from_scratch_generation",
    "multi_reference_synthesis",
]


# ---------------------------------------------------------------------------
# Upstream loaders
# ---------------------------------------------------------------------------

def _build_scene_index_lookup(research_intake: dict) -> dict[str, list[str]]:
    """Build scene_id -> linked_target_ids lookup from scene_index list."""
    lookup = {}
    for entry in research_intake.get("scene_index", []):
        sid = entry.get("scene_id", "")
        tids = entry.get("linked_target_ids", [])
        if sid:
            lookup[sid] = tids
    return lookup


def _build_entity_lookup(compiled_entities: dict) -> dict[str, list[dict]]:
    """Build scene_id -> [entity_info] lookup from compiled entities."""
    lookup: dict[str, list[dict]] = {}
    categories = compiled_entities.get("compiled_entities", {})
    for cat_name, entities in categories.items():
        for entity in entities:
            scene_ids = entity.get("scene_ids", [])
            info = {
                "entity_id": entity.get("entity_id") or entity.get("location_id") or entity.get("event_id", ""),
                "entity_type": entity.get("entity_type") or entity.get("type", cat_name),
                "canonical_label": entity.get("canonical_label") or entity.get("name", ""),
                "category": cat_name,
            }
            for sid in scene_ids:
                lookup.setdefault(sid, []).append(info)
    return lookup


def _build_asset_lookup(asset_pool: dict) -> dict[str, dict]:
    """Build asset_id -> full asset object lookup."""
    return {a["asset_id"]: a for a in asset_pool.get("assets", [])}


def _build_target_asset_index(asset_pool: dict) -> dict[str, list[str]]:
    """Build target_id -> [asset_id] lookup from grouped_views.by_target."""
    return asset_pool.get("grouped_views", {}).get("by_target", {})


# ---------------------------------------------------------------------------
# Deterministic assembly per scene
# ---------------------------------------------------------------------------

def _assemble_scene_deterministic(
    scene: dict,
    idx: int,
    entity_lookup: dict[str, list[dict]],
    scene_index_lookup: dict[str, list[str]],
    target_asset_index: dict[str, list[str]],
    asset_lookup: dict[str, dict],
) -> dict:
    """Assemble deterministic fields for a single scene."""
    sid = scene["scene_id"]
    scene_number = int(scene.get("scene_number", idx + 1))

    # Semantic grounding from S3 entities
    entities = entity_lookup.get(sid, [])
    factual_anchors = [e["canonical_label"] for e in entities if e["canonical_label"]]
    symbolic_anchors = [
        e["canonical_label"] for e in entities
        if e.get("category") == "symbolic_events"
    ]

    # Reference layer from S4
    linked_target_ids = scene_index_lookup.get(sid, [])
    ref_assets = []
    for tid in linked_target_ids:
        asset_ids = target_asset_index.get(tid, [])
        for aid in asset_ids:
            asset = asset_lookup.get(aid)
            if asset and sid in asset.get("scene_relevance", []):
                ref_assets.append({
                    "asset_id": asset["asset_id"],
                    "source_target_id": asset["source_target_id"],
                    "source_target_label": asset.get("source_target_label", ""),
                    "filepath": asset.get("filepath", ""),
                    "reference_value": asset.get("reference_value", []),
                    "preserve_if_used": asset.get("preserve_if_used", []),
                    "depiction_type": asset.get("depiction_type", ""),
                    "relevance": asset.get("relevance", 0),
                    "quality": asset.get("quality", 0),
                })

    # Motion policy: first 10 scenes only
    motion_allowed = scene_number <= 10

    return {
        "package_version": "v1",
        "scene_id": sid,
        "scene_core": {
            "scene_id": sid,
            "scene_text": scene.get("text", ""),
            "scene_number": scene_number,
            "sequence_position": idx + 1,
            "scene_summary": "",  # filled by LLM
            "narrative_function": "",  # filled by LLM
        },
        "semantic_grounding": {
            "scene_entities": entities,
            "factual_anchors": factual_anchors,
            "symbolic_anchors": symbolic_anchors,
        },
        "reference_layer": {
            "relevant_targets": linked_target_ids,
            "reference_ready_assets": ref_assets,
        },
        "policy": {
            "motion_allowed": motion_allowed,
            "allowed_generation_modes": ALLOWED_GENERATION_MODES,
        },
    }


# ---------------------------------------------------------------------------
# LLM-derived fields (scene_summary + narrative_function)
# ---------------------------------------------------------------------------

async def _derive_semantic_fields(
    packages: list[dict],
    entity_lookup: dict[str, list[dict]],
    client,
    tracker: UsageTracker,
) -> None:
    """Derive scene_summary and narrative_function for all packages via batched LLM calls."""
    prompt_path = Path(__file__).parent.parent / "prompts" / "input_assembly_scene_normalization.txt"
    system_prompt = prompt_path.read_text(encoding="utf-8")

    # Build batches of BATCH_SIZE scenes
    batches = []
    for i in range(0, len(packages), BATCH_SIZE):
        batches.append(packages[i:i + BATCH_SIZE])

    print(f"[input_assembly] deriving summaries: {len(packages)} scenes in {len(batches)} batches")

    async def _process_batch(batch):
        scenes_payload = []
        for pkg in batch:
            sid = pkg["scene_id"]
            entities = entity_lookup.get(sid, [])
            entity_labels = [e["canonical_label"] for e in entities if e["canonical_label"]]
            scenes_payload.append({
                "scene_id": sid,
                "scene_number": pkg["scene_core"]["scene_number"],
                "text": pkg["scene_core"]["scene_text"][:1000],  # limit text length
                "entities": entity_labels[:10],
            })

        user_content = json.dumps({"scenes": scenes_payload}, ensure_ascii=False)
        result = await call_llm(client, system_prompt, user_content, tracker=tracker, max_tokens=4096)
        return result

    # Process batches with retry waves (up to 3 attempts for failed batches)
    summary_map = {}
    max_waves = 3
    remaining_batches = list(enumerate(batches))

    for wave in range(1, max_waves + 1):
        if not remaining_batches:
            break

        print(f"[input_assembly] wave {wave}/{max_waves}: {len(remaining_batches)} batches")

        async def _safe_batch(i, batch):
            try:
                result = await _process_batch(batch)
                return (i, batch, result, True)
            except Exception as e:
                print(f"[input_assembly] WARN: batch {i+1} failed (wave {wave}): {e}")
                return (i, batch, {"scenes": []}, False)

        tasks = [_safe_batch(i, b) for i, b in remaining_batches]
        wave_results = await asyncio.gather(*tasks)

        failed_batches = []
        for i, batch, result, ok in wave_results:
            for scene_data in result.get("scenes", []):
                sid = scene_data.get("scene_id", "")
                if sid and scene_data.get("scene_summary"):
                    summary_map[sid] = {
                        "scene_summary": scene_data.get("scene_summary", ""),
                        "narrative_function": scene_data.get("narrative_function", ""),
                    }
            if not ok:
                failed_batches.append((i, batch))

        remaining_batches = failed_batches
        if not remaining_batches:
            break

    if remaining_batches:
        print(f"[input_assembly] WARN: {len(remaining_batches)} batches still failed after {max_waves} waves")

    applied = 0
    for pkg in packages:
        sid = pkg["scene_id"]
        if sid in summary_map:
            pkg["scene_core"]["scene_summary"] = summary_map[sid]["scene_summary"]
            pkg["scene_core"]["narrative_function"] = summary_map[sid]["narrative_function"]
            applied += 1

    print(f"[input_assembly] applied summaries to {applied}/{len(packages)} scenes")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

async def assemble_all(
    source_package_path: str,
    compiled_entities_path: str,
    research_intake_path: str,
    asset_pool_path: str,
    sector_root: str,
    job_id: str,
) -> None:
    sr = Path(sector_root).resolve()

    # Load upstream
    print("[input_assembly] loading upstream artifacts...")
    source_pkg = read_json(Path(source_package_path))
    compiled_ent = read_json(Path(compiled_entities_path))
    research_int = read_json(Path(research_intake_path))
    asset_pool = read_json(Path(asset_pool_path))

    scenes = source_pkg.get("scenes", [])
    print(f"[input_assembly] {len(scenes)} scenes to process")

    # Build lookups
    scene_index_lookup = _build_scene_index_lookup(research_int)
    entity_lookup = _build_entity_lookup(compiled_ent)
    asset_lookup = _build_asset_lookup(asset_pool)
    target_asset_index = _build_target_asset_index(asset_pool)

    print(f"[input_assembly] lookups: {len(scene_index_lookup)} scene_index entries, "
          f"{len(entity_lookup)} entity-mapped scenes, {len(asset_lookup)} assets, "
          f"{len(target_asset_index)} targets")

    # Phase 1: Deterministic assembly
    packages = []
    for idx, scene in enumerate(scenes):
        pkg = _assemble_scene_deterministic(
            scene, idx, entity_lookup, scene_index_lookup,
            target_asset_index, asset_lookup,
        )
        packages.append(pkg)

    # Stats
    with_refs = sum(1 for p in packages if p["reference_layer"]["reference_ready_assets"])
    print(f"[input_assembly] deterministic: {with_refs}/{len(packages)} scenes have S4 references")

    # Phase 2: LLM-derived fields
    client = create_client()
    tracker = UsageTracker()
    await _derive_semantic_fields(packages, entity_lookup, client, tracker)

    # Phase 3: Write packages
    written = 0
    for pkg in packages:
        out_path = scene_input_package_path(sr, pkg["scene_id"])
        write_json(out_path, pkg)
        written += 1

    # Write usage
    write_json(usage_path(sr), {
        "phase": "input_assembly",
        "usage": tracker.summary(),
        "timestamp": utc_now(),
    })

    print(f"[input_assembly] DONE: {written} packages written, {tracker.summary()['calls']} LLM calls")


def main():
    if len(sys.argv) != 7:
        raise SystemExit(
            "usage: input_assembly.py <source_package> <compiled_entities> "
            "<research_intake> <asset_pool> <sector_root> <job_id>"
        )
    asyncio.run(assemble_all(*sys.argv[1:]))


if __name__ == "__main__":
    main()
