import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def write_json(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    if len(sys.argv) < 5:
        raise SystemExit("usage: emit_s3_b2_checkpoint.py <completed|failed> <b2_root> <job_id> <sector_root> [error]")

    mode = sys.argv[1]
    b2_root = Path(sys.argv[2])
    job_id = sys.argv[3]
    sector_root = Path(sys.argv[4])

    if mode == "completed":
        compiled_entities = sector_root / "compiled" / "compiled_entities.json"
        report = sector_root / "compiled" / "s3_sector_report.md"
        payload = {
            "event": "s3_completed",
            "job_id": job_id,
            "sector": "s3_visual_planning",
            "compiled_entities_path": str(compiled_entities),
            "sector_report_path": str(report),
            "completed_at": utc_now(),
            "status": "completed"
        }
        write_json(b2_root / "checkpoints" / "s3_completed.json", payload)
        print(str(b2_root / "checkpoints" / "s3_completed.json"))
        return

    if mode == "failed":
        error = sys.argv[5] if len(sys.argv) > 5 else "unknown_error"
        payload = {
            "event": "s3_failed",
            "job_id": job_id,
            "sector": "s3_visual_planning",
            "failed_at": utc_now(),
            "status": "failed",
            "error": error
        }
        write_json(b2_root / "checkpoints" / "s3_failed.json", payload)
        print(str(b2_root / "checkpoints" / "s3_failed.json"))
        return

    raise SystemExit(f"unknown mode: {mode}")


if __name__ == "__main__":
    main()
