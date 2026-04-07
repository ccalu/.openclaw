"""S4 checkpoint and status helpers."""
import sys
from pathlib import Path

from artifact_io import read_json, write_json, utc_now


# ---------------------------------------------------------------------------
# Phase checkpoint progression
# ---------------------------------------------------------------------------

PHASE_CHECKPOINTS_FILE = "phase_checkpoints.json"


def _phase_checkpoints_path(sector_root: Path) -> Path:
    return (sector_root / "runtime" / PHASE_CHECKPOINTS_FILE).resolve()


def read_phase_checkpoints(sector_root: Path) -> dict:
    """Read current phase progression. Returns empty structure if none exists."""
    p = _phase_checkpoints_path(sector_root)
    if p.exists():
        return read_json(p)
    return {
        "job_id": None,
        "phases_completed": [],
        "current_phase": "not_started",
        "last_updated": None,
    }


def write_phase_checkpoint(
    sector_root: Path,
    phase_name: str,
    status: str,
    job_id: str,
    artifacts: list[str] | None = None,
    duration_seconds: float | None = None,
) -> None:
    """Append a phase checkpoint to the progression file."""
    sr = sector_root.resolve()
    data = read_phase_checkpoints(sr)
    data["job_id"] = job_id

    entry = {
        "phase": phase_name,
        "status": status,
        "timestamp": utc_now(),
    }
    if artifacts:
        entry["artifacts"] = artifacts
    if duration_seconds is not None:
        entry["duration_seconds"] = duration_seconds

    # Replace existing entry for same phase if re-running
    data["phases_completed"] = [
        p for p in data["phases_completed"] if p["phase"] != phase_name
    ]
    data["phases_completed"].append(entry)
    data["current_phase"] = phase_name
    data["last_updated"] = utc_now()

    write_json(_phase_checkpoints_path(sr), data)


def get_completed_phases(sector_root: Path) -> set[str]:
    """Return set of phase names that completed successfully."""
    data = read_phase_checkpoints(sector_root)
    return {
        p["phase"]
        for p in data.get("phases_completed", [])
        if p.get("status") == "done"
    }


# ---------------------------------------------------------------------------
# Sector status (runtime/sector_status.json)
# ---------------------------------------------------------------------------

def write_sector_status(sector_root: Path, phase: str, status: str, details: dict = None) -> None:
    """Write current sector status to runtime/sector_status.json."""
    sr = sector_root.resolve()
    payload = {
        "sector": "s4_asset_research",
        "phase": phase,
        "status": status,
        "updated_at": utc_now(),
    }
    if details:
        payload["details"] = details
    path = sr / "runtime" / "sector_status.json"
    write_json(path, payload)


# ---------------------------------------------------------------------------
# Event checkpoints (checkpoints/{event}.json)
# ---------------------------------------------------------------------------

def write_checkpoint(sector_root: Path, event: str, data: dict = None) -> None:
    """Write a checkpoint event to checkpoints/{event}.json."""
    sr = sector_root.resolve()
    payload = {
        "event": event,
        "sector": "s4_asset_research",
        "timestamp": utc_now(),
    }
    if data:
        payload.update(data)
    path = sr / "checkpoints" / f"{event}.json"
    write_json(path, payload)


def write_completion(sector_root: Path, job_id: str, compiled_output_path: str, sector_report_path: str) -> None:
    """Write s4_completed checkpoint and mirror to b2."""
    sr = sector_root.resolve()
    payload = {
        "event": "s4_completed",
        "job_id": job_id,
        "sector": "s4_asset_research",
        "compiled_output_path": compiled_output_path,
        "sector_report_path": sector_report_path,
        "completed_at": utc_now(),
        "status": "completed",
    }
    write_json(sr / "checkpoints" / "s4_completed.json", payload)
    mirror_to_b2(sr, "s4_completed.json", payload)
    print(f"[checkpoint] s4_completed written + mirrored to b2")


def write_failure(sector_root: Path, job_id: str, reason: str) -> None:
    """Write s4_failed checkpoint and mirror to b2."""
    sr = sector_root.resolve()
    payload = {
        "event": "s4_failed",
        "job_id": job_id,
        "sector": "s4_asset_research",
        "failed_at": utc_now(),
        "status": "failed",
        "error": reason,
    }
    write_json(sr / "checkpoints" / "s4_failed.json", payload)
    mirror_to_b2(sr, "s4_failed.json", payload)
    print(f"[checkpoint] s4_failed written + mirrored to b2: {reason}")


def mirror_to_b2(sector_root: Path, filename: str, data: dict) -> None:
    """Mirror checkpoint to b2/checkpoints/. sector_root = b2/sectors/s4_asset_research."""
    sr = sector_root.resolve()
    b2_checkpoints = sr.parent.parent / "checkpoints"
    write_json(b2_checkpoints / filename, data)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) < 4:
        raise SystemExit("usage: checkpoint_writer.py <started|completed|failed> <sector_root> <job_id> [args...]")

    mode = sys.argv[1]
    sr = Path(sys.argv[2])
    job_id = sys.argv[3]

    if mode == "started":
        write_sector_status(sr, phase="bootstrap", status="started", details={"job_id": job_id})
        write_checkpoint(sr, event="s4_bootstrap_started", data={"job_id": job_id})
        print("sector_status + checkpoint written: bootstrap/started")
    elif mode == "completed":
        if len(sys.argv) < 6:
            raise SystemExit("usage: checkpoint_writer.py completed <sector_root> <job_id> <compiled_path> <report_path>")
        write_completion(sr, job_id, sys.argv[4], sys.argv[5])
    elif mode == "failed":
        reason = sys.argv[4] if len(sys.argv) > 4 else "unknown_error"
        write_failure(sr, job_id, reason)
    else:
        raise SystemExit(f"unknown mode: {mode}")
