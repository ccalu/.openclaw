import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def write_json(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def read_json(path_str: str | None):
    if not path_str:
        return None
    path = Path(path_str)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def build_source_package(b2_bootstrap: dict):
    inputs = b2_bootstrap.get("inputs", {})
    screenplay = read_json(inputs.get("screenplay_analysis_path")) or {}
    script_fetched = read_json(inputs.get("script_fetched_checkpoint_path")) or {}
    fetched_data = script_fetched.get("data", {})

    scenes = []
    for idx, scene in enumerate(screenplay.get("scenes", []), start=1):
        scenes.append({
            "scene_id": scene.get("scene_id") or f"scene_{idx:03d}",
            "scene_number": scene.get("scene_number", idx),
            "text": scene.get("text") or scene.get("summary") or ""
        })

    language = screenplay.get("language") or b2_bootstrap.get("language")
    video_name = script_fetched.get("video_name") or b2_bootstrap.get("job_id")

    return {
        "contract_version": "s3_source_package.v1",
        "job_id": b2_bootstrap["job_id"],
        "video_id": b2_bootstrap.get("video_id", b2_bootstrap.get("job_id")),
        "account_id": b2_bootstrap["account_id"],
        "language": language,
        "video_context": {
            "video_name": video_name,
            "title": fetched_data.get("title") or screenplay.get("video_context", {}).get("title") or video_name,
            "description": fetched_data.get("description") or screenplay.get("video_context", {}).get("description") or "",
            "account_id": b2_bootstrap["account_id"],
            "language": language
        },
        "script_overview": {
            "full_word_count": fetched_data.get("words"),
            "total_scenes": screenplay.get("total_scenes", len(scenes)),
            "source_row": fetched_data.get("row_number")
        },
        "entity_focus": {
            "priority_mode": "strict_precision",
            "coverage_mode": "balanced"
        },
        "inputs": inputs,
        "scenes": scenes,
        "generated_at": utc_now()
    }


def main():
    if len(sys.argv) != 3:
        raise SystemExit("usage: build_s3_bootstrap_from_b2.py <b2_bootstrap_path> <output_dir>")

    b2_bootstrap_path = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])
    b2_bootstrap = json.loads(b2_bootstrap_path.read_text(encoding="utf-8"))

    run_root = Path(b2_bootstrap["run_root"])
    b2_root = Path(b2_bootstrap["b2_root"])
    sector_root = b2_root / "sectors" / "s3_visual_planning"

    source_package = build_source_package(b2_bootstrap)
    source_package_path = sector_root / "inputs" / "s3_source_package.json"
    write_json(source_package_path, source_package)

    bootstrap = {
        "kind": "s3_start",
        "contract_version": "s3.supervisor_bootstrap.v1",
        "job_id": b2_bootstrap["job_id"],
        "video_id": source_package["video_id"],
        "account_id": b2_bootstrap["account_id"],
        "language": source_package["language"],
        "run_root": str(run_root),
        "sector_root": str(sector_root),
        "source_package_path": str(source_package_path),
        "checkpoints_dir": str(sector_root / "checkpoints"),
        "operators_dir": str(sector_root / "operators"),
        "compiled_dir": str(sector_root / "compiled"),
        "logs_dir": str(sector_root / "logs"),
        "dispatch_dir": str(sector_root / "dispatch"),
        "bootstrap_checkpoint_path": str(sector_root / "checkpoints" / "s3_bootstrap_ready.json")
    }

    out_path = output_dir / "s3_supervisor_bootstrap.json"
    write_json(out_path, bootstrap)
    write_json(Path(bootstrap["bootstrap_checkpoint_path"]), {
        "event": "s3_bootstrap_ready",
        "job_id": b2_bootstrap["job_id"],
        "sector": "s3_visual_planning",
        "created_at": utc_now(),
        "source_package_path": str(source_package_path)
    })

    print(str(out_path))


if __name__ == "__main__":
    main()
