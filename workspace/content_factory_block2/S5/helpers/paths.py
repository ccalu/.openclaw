"""S5 path derivation. All paths absolute via .resolve()."""
import re
from pathlib import Path


def sector_root(b2_root: Path) -> Path:
    return (b2_root / "sectors" / "s5_scene_kit_design").resolve()


def scene_input_package_path(sr: Path, scene_id: str) -> Path:
    return (sr / "scene_direction_input_packages" / f"{sanitize_scene_id(scene_id)}.json").resolve()


def scene_kit_spec_path(sr: Path, scene_id: str) -> Path:
    return (sr / "scene_kit_specs" / f"{sanitize_scene_id(scene_id)}.json").resolve()


def direction_frame_path(sr: Path) -> Path:
    return (sr / "compiled" / "video_direction_frame.json").resolve()


def scene_kit_pack_path(sr: Path) -> Path:
    return (sr / "compiled" / "s5_scene_kit_pack.json").resolve()


def sector_report_path(sr: Path) -> Path:
    return (sr / "compiled" / "s5_sector_report.md").resolve()


def phase_checkpoints_path(sr: Path) -> Path:
    return (sr / "runtime" / "phase_checkpoints.json").resolve()


def sector_status_path(sr: Path) -> Path:
    return (sr / "runtime" / "sector_status.json").resolve()


def usage_path(sr: Path) -> Path:
    return (sr / "runtime" / "minimax_usage.json").resolve()


def sanitize_scene_id(sid: str) -> str:
    """ASCII-safe, lowercase, underscores."""
    cleaned = sid.lower().strip()
    cleaned = re.sub(r"[^a-z0-9_]", "_", cleaned)
    cleaned = re.sub(r"_+", "_", cleaned)
    return cleaned.strip("_")
