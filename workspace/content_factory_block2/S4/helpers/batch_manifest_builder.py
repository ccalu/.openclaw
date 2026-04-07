"""S4 Batch Manifest Builder -- creates research batch manifest from intake."""
import sys
from pathlib import Path

from artifact_io import read_json, write_json
from paths import batch_manifest_path, target_brief_path, candidate_set_path
from schema_validator import validate_artifact_strict


def build_manifest(in_path: Path, sector_root: Path) -> Path:
    """Build batch manifest from intake.

    For prototype: single batch, single target, parallelism_cap=1.
    """
    intake = read_json(in_path)
    job_id = intake["metadata"]["job_id"]
    targets = intake["research_targets"]
    target_ids = [t["target_id"] for t in targets]

    manifest = {
        "contract_version": "s4.research_batch_manifest.v1",
        "job_id": job_id,
        "parallelism_cap": 1,
        "batches": [
            {
                "batch_id": "batch_001",
                "target_ids": target_ids,
                "priority_order": target_ids,
                "notes": "single-batch multi-target",
            }
        ],
        "expected_worker_outputs": [
            {
                "target_id": tid,
                "brief_path": str(target_brief_path(sector_root, tid)),
                "candidate_set_path": str(candidate_set_path(sector_root, tid)),
            }
            for tid in target_ids
        ],
        "v1_second_round_policy": "disabled",
    }

    validate_artifact_strict(manifest, "research_batch_manifest")

    out = batch_manifest_path(sector_root)
    write_json(out, manifest)
    print(f"[batch_manifest_builder] wrote manifest: {out}")
    print(f"[batch_manifest_builder] {len(target_ids)} targets in 1 batch")
    return out


def main():
    if len(sys.argv) != 3:
        raise SystemExit("usage: batch_manifest_builder.py <intake_path> <sector_root>")
    build_manifest(Path(sys.argv[1]), Path(sys.argv[2]))


if __name__ == "__main__":
    main()
