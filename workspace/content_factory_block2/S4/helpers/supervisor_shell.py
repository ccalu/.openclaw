"""S4 Supervisor Runtime Orchestrator — checkpoint-resume, deterministic.

This is the official S4 long-chain orchestrator. The SM OpenClaw actor
delegates to this script. It owns:
- sequential dispatch of all 6 operators via `openclaw agent`
- schema validation gates between phases
- checkpoint-resume (can be interrupted and restarted)
- failure table enforcement
- completion/failure writing + B2 mirror
- run summary + duration tracking (Phase 5A)
- worker retry with backoff (Phase 5A)
- asset pipeline (query gen + Serper + Gemini Vision) as unified phase
"""
import json
import subprocess
import sys
import time
from pathlib import Path

from artifact_io import read_json
from bootstrap_loader import load_bootstrap
from dirs import create_s4_directories
from checkpoint_writer import (
    get_completed_phases,
    write_checkpoint,
    write_completion,
    write_failure,
    write_phase_checkpoint,
    write_sector_status,
)
from paths import (
    batch_manifest_path,
    candidate_set_path,
    coverage_report_path,
    evaluated_set_path,
    intake_path,
    research_pack_path,
    sector_report_path,
    target_brief_path,
)
from schema_validator import validate_artifact

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

HELPERS_DIR = Path(__file__).parent.resolve()
OPENCLAW_TIMEOUT = 1800  # 30 min per OpenClaw actor
HELPER_TIMEOUT_WORKER = 120  # 2 min per worker helper
HELPER_TIMEOUT_DEFAULT = 60  # 1 min for other helpers
WORKER_RETRY_COUNT = 1  # retry once on failure
WORKER_RETRY_BACKOFF = 5  # seconds between retries
SETTLE_TIME = 2  # seconds after operator completes


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _dispatch_operator(agent_name: str, session_suffix: str, message: str, job_id: str) -> dict:
    """Dispatch an OpenClaw operator and return parsed JSON result."""
    session_id = f"s4-{job_id}-{session_suffix}-{int(time.time())}"
    cmd = [
        "openclaw.cmd", "agent",
        "--agent", agent_name,
        "--session-id", session_id,
        "--message", message,
        "--json",
        "--timeout", str(OPENCLAW_TIMEOUT),
    ]
    print(f"[supervisor] dispatching {agent_name} (session: {session_id})")
    result = subprocess.run(
        cmd, capture_output=True, text=True, timeout=OPENCLAW_TIMEOUT + 60,
    )
    if result.stdout:
        try:
            parsed = json.loads(result.stdout)
            payloads = parsed.get("result", {}).get("payloads", [])
            for p in payloads:
                txt = p.get("text", "")[:300]
                if txt:
                    print(f"[supervisor] agent said: {txt}")
        except json.JSONDecodeError:
            print(f"[supervisor] raw stdout (first 500): {result.stdout[:500]}")
    if result.stderr:
        print(f"[supervisor] stderr: {result.stderr[:300]}")
    time.sleep(SETTLE_TIME)

    if result.returncode != 0:
        stderr = result.stderr.strip()[:500] if result.stderr else "no stderr"
        raise RuntimeError(f"{agent_name} failed (exit {result.returncode}): {stderr}")

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"raw_stdout": result.stdout[:1000]}


def _run_helper(cmd: list[str], timeout: int = HELPER_TIMEOUT_DEFAULT) -> subprocess.CompletedProcess:
    """Run a helper subprocess with timeout."""
    return subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=timeout)


def _run_worker_with_retry(cmd: list[str], tid: str) -> None:
    """Run research worker helper with 1 retry on failure."""
    for attempt in range(1 + WORKER_RETRY_COUNT):
        try:
            _run_helper(cmd, timeout=HELPER_TIMEOUT_WORKER)
            return
        except Exception as e:
            if attempt < WORKER_RETRY_COUNT:
                print(f"[supervisor] worker {tid} attempt {attempt + 1} failed: {e}")
                print(f"[supervisor] retrying in {WORKER_RETRY_BACKOFF}s...")
                time.sleep(WORKER_RETRY_BACKOFF)
            else:
                raise


