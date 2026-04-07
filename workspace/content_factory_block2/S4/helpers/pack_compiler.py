"""S4 Pack Compiler -- builds final research pack and sector report.

Reads asset_materialization_report.json (new format) as primary source.
Falls back to evaluated_candidate_set.json (legacy) if absent.
"""
import sys
from pathlib import Path

from artifact_io import read_json, write_json, write_markdown, utc_now
from paths import (
    asset_report_path,
    evaluated_set_path,
    coverage_report_path,
    candidate_set_path,
    research_pack_path,
    sector_report_path,
    sanitize_target_id,
)
from schema_validator import validate_artifact_strict


def compile_pack(
    intake_path_arg: Path,
    sector_root: Path,
    job_id: str,
    video_id: str,
    account_id: str,
    language: str,
) -> Path:
    """Compile all S4 artifacts into the final research pack and sector report."""
    intake = read_json(intake_path_arg)
    targets = intake["research_targets"]
    scene_index = intake["scene_index"]

    print(f"[pack_compiler] compiling pack for {len(targets)} targets")

    # Read coverage report
    cov_path = coverage_report_path(sector_root)
    coverage = read_json(cov_path)
    cov_by_target = {tc["target_id"]: tc for tc in coverage["target_coverage"]}
    cov_by_scene = {sc["scene_id"]: sc for sc in coverage["scene_coverage"]}

    # Build target results
    target_results = []
    all_warnings = list(coverage.get("warnings", []))
    asset_manifest = []
    preview_manifest = []
    capture_manifest = []
    total_candidates = 0
    total_best = 0

    for target in targets:
        tid = target["target_id"]
        stid = sanitize_target_id(tid)

        # Try new format first (asset_materialization_report.json)
        new_report_path = asset_report_path(sector_root, tid)
        if new_report_path.exists():
            mat_report = read_json(new_report_path)
            entries = mat_report.get("entries", [])

            approved_ids = []
            for e in entries:
                total_candidates += 1
                if e.get("materialization_status") == "downloaded":
                    total_best += 1
                    cid = e["candidate_id"]
                    approved_ids.append(cid)
                    if e.get("local_asset_path"):
                        asset_manifest.append({
                            "candidate_id": cid,
                            "target_id": tid,
                            "local_asset_path": e["local_asset_path"],
                        })

            # Also check assets/ directory for any files not in the report
            assets_dir = sector_root / "targets" / stid / "assets"
            if assets_dir.exists():
                for f in assets_dir.iterdir():
                    if f.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp", ".gif"):
                        fid = f.stem.split("_")[0]
                        if not any(a["candidate_id"] == fid and a["target_id"] == tid for a in asset_manifest):
                            asset_manifest.append({
                                "candidate_id": fid,
                                "target_id": tid,
                                "local_asset_path": str(f),
                            })

            cov_state = cov_by_target.get(tid, {}).get("coverage_state", "unresolved")
            cov_notes = cov_by_target.get(tid, {}).get("notes", "")

            target_results.append({
                "target_id": tid,
                "canonical_label": target["canonical_label"],
                "best_factual_evidence_ids": [],
                "best_visual_reference_ids": approved_ids,
                "best_stylistic_inspiration_ids": [],
                "coverage_state": cov_state,
                "notes": cov_notes,
            })
            continue

        # Legacy format: evaluated_candidate_set.json
        try:
            eval_set = read_json(evaluated_set_path(sector_root, tid))
        except FileNotFoundError:
            all_warnings.append(f"no materialization report or evaluated set for target {tid}")
            target_results.append({
                "target_id": tid,
                "canonical_label": target["canonical_label"],
                "best_factual_evidence_ids": [],
                "best_visual_reference_ids": [],
                "best_stylistic_inspiration_ids": [],
                "coverage_state": "unresolved",
                "notes": "no data found",
            })
            continue

        # Legacy: read raw candidate set for asset paths
        try:
            raw_set = read_json(candidate_set_path(sector_root, tid))
            raw_by_id = {c["candidate_id"]: c for c in raw_set.get("candidates", [])}
        except FileNotFoundError:
            raw_by_id = {}

        # Legacy: read materialization report if it exists
        mat_by_id = {}
        legacy_mat_path = sector_root / "targets" / tid / f"{tid}_asset_materialization_report.json"
        if legacy_mat_path.exists():
            legacy_mat = read_json(legacy_mat_path)
            mat_by_id = {e["candidate_id"]: e for e in legacy_mat.get("entries", [])}

        factual_ids = []
        visual_ids = []
        stylistic_ids = []

        for ev in eval_set.get("evaluated_candidates", []):
            total_candidates += 1
            cid = ev["candidate_id"]
            fc = ev["final_classification"]

            if ev["is_best_candidate"]:
                total_best += 1
                if fc == "factual_evidence":
                    factual_ids.append(cid)
                elif fc == "visual_reference":
                    visual_ids.append(cid)
                elif fc == "stylistic_inspiration":
                    stylistic_ids.append(cid)

            mat_entry = mat_by_id.get(cid, {})
            if mat_entry.get("local_asset_path"):
                asset_manifest.append({
                    "candidate_id": cid,
                    "target_id": tid,
                    "local_asset_path": mat_entry["local_asset_path"],
                })
            if mat_entry.get("capture_path"):
                capture_manifest.append({
                    "candidate_id": cid,
                    "target_id": tid,
                    "capture_path": mat_entry["capture_path"],
                })

        cov_state = cov_by_target.get(tid, {}).get("coverage_state", "unresolved")
        cov_notes = cov_by_target.get(tid, {}).get("notes", "")

        target_results.append({
            "target_id": tid,
            "canonical_label": target["canonical_label"],
            "best_factual_evidence_ids": factual_ids,
            "best_visual_reference_ids": visual_ids,
            "best_stylistic_inspiration_ids": stylistic_ids,
            "coverage_state": cov_state,
            "notes": cov_notes,
        })

    # Build scene results
    scene_results = []
    for scene in scene_index:
        sid = scene["scene_id"]
        linked = scene["linked_target_ids"]

        recommended = []
        for tid in linked:
            for tr in target_results:
                if tr["target_id"] == tid:
                    recommended.extend(tr["best_factual_evidence_ids"])
                    recommended.extend(tr["best_visual_reference_ids"])
                    recommended.extend(tr["best_stylistic_inspiration_ids"])

        sc_cov = cov_by_scene.get(sid, {})
        scene_results.append({
            "scene_id": sid,
            "linked_target_ids": linked,
            "recommended_candidate_ids": list(dict.fromkeys(recommended)),
            "coverage_state": sc_cov.get("coverage_state", "unresolved"),
            "notes": sc_cov.get("notes", ""),
        })

    # Determine overall status
    covered_count = sum(1 for tr in target_results if tr["coverage_state"] == "covered")
    partially_count = sum(1 for tr in target_results if tr["coverage_state"] == "partially_covered")
    if covered_count == len(target_results):
        status = "fully_covered"
    elif covered_count + partially_count > 0:
        status = "partially_covered"
    else:
        status = "unresolved"

    pack = {
        "contract_version": "s4.research_pack.v1",
        "metadata": {
            "job_id": job_id,
            "video_id": video_id,
            "account_id": account_id,
            "language": language,
            "sector": "s4_asset_research",
            "generated_at": utc_now(),
            "status": status,
        },
        "target_results": target_results,
        "scene_results": scene_results,
        "asset_manifest": asset_manifest,
        "preview_manifest": preview_manifest,
        "capture_manifest": capture_manifest,
        "unresolved_gaps": coverage.get("unresolved_gaps", []),
        "warnings": all_warnings,
    }

    validate_artifact_strict(pack, "research_pack")

    out = research_pack_path(sector_root)
    write_json(out, pack)
    print(f"[pack_compiler] wrote research pack: {out}")

    # Compile reference_ready asset pool from sidecars
    _compile_reference_ready_pool(sector_root, targets, scene_index, pack)

    # Build sector report
    report_lines = [
        "# S4 Asset Research - Sector Report",
        "",
        f"- **Job**: {job_id}",
        f"- **Video**: {video_id}",
        f"- **Account**: {account_id}",
        f"- **Language**: {language}",
        f"- **Status**: {status}",
        f"- **Generated**: {pack['metadata']['generated_at']}",
        "",
        "## Summary",
        "",
        f"- Targets: {len(target_results)}",
        f"- Candidates evaluated: {total_candidates}",
        f"- Best candidates selected: {total_best}",
        f"- Assets downloaded: {len(asset_manifest)}",
        f"- Page captures: {len(capture_manifest)}",
        "",
        "## Target Coverage",
        "",
        "| Target | Label | State | Assets |",
        "|--------|-------|-------|--------|",
    ]

    for tr in target_results:
        n_assets = (len(tr["best_factual_evidence_ids"])
                    + len(tr["best_visual_reference_ids"])
                    + len(tr["best_stylistic_inspiration_ids"]))
        report_lines.append(
            f"| {tr['target_id']} | {tr['canonical_label']} "
            f"| {tr['coverage_state']} | {n_assets} |"
        )

    report_lines.extend([
        "",
        "## Scene Coverage",
        "",
        "| Scene | State | Linked Targets | Recommended |",
        "|-------|-------|----------------|-------------|",
    ])

    for sr_item in scene_results:
        report_lines.append(
            f"| {sr_item['scene_id']} | {sr_item['coverage_state']} "
            f"| {', '.join(sr_item['linked_target_ids'])} "
            f"| {len(sr_item['recommended_candidate_ids'])} |"
        )

    if pack["unresolved_gaps"]:
        report_lines.extend(["", "## Unresolved Gaps", ""])
        for gap in pack["unresolved_gaps"]:
            report_lines.append(f"- {gap}")

    if pack["warnings"]:
        report_lines.extend(["", "## Warnings", ""])
        for w in pack["warnings"]:
            report_lines.append(f"- {w}")

    report_out = sector_report_path(sector_root)
    write_markdown(report_out, "\n".join(report_lines))
    print(f"[pack_compiler] wrote sector report: {report_out}")

    return out


