"""S5 Supervisor Runtime Orchestrator — checkpoint-resume, deterministic.

This is the official S5 long-chain orchestrator. The SM OpenClaw actor
delegates to this script. It owns:
- sequential dispatch of all helper-direct phases
- schema validation gates between phases
- checkpoint-resume (can be interrupted and restarted)
- completion/failure writing + B2 mirror
- run summary + duration tracking
"""
import json
import subprocess
import sys
import time
from pathlib import Path

from artifact_io import read_json
from bootstrap_loader import load_bootstrap
from dirs import create_s5_directories
from checkpoint_writer import (
    get_completed_phases,
    write_checkpoint,
    write_completion,
    write_failure,
    write_phase_checkpoint,
    write_sector_status,
)
from paths import (
    direction_frame_path,
    scene_kit_pack_path,
    sector_report_path,
    usage_path,
)
from schema_validator import validate_artifact

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

HELPERS_DIR = Path(__file__).parent.resolve()
HELPER_TIMEOUT_INPUT_ASSEMBLY = 600   # 10 min (30 concurrent MiniMax calls with retries)
HELPER_TIMEOUT_DIRECTION_FRAME = 120  # 2 min (1 call + overhead)
HELPER_TIMEOUT_SCENE_KIT_DESIGN = 600 # 10 min (150 calls with Semaphore(10))
HELPER_TIMEOUT_COMPILE = 60           # 1 min (deterministic)

S5_AGENTS = [
    "sm_s5_scene_kit_design",
    "op_s5_scene_kit_designer",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _run_helper(cmd: list[str], timeout: int = 60) -> subprocess.CompletedProcess:
    """Run a helper subprocess with timeout."""
    return subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=timeout)


def _clean_s5_sessions() -> None:
    """Clean all S5 OpenClaw agent sessions to prevent context leaking between videos."""
    print("[supervisor] cleaning S5 agent sessions...")
    for agent in S5_AGENTS:
        try:
            result = subprocess.run(
                ["openclaw.cmd", "sessions", "cleanup", "--agent", agent, "--enforce"],
                capture_output=True, text=True, timeout=15,
            )
            if result.returncode == 0:
                print(f"[supervisor] cleaned sessions for {agent}")
            else:
                print(f"[supervisor] session cleanup for {agent}: {result.stderr[:100]}")
        except Exception as e:
            print(f"[supervisor] session cleanup for {agent} failed: {e}")


def _validate_schema(artifact_path: Path, schema_name: str) -> None:
    """Validate artifact against schema. Raises on failure."""
    data = read_json(artifact_path)
    valid, errors = validate_artifact(data, schema_name)
    if not valid:
        error_str = "; ".join(str(e) for e in errors[:3])
        raise RuntimeError(f"Schema validation failed for {artifact_path.name} ({schema_name}): {error_str}")
    print(f"[supervisor] schema OK: {artifact_path.name} -> {schema_name}")


def _file_must_exist(p: Path, label: str) -> None:
    if not p.exists():
        raise RuntimeError(f"Expected artifact missing: {label} at {p}")
    print(f"[supervisor] artifact exists: {label}")


# ---------------------------------------------------------------------------
# Phase definitions
# ---------------------------------------------------------------------------