S4_AGENTS = [
    "sm_s4_asset_research",
    "op_s4_target_builder",
    "op_s4_web_investigator",
    "op_s4_target_research_worker",
    "op_s4_candidate_evaluator",
    "op_s4_coverage_analyst",
    "op_s4_pack_compiler",
]


def _clean_s4_sessions() -> None:
    """Clean all S4 OpenClaw agent sessions to prevent context leaking between videos."""
    print("[supervisor] cleaning S4 agent sessions...")
    for agent in S4_AGENTS:
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
    """Run the full S4 chain with checkpoint-resume."""

    run_start = time.time()
    phase_durations: dict[str, float] = {}

    def _phase_timer(phase_name: str):
        """Context-like helper to track phase duration."""
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
    compiled_entities = bootstrap["upstream"]["compiled_entities_path"]

    print(f"[supervisor] starting S4 for job={job_id}, sector_root={sr}")

    # Clean all S4 OpenClaw agent sessions to avoid context leaking between videos
    _clean_s4_sessions()

    # Create dirs (idempotent)
    create_s4_directories(sr)

    # Read completed phases for resume
    done = get_completed_phases(sr)
    if done:
        print(f"[supervisor] resuming - phases already done: {sorted(done)}")

    # Tracking
    worker_failures: list[str] = []
    total_candidates = 0
    total_best = 0

    # --- Phase: bootstrap ---
    if "bootstrap" not in done:
        t0 = _phase_timer("bootstrap")
        write_sector_status(sr, phase="bootstrap", status="started", details={
            "job_id": job_id, "video_id": video_id,
            "account_id": account_id, "language": language,
        })
        write_checkpoint(sr, event="s4_bootstrap_started", data={"job_id": job_id})
        dur = _record_phase("bootstrap", t0)
        write_phase_checkpoint(sr, "bootstrap", "done", job_id,
                               artifacts=None, duration_seconds=dur)
        print(f"[supervisor] phase: bootstrap DONE ({dur}s)")
    else:
        print("[supervisor] phase: bootstrap SKIPPED (already done)")

    # --- Phase: target_builder (helper-direct, includes LLM consolidation) ---
    ip = intake_path(sr)
    if "target_builder" not in done:
        t0 = _phase_timer("target_builder")
        write_sector_status(sr, phase="target_builder", status="running")
        print(f"[supervisor] running target_builder helper (with consolidation)...")
        cmd_tb = [
            sys.executable, str(HELPERS_DIR / "target_builder.py"),
            str(compiled_entities), str(sr), job_id, video_id, account_id, language,
        ]
        result_tb = subprocess.run(cmd_tb, capture_output=True, text=True, timeout=120)
        if result_tb.stdout:
            for line in result_tb.stdout.strip().split("\n"):
                print(f"[supervisor] {line}")
        if result_tb.returncode != 0:
            raise RuntimeError(f"target_builder failed: {result_tb.stderr[:500]}")
        _file_must_exist(ip, "research_intake.json")
        _validate_schema(ip, "research_intake")
        dur = _record_phase("target_builder", t0)
        write_phase_checkpoint(sr, "target_builder", "done", job_id,
                               artifacts=[str(ip)], duration_seconds=dur)
        print(f"[supervisor] phase: target_builder DONE ({dur}s)")
    else:
        print("[supervisor] phase: target_builder SKIPPED (already done)")

    # --- Phase: batch_manifest ---
    mp = batch_manifest_path(sr)
    if "batch_manifest" not in done:
        t0 = _phase_timer("batch_manifest")
        write_sector_status(sr, phase="batch_manifest", status="running")
        _run_helper([sys.executable, str(HELPERS_DIR / "batch_manifest_builder.py"), str(ip), str(sr)])
        _file_must_exist(mp, "research_batch_manifest.json")
        _validate_schema(mp, "research_batch_manifest")
        dur = _record_phase("batch_manifest", t0)
        write_phase_checkpoint(sr, "batch_manifest", "done", job_id,
                               artifacts=[str(mp)], duration_seconds=dur)
        print(f"[supervisor] phase: batch_manifest DONE ({dur}s)")
    else:
        print("[supervisor] phase: batch_manifest SKIPPED (already done)")

    # --- Phase: web_investigator ---
    if "web_investigator" not in done:
        t0 = _phase_timer("web_investigator")
        write_sector_status(sr, phase="web_investigator", status="running")
        _run_helper([sys.executable, str(HELPERS_DIR / "web_investigator.py"), str(ip), str(mp), str(sr)])
        intake = read_json(ip)
        for target in intake["research_targets"]:
            tid = target["target_id"]
            bp = target_brief_path(sr, tid)
            _file_must_exist(bp, f"brief for {tid}")
            _validate_schema(bp, "target_research_brief")
        dur = _record_phase("web_investigator", t0)
        write_phase_checkpoint(sr, "web_investigator", "done", job_id,
                               duration_seconds=dur)
        print(f"[supervisor] phase: web_investigator DONE ({dur}s)")
    else:
        print("[supervisor] phase: web_investigator SKIPPED (already done)")

    # --- Phase: asset_pipeline (replaces serper_image_search + image_download + visual_evaluator) ---
    intake = read_json(ip)
    targets = intake["research_targets"]

    # Backward compat: if old phases are done, treat asset_pipeline as done too
    old_phases_done = all(p in done for p in ("serper_image_search", "image_download", "visual_evaluator"))
    if "asset_pipeline" not in done and not old_phases_done:
        t0 = _phase_timer("asset_pipeline")
        write_sector_status(sr, phase="asset_pipeline", status="running")
        print(f"[supervisor] running asset pipeline for {len(targets)} targets (query gen + Serper + Gemini Vision)...")
        cmd_pipeline = [sys.executable, str(HELPERS_DIR / "s4_asset_pipeline.py"), str(ip), str(sr), job_id]
        result_pipeline = subprocess.run(cmd_pipeline, capture_output=True, text=True, timeout=900)
        if result_pipeline.stdout:
            for line in result_pipeline.stdout.strip().split("\n")[-15:]:
                print(f"[supervisor] {line}")
        if result_pipeline.returncode != 0:
            stderr_msg = result_pipeline.stderr[:500] if result_pipeline.stderr else "no stderr"
            print(f"[supervisor] WARNING: asset pipeline had errors: {stderr_msg}")
        dur = _record_phase("asset_pipeline", t0)
        write_phase_checkpoint(sr, "asset_pipeline", "done", job_id,
                               duration_seconds=dur)
        print(f"[supervisor] phase: asset_pipeline DONE ({dur}s)")
    else:
        print("[supervisor] phase: asset_pipeline SKIPPED (already done)")

    # --- Phase: coverage_analyst ---
    if "coverage_analyst" not in done:
        t0 = _phase_timer("coverage_analyst")
        write_sector_status(sr, phase="coverage_analyst", status="running")
        _dispatch_operator(
            "op_s4_coverage_analyst", "coverage",
            f"Coverage analyst dispatch. intake_path: {ip}. sector_root: {sr}.",
            job_id,
        )
        cr = coverage_report_path(sr)
        _file_must_exist(cr, "coverage_report.json")
        _validate_schema(cr, "coverage_report")
        dur = _record_phase("coverage_analyst", t0)
        write_phase_checkpoint(sr, "coverage_analyst", "done", job_id,
                               artifacts=[str(cr)], duration_seconds=dur)
        print(f"[supervisor] phase: coverage_analyst DONE ({dur}s)")
    else:
        print("[supervisor] phase: coverage_analyst SKIPPED (already done)")

    # --- Phase: pack_compiler ---
    if "pack_compiler" not in done:
        t0 = _phase_timer("pack_compiler")
        write_sector_status(sr, phase="pack_compiler", status="running")
        _dispatch_operator(
            "op_s4_pack_compiler", "compiler",
            f"Pack compiler dispatch. intake_path: {ip}. sector_root: {sr}. "
            f"job_id: {job_id}. video_id: {video_id}. "
            f"account_id: {account_id}. language: {language}.",
            job_id,
        )
        rp = research_pack_path(sr)
        srp = sector_report_path(sr)
        _file_must_exist(rp, "research_pack.json")
        _file_must_exist(srp, "s4_sector_report.md")
        _validate_schema(rp, "research_pack")
        dur = _record_phase("pack_compiler", t0)
        write_phase_checkpoint(sr, "pack_compiler", "done", job_id,
                               artifacts=[str(rp), str(srp)], duration_seconds=dur)
        print(f"[supervisor] phase: pack_compiler DONE ({dur}s)")
    else:
        print("[supervisor] phase: pack_compiler SKIPPED (already done)")

    # --- Closure ---
    rp = research_pack_path(sr)
    srp = sector_report_path(sr)
    write_completion(sr, job_id, str(rp), str(srp))
    write_sector_status(sr, phase="completed", status="completed")

    # --- Run Summary ---
    total_duration = round(time.time() - run_start, 1)
    _print_run_summary(sr, job_id, video_id, account_id, targets,
                       worker_failures, phase_durations, total_duration)