def _compile_reference_ready_pool(
    sector_root: Path,
    targets: list,
    scene_index: list,
    pack: dict,
) -> None:
    """Compile all reference_ready sidecars into a single asset pool for S5."""
    # Build target→scenes lookup from scene_index
    target_to_scenes = {}
    for scene in scene_index:
        for tid in scene["linked_target_ids"]:
            target_to_scenes.setdefault(tid, []).append(scene["scene_id"])

    # Build target label lookup
    target_labels = {t["target_id"]: t.get("canonical_label", "") for t in targets}

    # Collect all sidecars
    assets = []
    targets_dir = sector_root / "targets"
    if not targets_dir.exists():
        print("[pack_compiler] no targets/ dir, skipping reference_ready pool")
        return

    for target_dir in sorted(targets_dir.iterdir()):
        assets_dir = target_dir / "assets"
        if not assets_dir.exists():
            continue
        for sidecar_path in sorted(assets_dir.glob("*.reference_ready.json")):
            try:
                sidecar = read_json(sidecar_path)
            except Exception:
                continue
            # Enrich with scene relevance from intake linkage
            tid = sidecar.get("source_target_id", "")
            sidecar["scene_relevance"] = target_to_scenes.get(tid, [])
            assets.append(sidecar)

    if not assets:
        print("[pack_compiler] no reference_ready sidecars found, skipping pool")
        return

    # Build grouped views
    by_target = {}
    by_reference_value = {}
    by_depiction_type = {}
    for a in assets:
        tid = a.get("source_target_id", "unknown")
        by_target.setdefault(tid, []).append(a["asset_id"])
        for rv in a.get("reference_value", []):
            by_reference_value.setdefault(rv, []).append(a["asset_id"])
        dt = a.get("depiction_type", "unknown")
        by_depiction_type.setdefault(dt, []).append(a["asset_id"])

    pool = {
        "contract_version": "s4.reference_ready_asset_pool.v1",
        "metadata": {
            "generated_at": utc_now(),
            "source_pack_version": pack["metadata"].get("generated_at", ""),
            "total_assets": len(assets),
        },
        "assets": assets,
        "grouped_views": {
            "by_target": by_target,
            "by_reference_value": by_reference_value,
            "by_depiction_type": by_depiction_type,
        },
    }

    compiled_dir = sector_root / "compiled"
    compiled_dir.mkdir(parents=True, exist_ok=True)
    pool_path = compiled_dir / "s4_reference_ready_asset_pool.json"
    write_json(pool_path, pool)
    print(f"[pack_compiler] wrote reference_ready pool: {pool_path} ({len(assets)} assets)")


def main():
    if len(sys.argv) != 7:
        raise SystemExit(
            "usage: pack_compiler.py <intake_path> <sector_root> "
            "<job_id> <video_id> <account_id> <language>"
        )
    compile_pack(
        intake_path_arg=Path(sys.argv[1]),
        sector_root=Path(sys.argv[2]),
        job_id=sys.argv[3],
        video_id=sys.argv[4],
        account_id=sys.argv[5],
        language=sys.argv[6],
    )


if __name__ == "__main__":
    main()