def run_supervisor(bootstrap_path: Path) -> None:
    """Run the full S5 chain with checkpoint-resume."""

    run_start = time.time()
    phase_durations: dict[str, float] = {}
    last_successful_phase = "none"

    def _phase_timer(phase_name: str):
        return time.time()

    def _record_phase(phase_name: str, start_time: float):
        duration = round(time.time() - start_time, 1)
        phase_durations[phase_name] = duration
        return duration

    # --- Bootstrap ---
    bootstrap = load_bootstrap(bootstrap_path)
    sr = Path(bootstrap["sector_root"]).resolve()
    job_id = bootstrap["job_id"]
    video_id = bootstrap["video_id"]
    account_id = bootstrap["account_id"]
    language = bootstrap["language"]
    upstream = bootstrap["upstream"]

    print(f"[supervisor] starting S5 for job={job_id}, sector_root={sr}")

    # Clean sessions
    _clean_s5_sessions()

    # Create dirs (idempotent)
    create_s5_directories(sr)

    # Read completed phases for resume
    done = get_completed_phases(sr)
    if done:
        print(f"[supervisor] resuming - phases already done: {sorted(done)}")

    try:
        # === PHASE: bootstrap ===
        if "bootstrap" not in done:
            t0 = _phase_timer("bootstrap")
            write_sector_status(sr, phase="bootstrap", status="started", details={
                "job_id": job_id, "video_id": video_id,
                "account_id": account_id, "language": language,
            })
            write_checkpoint(sr, event="s5_bootstrap_started", data={"job_id": job_id})
            dur = _record_phase("bootstrap", t0)
            write_phase_checkpoint(sr, "bootstrap", "done", job_id,
                                   artifacts=None, duration_seconds=dur)
            print(f"[supervisor] phase: bootstrap DONE ({dur}s)")
        else:
            print("[supervisor] phase: bootstrap SKIPPED (already done)")
        last_successful_phase = "bootstrap"

        # === PHASE: input_assembly ===
        if "input_assembly" not in done:
            t0 = _phase_timer("input_assembly")
            write_sector_status(sr, phase="input_assembly", status="running")
            print("[supervisor] running input_assembly helper...")
            cmd = [
                sys.executable, str(HELPERS_DIR / "input_assembly.py"),
                upstream["source_package_path"],
                upstream["compiled_entities_path"],
                upstream["research_intake_path"],
                upstream["reference_ready_asset_pool_path"],
                str(sr), job_id,
            ]
            result = subprocess.run(cmd, capture_output=True, text=True,
                                    timeout=HELPER_TIMEOUT_INPUT_ASSEMBLY)
            if result.stdout:
                for line in result.stdout.strip().split("\n")[-10:]:
                    print(f"[supervisor] {line}")
            if result.returncode != 0:
                raise RuntimeError(f"input_assembly failed: {result.stderr[:500]}")

            # Validate: at least 1 package exists
            pkg_dir = sr / "scene_direction_input_packages"
            pkgs = list(pkg_dir.glob("*.json"))
            if not pkgs:
                raise RuntimeError("input_assembly produced no packages")
            print(f"[supervisor] input_assembly: {len(pkgs)} packages written")

            dur = _record_phase("input_assembly", t0)
            write_phase_checkpoint(sr, "input_assembly", "done", job_id,
                                   artifacts=[str(pkg_dir)], duration_seconds=dur)
            print(f"[supervisor] phase: input_assembly DONE ({dur}s)")
        else:
            print("[supervisor] phase: input_assembly SKIPPED (already done)")
        last_successful_phase = "input_assembly"

        # === PHASE: direction_frame ===
        dfp = direction_frame_path(sr)
        if "direction_frame" not in done:
            t0 = _phase_timer("direction_frame")
            write_sector_status(sr, phase="direction_frame", status="running")
            print("[supervisor] running direction_frame_builder helper...")
            cmd = [
                sys.executable, str(HELPERS_DIR / "direction_frame_builder.py"),
                upstream["video_context_path"],
                upstream["compiled_entities_path"],
                upstream["source_package_path"],
                str(sr), job_id,
            ]
            result = subprocess.run(cmd, capture_output=True, text=True,
                                    timeout=HELPER_TIMEOUT_DIRECTION_FRAME)
            if result.stdout:
                for line in result.stdout.strip().split("\n")[-5:]:
                    print(f"[supervisor] {line}")
            if result.returncode != 0:
                raise RuntimeError(f"direction_frame_builder failed: {result.stderr[:500]}")

            _file_must_exist(dfp, "video_direction_frame.json")
            _validate_schema(dfp, "video_direction_frame")
            dur = _record_phase("direction_frame", t0)
            write_phase_checkpoint(sr, "direction_frame", "done", job_id,
                                   artifacts=[str(dfp)], duration_seconds=dur)
            print(f"[supervisor] phase: direction_frame DONE ({dur}s)")
        else:
            print("[supervisor] phase: direction_frame SKIPPED (already done)")
        last_successful_phase = "direction_frame"

        # === PHASE: scene_kit_design ===
        if "scene_kit_design" not in done:
            t0 = _phase_timer("scene_kit_design")
            write_sector_status(sr, phase="scene_kit_design", status="running")
            print("[supervisor] running scene_kit_designer helper...")
            cmd = [
                sys.executable, str(HELPERS_DIR / "scene_kit_designer.py"),
                str(sr), job_id,
            ]
            result = subprocess.run(cmd, capture_output=True, text=True,
                                    timeout=HELPER_TIMEOUT_SCENE_KIT_DESIGN)
            if result.stdout:
                for line in result.stdout.strip().split("\n")[-10:]:
                    print(f"[supervisor] {line}")
            if result.returncode != 0:
                raise RuntimeError(f"scene_kit_designer failed: {result.stderr[:500]}")

            # Validate: at least 1 spec exists
            specs = list((sr / "scene_kit_specs").glob("*.json"))
            if not specs:
                raise RuntimeError("scene_kit_designer produced no specs")
            print(f"[supervisor] scene_kit_design: {len(specs)} specs written")

            dur = _record_phase("scene_kit_design", t0)
            write_phase_checkpoint(sr, "scene_kit_design", "done", job_id,
                                   artifacts=[str(sr / "scene_kit_specs")],
                                   duration_seconds=dur)
            print(f"[supervisor] phase: scene_kit_design DONE ({dur}s)")
        else:
            print("[supervisor] phase: scene_kit_design SKIPPED (already done)")
        last_successful_phase = "scene_kit_design"

        # === PHASE: compile ===
        if "compile" not in done:
            t0 = _phase_timer("compile")
            write_sector_status(sr, phase="compile", status="running")
            print("[supervisor] running pack_compiler helper...")
            cmd = [
                sys.executable, str(HELPERS_DIR / "pack_compiler.py"),
                str(sr), job_id, video_id, account_id, language,
            ]
            result = subprocess.run(cmd, capture_output=True, text=True,
                                    timeout=HELPER_TIMEOUT_COMPILE)
            if result.stdout:
                for line in result.stdout.strip().split("\n")[-5:]:
                    print(f"[supervisor] {line}")
            if result.returncode != 0:
                raise RuntimeError(f"pack_compiler failed: {result.stderr[:500]}")

            pkp = scene_kit_pack_path(sr)
            srp = sector_report_path(sr)
            _file_must_exist(pkp, "s5_scene_kit_pack.json")
            _file_must_exist(srp, "s5_sector_report.md")
            _validate_schema(pkp, "s5_scene_kit_pack")

            dur = _record_phase("compile", t0)
            write_phase_checkpoint(sr, "compile", "done", job_id,
                                   artifacts=[str(pkp), str(srp)],
                                   duration_seconds=dur)
            print(f"[supervisor] phase: compile DONE ({dur}s)")
        else:
            print("[supervisor] phase: compile SKIPPED (already done)")
        last_successful_phase = "compile"

        # === CLOSURE ===
        pkp = scene_kit_pack_path(sr)
        srp = sector_report_path(sr)
        specs_dir = sr / "scene_kit_specs"
        specs = list(specs_dir.glob("*.json"))
        pkg_dir = sr / "scene_direction_input_packages"
        pkgs = list(pkg_dir.glob("*.json"))

        write_completion(
            sr, job_id,
            video_direction_frame_path=str(direction_frame_path(sr)),
            scene_kit_specs_dir=str(specs_dir),
            scene_kit_pack_path=str(pkp),
            sector_report_path=str(srp),
            scene_count_total=len(pkgs),
            scene_kit_specs_generated=len(specs),
            scene_kit_specs_valid=len(specs),
        )
        write_sector_status(sr, phase="completed", status="completed")

        # Run summary
        total_duration = round(time.time() - run_start, 1)
        _print_run_summary(sr, job_id, video_id, account_id, phase_durations,
                           total_duration, len(pkgs), len(specs))

    except Exception as e:
        print(f"[supervisor] FATAL ERROR: {e}")
        write_failure(sr, job_id, str(e), last_successful_phase=last_successful_phase)
        write_sector_status(sr, phase="failed", status="failed")
        raise