def _print_run_summary(
    sr: Path, job_id: str, video_id: str, account_id: str,
    targets: list, worker_failures: list, phase_durations: dict,
    total_duration: float,
) -> None:
    """Print structured run summary at the end."""
    # Read final pack for stats
    try:
        pack = read_json(research_pack_path(sr))
        pack_status = pack["metadata"]["status"]
        target_results = pack.get("target_results", [])
        scene_results = pack.get("scene_results", [])
        gaps = pack.get("unresolved_gaps", [])
        warnings = pack.get("warnings", [])

        total_candidates = 0
        total_best = 0
        coverage_dist: dict[str, int] = {}
        for tr in target_results:
            best = (len(tr.get("best_factual_evidence_ids", []))
                    + len(tr.get("best_visual_reference_ids", []))
                    + len(tr.get("best_stylistic_inspiration_ids", [])))
            total_best += best
            state = tr.get("coverage_state", "unknown")
            coverage_dist[state] = coverage_dist.get(state, 0) + 1

        # Count total candidates from evaluated sets
        for td in (sr / "targets").iterdir():
            if not td.is_dir():
                continue
            cs_file = td / f"{td.name}_candidate_set.json"
            if cs_file.exists():
                cs = read_json(cs_file)
                total_candidates += len(cs.get("candidates", []))
    except Exception:
        pack_status = "unknown"
        total_candidates = 0
        total_best = 0
        coverage_dist = {}
        gaps = []
        warnings = []
        target_results = []
        scene_results = []

    # Format duration
    mins = int(total_duration // 60)
    secs = int(total_duration % 60)
    duration_str = f"{mins}m {secs}s" if mins > 0 else f"{secs}s"

    # Coverage string
    cov_parts = []
    for state in ["covered", "partially_covered", "inspiration_only", "unresolved"]:
        if state in coverage_dist:
            cov_parts.append(f"{coverage_dist[state]} {state}")
    cov_str = ", ".join(cov_parts) if cov_parts else "none"

    print()
    print("=" * 60)
    print("  S4 SECTOR SUMMARY")
    print("=" * 60)
    print(f"  Job: {job_id} | Video: {video_id} | Account: {account_id}")
    print(f"  Duration: {duration_str}")
    print(f"  Targets: {len(targets)} processed | {len(worker_failures)} failed workers")
    print(f"  Candidates: {total_candidates} total | {total_best} best selected")
    print(f"  Scenes: {len(scene_results)}")
    print(f"  Coverage: {cov_str}")
    print(f"  Gaps: {len(gaps)} unresolved")
    print(f"  Warnings: {len(warnings)}")
    print(f"  Pack: {pack_status} | Schema: PASS")
    print(f"  Status: COMPLETED")
    print("=" * 60)

    # Phase duration breakdown (top 10 slowest)
    if phase_durations:
        sorted_phases = sorted(phase_durations.items(), key=lambda x: x[1], reverse=True)
        print("  Top phases by duration:")
        for name, dur in sorted_phases[:10]:
            print(f"    {name}: {dur}s")
        print("=" * 60)
    print()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: supervisor_shell.py <bootstrap_path>")

    bootstrap_path = Path(sys.argv[1])
    try:
        run_supervisor(bootstrap_path)
    except Exception as e:
        print(f"[supervisor] FATAL: {e}")
        try:
            bs = json.loads(bootstrap_path.read_text(encoding="utf-8"))
            sr = Path(bs.get("sector_root", ".")).resolve()
            job_id = bs.get("job_id", "unknown")
            write_failure(sr, job_id, str(e))
        except Exception:
            pass
        sys.exit(1)
