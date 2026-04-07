"""S4 path derivation. All paths absolute via .resolve()."""
import re
from pathlib import Path


def sector_root(b2_root: Path) -> Path:
    return (b2_root / "sectors" / "s4_asset_research").resolve()


def intake_path(sr: Path) -> Path:
    return (sr / "intake" / "research_intake.json").resolve()


def batch_manifest_path(sr: Path) -> Path:
    return (sr / "intake" / "research_batch_manifest.json").resolve()


def target_root(sr: Path, target_id: str) -> Path:
    return (sr / "targets" / sanitize_target_id(target_id)).resolve()


def target_brief_path(sr: Path, target_id: str) -> Path:
    tid = sanitize_target_id(target_id)
    return (sr / "targets" / tid / f"{tid}_brief.json").resolve()


def candidate_set_path(sr: Path, target_id: str) -> Path:
    tid = sanitize_target_id(target_id)
    return (sr / "targets" / tid / f"{tid}_candidate_set.json").resolve()


def evaluated_set_path(sr: Path, target_id: str) -> Path:
    tid = sanitize_target_id(target_id)
    return (sr / "targets" / tid / f"{tid}_evaluated_candidate_set.json").resolve()


def coverage_report_path(sr: Path) -> Path:
    return (sr / "compiled" / "coverage_report.json").resolve()


def research_pack_path(sr: Path) -> Path:
    return (sr / "compiled" / "research_pack.json").resolve()


def sector_report_path(sr: Path) -> Path:
    return (sr / "compiled" / "s4_sector_report.md").resolve()


def sector_status_path(sr: Path) -> Path:
    return (sr / "runtime" / "sector_status.json").resolve()


def search_queries_path(sr: Path, target_id: str) -> Path:
    tid = sanitize_target_id(target_id)
    return (sr / "targets" / tid / f"{tid}_search_queries.json").resolve()


def serper_results_path(sr: Path, target_id: str) -> Path:
    tid = sanitize_target_id(target_id)
    return (sr / "targets" / tid / f"{tid}_serper_results.json").resolve()


def asset_report_path(sr: Path, target_id: str) -> Path:
    tid = sanitize_target_id(target_id)
    return (sr / "targets" / tid / f"{tid}_asset_materialization_report.json").resolve()


def dispatch_log_path(sr: Path) -> Path:
    return (sr / "logs" / "dispatch_log.json").resolve()


def sanitize_target_id(tid: str) -> str:
    """ASCII-safe, lowercase, underscores."""
    cleaned = tid.lower().strip()
    cleaned = re.sub(r"[^a-z0-9_]", "_", cleaned)
    cleaned = re.sub(r"_+", "_", cleaned)
    return cleaned.strip("_")
