"""S4 Asset Pipeline — unified orchestrator for visual asset retrieval.

Uses GPT-5.4-nano via OpenAI API for query generation + visual evaluation.
No KMS, no Gemini, no cascade. 1 AsyncOpenAI client, Semaphore(10).
Tracks token usage and cost across all steps.

Steps:
  0. Context extraction (GPT-5.4-nano infers era, style, subject from script)
  1. Query generation (GPT-5.4-nano generates 2 queries per target)
  2. Image collection (Serper.dev + download + pHash dedup)
  3. Visual evaluation (GPT-5.4-nano vision, batches of 5, relevance >= 7 → assets/)

CLI: python s4_asset_pipeline.py <intake_path> <sector_root> <job_id>
"""
import asyncio
import json
import sys
import time
import threading
from pathlib import Path

# Add helpers dir to path for local imports
HELPERS_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(HELPERS_DIR))

from openai import AsyncOpenAI

from artifact_io import read_json, write_json
from s4_query_generator import generate_all_queries
from s4_image_collector import collect_all_targets
from s4_visual_evaluator import evaluate_all_targets

MODEL = "gpt-5.4-nano"
OPENAI_API_KEY = "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"

# GPT-5.4-nano pricing (per 1M tokens)
COST_INPUT_PER_M = 0.20
COST_OUTPUT_PER_M = 1.25


class UsageTracker:
    """Thread-safe token usage tracker for OpenAI API calls."""

    def __init__(self):
        self._lock = threading.Lock()
        self.input_tokens = 0
        self.output_tokens = 0
        self.calls = 0

    def track(self, usage):
        """Track usage from an OpenAI response.usage object."""
        if usage is None:
            return
        with self._lock:
            self.input_tokens += getattr(usage, "prompt_tokens", 0) or 0
            self.output_tokens += getattr(usage, "completion_tokens", 0) or 0
            self.calls += 1

    @property
    def cost_input(self) -> float:
        return self.input_tokens / 1_000_000 * COST_INPUT_PER_M

    @property
    def cost_output(self) -> float:
        return self.output_tokens / 1_000_000 * COST_OUTPUT_PER_M

    @property
    def cost_total(self) -> float:
        return self.cost_input + self.cost_output

    def summary(self) -> str:
        return (
            f"  API calls: {self.calls}\n"
            f"  Input tokens: {self.input_tokens:,}\n"
            f"  Output tokens: {self.output_tokens:,}\n"
            f"  Cost: ${self.cost_total:.4f} "
            f"(input: ${self.cost_input:.4f}, output: ${self.cost_output:.4f})"
        )


async def extract_video_context(
    intake_path: Path,
    sector_root: Path,
    client: AsyncOpenAI,
    tracker: UsageTracker,
) -> dict:
    """Extract video context (era, style, subject, locations) from the script."""
    sr = sector_root.resolve()
    intake = read_json(intake_path)
    metadata = intake.get("metadata", {})

    source_package_path = metadata.get("generated_from", "")
    scenes_text = ""

    if source_package_path:
        compiled_path = Path(source_package_path)
        source_pkg_path = compiled_path.parent.parent / "inputs" / "s3_source_package.json"
        if source_pkg_path.exists():
            source_pkg = read_json(source_pkg_path)
            scenes = source_pkg.get("scenes", [])
            for s in scenes[:20]:
                scenes_text += f"[{s.get('scene_id', '')}] {s.get('text', '')}\n"

    video_dir_name = ""
    video_dir = sr.parent.parent.parent
    if video_dir.exists():
        video_dir_name = video_dir.name.replace("_", " ").replace("-", " — ")

    if not scenes_text and not video_dir_name:
        print("[context] WARNING: no script or video name found, using empty context")
        return _empty_context()

    prompt = "Analyze this documentary video script and extract structured context.\n\n"
    if video_dir_name:
        prompt += f"VIDEO TITLE (from directory): {video_dir_name}\n\n"
    if scenes_text:
        prompt += f"FIRST SCENES OF THE SCRIPT:\n{scenes_text}\n\n"

    prompt += (
        "Extract the following as JSON:\n"
        "{\n"
        '  "title": "the video title in its original language",\n'
        '  "subject": "the main subject of the documentary (building, event, person, etc.)",\n'
        '  "era": "the historical period covered (e.g. 1940-1950, WWII, Medieval)",\n'
        '  "style": "the documentary style/tone (e.g. nostalgic historical, military, architectural)",\n'
        '  "key_locations": ["list of specific locations mentioned"],\n'
        '  "key_people": ["list of specific people mentioned"],\n'
        '  "visual_era_guidance": "brief description of what visual era is appropriate for images — what should be accepted and what looks anachronistic"\n'
        "}\n\n"
        "Respond ONLY with valid JSON."
    )

    try:
        resp = await client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_completion_tokens=1024,
            response_format={"type": "json_object"},
        )
        tracker.track(resp.usage)
        ctx = json.loads(resp.choices[0].message.content)
        print(f"[context] extracted: {ctx.get('title', '?')} | era={ctx.get('era', '?')} | style={ctx.get('style', '?')}")
        return ctx
    except Exception as e:
        print(f"[context] extraction failed: {e}, using fallback")
        return _empty_context()