def _print_run_summary(
    sr: Path, job_id: str, video_id: str, account_id: str,
    phase_durations: dict, total_duration: float,
    total_scenes: int, total_specs: int,
) -> None:
    """Print structured run summary."""
    mins = int(total_duration // 60)
    secs = int(total_duration % 60)

    # Read usage if available
    up = usage_path(sr)
    usage_info = ""
    if up.exists():
        usage = read_json(up)
        total_calls = 0
        for phase_name, phase_data in usage.items():
            if isinstance(phase_data, dict) and "usage" in phase_data:
                total_calls += phase_data["usage"].get("calls", 0)
        usage_info = f"  LLM calls: {total_calls}"

    print()
    print("=" * 60)
    print("  S5 SECTOR SUMMARY")
    print("=" * 60)
    print(f"  Job: {job_id}")
    print(f"  Video: {video_id} | Account: {account_id}")
    print(f"  Duration: {mins}m {secs}s")
    print(f"  Scenes: {total_scenes} total | {total_specs} specs generated")
    if usage_info:
        print(usage_info)
    print()
    print("  Phase durations:")
    for phase, dur in phase_durations.items():
        print(f"    {phase}: {dur}s")
    print("=" * 60)
    print()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: supervisor_shell.py <bootstrap_path>")

    bootstrap_path = Path(sys.argv[1]).resolve()
    run_supervisor(bootstrap_path)
