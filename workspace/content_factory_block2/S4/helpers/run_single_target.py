# DEPRECATED — This file is no longer part of the active S4 pipeline.
# Replaced by the V3 asset_pipeline (s4_query_generator + s4_image_collector + s4_visual_evaluator).
# Retained temporarily for reference. See S4_ARCHITECTURE_V2.md for current architecture.
"""S4 Single-Target Prototype Runner -- runs full S4 pipeline for 1 target."""
import sys
import traceback
from pathlib import Path

from artifact_io import read_json
from checkpoint_writer import write_completion, write_failure
from dirs import create_s4_directories
from paths import (
    sector_root as derive_sector_root,
    intake_path,
    batch_manifest_path,
    target_brief_path,
    candidate_set_path,
    evaluated_set_path,
    coverage_report_path,
    research_pack_path,
    sector_report_path,
)
from schema_validator import validate_artifact_strict


def _step(step_num: int, name: str) -> None:
    """Print step banner."""
    print(f"\n{'='*60}")
    print(f"  STEP {step_num}: {name}")
    print(f"{'='*60}")


def run_pipeline(
    compiled_entities_path: Path,
    b2_root: Path,
    job_id: str,
    video_id: str,
    account_id: str,
    language: str,
) -> None:
    """Run the full S4 single-target pipeline.

    Sequence:
    1. Create S4 directories
    2. target_builder -> validate intake
    3. batch_manifest_builder -> validate manifest
    4. web_investigator -> validate briefs
    5. research_worker -> validate candidate_set
    6. candidate_evaluator -> validate evaluated_set
    7. coverage_analyst -> validate coverage_report
    8. pack_compiler -> validate research_pack
    9. Write s4_completed checkpoint
    """
    sr = derive_sector_root(b2_root)
    compiled_entities_path = compiled_entities_path.resolve()

    print(f"\nS4 Single-Target Prototype Runner")
    print(f"  compiled_entities: {compiled_entities_path}")
    print(f"  b2_root: {b2_root}")
    print(f"  sector_root: {sr}")
    print(f"  job_id: {job_id}")
    print(f"  video_id: {video_id}")
    print(f"  account_id: {account_id}")
    print(f"  language: {language}")

    try:
        # -------------------------------------------------------
        # Step 1: Create S4 directories
        # -------------------------------------------------------
        _step(1, "Create S4 directories")
        create_s4_directories(sr)
        print(f"[runner] directories created at {sr}")

        # -------------------------------------------------------
        # Step 2: Target Builder
        # -------------------------------------------------------
        _step(2, "Target Builder")
        from target_builder import build_intake
        intake_out = build_intake(
            compiled_entities_path=compiled_entities_path,
            sector_root=sr,
            job_id=job_id,
            video_id=video_id,
            account_id=account_id,
            language=language,
        )
        intake_data = read_json(intake_out)
        validate_artifact_strict(intake_data, "research_intake")
        print(f"[runner] intake validated: {intake_out}")

        # -------------------------------------------------------
        # Step 3: Batch Manifest Builder
        # -------------------------------------------------------
        _step(3, "Batch Manifest Builder")
        from batch_manifest_builder import build_manifest
        manifest_out = build_manifest(intake_out, sr)
        manifest_data = read_json(manifest_out)
        validate_artifact_strict(manifest_data, "research_batch_manifest")
        print(f"[runner] manifest validated: {manifest_out}")

        # -------------------------------------------------------
        # Step 4: Web Investigator
        # -------------------------------------------------------
        _step(4, "Web Investigator")
        from web_investigator import build_all_briefs
        briefs = build_all_briefs(intake_out, manifest_out, sr)
        for brief in briefs:
            validate_artifact_strict(brief, "target_research_brief")
        print(f"[runner] {len(briefs)} briefs validated")

        # Get target IDs for subsequent steps
        target_ids = [t["target_id"] for t in intake_data["research_targets"]]

        # -------------------------------------------------------
        # Step 5: Research Worker
        # -------------------------------------------------------
        _step(5, "Research Worker")
        from research_worker import research_target
        for tid in target_ids:
            brief_path = target_brief_path(sr, tid)
            cs_out = research_target(brief_path, sr)
            cs_data = read_json(cs_out)
            validate_artifact_strict(cs_data, "candidate_set")
            print(f"[runner] candidate_set validated for {tid}: {cs_out}")

        # -------------------------------------------------------
        # Step 6: Candidate Evaluator
        # -------------------------------------------------------
        _step(6, "Candidate Evaluator")
        from candidate_evaluator import evaluate_candidates
        for tid in target_ids:
            cs_path = candidate_set_path(sr, tid)
            brief_path = target_brief_path(sr, tid)
            ev_out = evaluate_candidates(cs_path, brief_path, sr)
            ev_data = read_json(ev_out)
            validate_artifact_strict(ev_data, "evaluated_candidate_set")
            print(f"[runner] evaluated_set validated for {tid}: {ev_out}")

        # -------------------------------------------------------
        # Step 7: Coverage Analyst
        # -------------------------------------------------------
        _step(7, "Coverage Analyst")
        from coverage_analyst import analyze_coverage
        cov_out = analyze_coverage(intake_out, sr)
        cov_data = read_json(cov_out)
        validate_artifact_strict(cov_data, "coverage_report")
        print(f"[runner] coverage report validated: {cov_out}")

        # -------------------------------------------------------
        # Step 8: Pack Compiler
        # -------------------------------------------------------
        _step(8, "Pack Compiler")
        from pack_compiler import compile_pack
        pack_out = compile_pack(
            intake_path_arg=intake_out,
            sector_root=sr,
            job_id=job_id,
            video_id=video_id,
            account_id=account_id,
            language=language,
        )
        pack_data = read_json(pack_out)
        validate_artifact_strict(pack_data, "research_pack")
        print(f"[runner] research pack validated: {pack_out}")

        # -------------------------------------------------------
        # Step 9: Write s4_completed checkpoint + mirror to b2
        # -------------------------------------------------------
        _step(9, "Completion checkpoint")
        report_out = sector_report_path(sr)
        write_completion(sr, job_id, str(pack_out), str(report_out))

        # -------------------------------------------------------
        # Success summary
        # -------------------------------------------------------
        print(f"\n{'='*60}")
        print(f"  S4 PIPELINE COMPLETED SUCCESSFULLY")
        print(f"{'='*60}")
        print(f"  research_pack: {pack_out}")
        print(f"  sector_report: {report_out}")
        print(f"  status: {pack_data['metadata']['status']}")
        print(f"  targets: {len(pack_data['target_results'])}")
        print(f"  scenes: {len(pack_data['scene_results'])}")
        print(f"  unresolved_gaps: {len(pack_data['unresolved_gaps'])}")
        print(f"{'='*60}\n")

    except Exception as exc:
        print(f"\n[runner] PIPELINE FAILED: {exc}")
        traceback.print_exc()
        try:
            write_failure(sr, job_id, str(exc)[:500])
        except Exception:
            print("[runner] could not write failure checkpoint")
        sys.exit(1)


def main():
    if len(sys.argv) != 7:
        raise SystemExit(
            "usage: run_single_target.py <compiled_entities_path> <b2_root> "
            "<job_id> <video_id> <account_id> <language>"
        )
    run_pipeline(
        compiled_entities_path=Path(sys.argv[1]),
        b2_root=Path(sys.argv[2]),
        job_id=sys.argv[3],
        video_id=sys.argv[4],
        account_id=sys.argv[5],
        language=sys.argv[6],
    )


if __name__ == "__main__":
    main()