def _empty_context() -> dict:
    return {
        "title": "",
        "subject": "",
        "era": "",
        "style": "",
        "key_locations": [],
        "key_people": [],
        "visual_era_guidance": "",
    }


async def run_pipeline(intake_path: Path, sector_root: Path, job_id: str) -> None:
    """Run the full asset pipeline: context → query gen → collection → evaluation."""
    sr = sector_root.resolve()
    ip = intake_path.resolve()
    intake = read_json(ip)

    # 1 shared AsyncOpenAI client + usage tracker
    client = AsyncOpenAI(api_key=OPENAI_API_KEY)
    tracker = UsageTracker()

    total_targets = len(intake.get("research_targets", []))
    print(f"[asset_pipeline] starting for {total_targets} targets (job={job_id})")
    print(f"[asset_pipeline] using GPT-5.4-nano via OpenAI API")
    pipeline_start = time.time()

    # Step 0: Context Extraction
    t0 = time.time()
    print(f"\n{'='*50}")
    print(f"  STEP 0/3: CONTEXT EXTRACTION")
    print(f"{'='*50}")
    video_context = await extract_video_context(ip, sr, client, tracker)
    ctx_path = sr / "runtime" / "video_context.json"
    ctx_path.parent.mkdir(parents=True, exist_ok=True)
    write_json(ctx_path, video_context)
    dur0 = round(time.time() - t0, 1)
    print(f"[asset_pipeline] step 0 done ({dur0}s)")

    # Step 1: Query Generation
    t0 = time.time()
    print(f"\n{'='*50}")
    print(f"  STEP 1/3: QUERY GENERATION")
    print(f"{'='*50}")
    query_results = await generate_all_queries(ip, sr, client, video_context, tracker)
    total_queries = sum(len(r["queries"]) for r in query_results)
    dur1 = round(time.time() - t0, 1)
    print(f"[asset_pipeline] step 1 done: {len(query_results)} targets, {total_queries} queries ({dur1}s)")

    # Step 2: Image Collection (Serper + download + dedup)
    t0 = time.time()
    print(f"\n{'='*50}")
    print(f"  STEP 2/3: IMAGE COLLECTION")
    print(f"{'='*50}")
    collect_results = await collect_all_targets(ip, sr)
    total_downloaded = sum(r["downloaded"] for r in collect_results)
    total_dedup = sum(r["duplicates_removed"] for r in collect_results)
    dur2 = round(time.time() - t0, 1)
    print(f"[asset_pipeline] step 2 done: {total_downloaded} images, {total_dedup} deduped ({dur2}s)")

    # Step 3: Visual Evaluation (GPT-5.4-nano vision)
    t0 = time.time()
    print(f"\n{'='*50}")
    print(f"  STEP 3/3: VISUAL EVALUATION")
    print(f"{'='*50}")
    await evaluate_all_targets(ip, sr, client, job_id, video_context, tracker)
    dur3 = round(time.time() - t0, 1)
    print(f"[asset_pipeline] step 3 done ({dur3}s)")

    # Summary
    total_duration = round(time.time() - pipeline_start, 1)
    mins = int(total_duration // 60)
    secs = int(total_duration % 60)

    print(f"\n{'='*50}")
    print(f"  ASSET PIPELINE COMPLETE")
    print(f"{'='*50}")
    print(f"  Video: {video_context.get('title', '?')}")
    print(f"  Era: {video_context.get('era', '?')}")
    print(f"  Targets: {total_targets}")
    print(f"  Queries: {total_queries}")
    print(f"  Images downloaded: {total_downloaded}")
    print(f"  Duplicates removed: {total_dedup}")
    print(f"  Duration: {mins}m {secs}s")
    print(f"    Step 0 (context): {dur0}s")
    print(f"    Step 1 (queries): {dur1}s")
    print(f"    Step 2 (collect): {dur2}s")
    print(f"    Step 3 (evaluate): {dur3}s")
    print(f"  --- GPT-5.4-nano Usage ---")
    print(tracker.summary())
    print(f"{'='*50}\n")

    # Save usage report
    usage_path = sr / "runtime" / "openai_usage.json"
    write_json(usage_path, {
        "model": MODEL,
        "calls": tracker.calls,
        "input_tokens": tracker.input_tokens,
        "output_tokens": tracker.output_tokens,
        "cost_input": round(tracker.cost_input, 6),
        "cost_output": round(tracker.cost_output, 6),
        "cost_total": round(tracker.cost_total, 6),
    })


if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise SystemExit("usage: s4_asset_pipeline.py <intake_path> <sector_root> <job_id>")
    asyncio.run(run_pipeline(Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]))
