"""S4 Query Generator — GPT-5.4-nano generates 2 diverse search queries per target.

Uses OpenAI API directly (no KMS). Receives video_context to anchor queries
to the specific video subject, era, and locations.
"""
import asyncio
import json
import sys
from pathlib import Path

from openai import AsyncOpenAI

from artifact_io import read_json, write_json, utc_now
from paths import sanitize_target_id, search_queries_path

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"
MODEL = "gpt-5.4-nano"
QUERY_SEMAPHORE_LIMIT = 10


def _build_context_block(video_context: dict) -> str:
    """Build the VIDEO CONTEXT block to inject into the query prompt."""
    if not video_context or not video_context.get("title"):
        return ""

    parts = ["VIDEO CONTEXT (all queries MUST be anchored to this):"]
    if video_context.get("title"):
        parts.append(f"  Title: {video_context['title']}")
    if video_context.get("subject"):
        parts.append(f"  Subject: {video_context['subject']}")
    if video_context.get("era"):
        parts.append(f"  Era: {video_context['era']}")
    if video_context.get("style"):
        parts.append(f"  Style: {video_context['style']}")
    if video_context.get("key_locations"):
        parts.append(f"  Key locations: {', '.join(video_context['key_locations'])}")

    parts.append("")
    parts.append("CRITICAL RULE: Do NOT search for the generic concept.")
    parts.append("Every query must be anchored to the video's specific subject.")
    parts.append('Example: if target is "lago artificial" and the video is about Hotel Quitandinha,')
    parts.append('search "lago artificial Hotel Quitandinha Petrópolis" NOT "artificial lake".')
    parts.append('Example: if target is "cassino" and the video is about Hotel Quitandinha,')
    parts.append('search "cassino Hotel Quitandinha" NOT "casino Italy".')
    parts.append("")

    return "\n".join(parts)


async def generate_queries_for_target(
    target: dict,
    brief: dict,
    client: AsyncOpenAI,
    system_prompt: str,
    video_context: dict,
    tracker=None,
) -> dict:
    """Generate 2 search queries for one target via GPT-5.4-nano."""
    tid = target["target_id"]
    label = target["canonical_label"]
    target_type = target.get("target_type", "")

    user_input = {
        "target_id": tid,
        "canonical_label": label,
        "target_type": target_type,
        "search_goals": brief.get("search_goals", []),
        "research_needs": brief.get("research_needs", f"Visual references for {label}"),
        "context": brief.get("context", target.get("context", "")),
    }

    context_block = _build_context_block(video_context)

    user_prompt = (
        f"{context_block}"
        "Generate exactly 2 diverse Google Images search queries for this target.\n\n"
        f"TARGET:\n{json.dumps(user_input, indent=2, ensure_ascii=False)}\n\n"
        "Respond ONLY with valid JSON."
    )

    try:
        resp = await client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.4,
            max_completion_tokens=1024,
            response_format={"type": "json_object"},
        )
        if tracker:
            tracker.track(resp.usage)
        raw = resp.choices[0].message.content
        result = json.loads(raw)
    except Exception as e:
        print(f"[query_gen] {tid}: OpenAI call failed: {e}")
        return _fallback_queries(tid, label, target_type, brief, video_context)

    # Parse and validate
    queries = result.get("queries", [])
    if not isinstance(queries, list):
        print(f"[query_gen] {tid}: unexpected response format, using fallback")
        return _fallback_queries(tid, label, target_type, brief, video_context)

    # Filter: each query must be a string with 4+ words
    valid = []
    seen = set()
    for q in queries:
        if not isinstance(q, str):
            continue
        q = q.strip()
        if q.lower() in seen:
            continue
        if len(q.split()) < 4:
            continue
        seen.add(q.lower())
        valid.append(q)

    valid = valid[:2]

    if len(valid) < 2:
        print(f"[query_gen] {tid}: only {len(valid)} valid queries, supplementing with fallback")
        fallback = _fallback_queries(tid, label, target_type, brief, video_context)
        for fq in fallback["queries"]:
            if fq.lower() not in seen and len(valid) < 2:
                valid.append(fq)
                seen.add(fq.lower())

    output = {
        "target_id": tid,
        "canonical_label": label,
        "queries": valid,
        "generated_at": utc_now(),
    }

    print(f"[query_gen] {tid} ({label}): {len(valid)} queries generated")
    return output


def _fallback_queries(tid: str, label: str, target_type: str, brief: dict, video_context: dict) -> dict:
    """Generate basic fallback queries when LLM fails."""
    queries = []
    subject = video_context.get("subject", "") if video_context else ""

    goals = brief.get("search_goals", [])
    for g in goals[:2]:
        if isinstance(g, str) and len(g.split()) >= 4:
            queries.append(g)

    # Anchor fallback queries to video subject
    anchor = f" {subject}" if subject else ""
    queries.append(f"{label}{anchor} photograph high quality")
    queries.append(f"{label}{anchor} historical reference photograph")

    return {
        "target_id": tid,
        "canonical_label": label,
        "queries": queries[:2],
        "generated_at": utc_now(),
    }


async def generate_all_queries(
    intake_path: Path,
    sector_root: Path,
    client: AsyncOpenAI,
    video_context: dict = None,
    tracker=None,
) -> list[dict]:
    """Generate queries for all targets in parallel with Semaphore(10)."""
    sr = sector_root.resolve()
    intake = read_json(intake_path)
    all_targets = intake["research_targets"]
    targets = [t for t in all_targets if t.get("handling_mode") != "skip_visual_retrieval"]
    skipped = len(all_targets) - len(targets)
    if skipped:
        print(f"[query_gen] skipping {skipped} non-retrievable targets")

    prompt_path = PROMPTS_DIR / "s4_query_generator_system.txt"
    system_prompt = prompt_path.read_text(encoding="utf-8")

    if video_context is None:
        video_context = {}

    semaphore = asyncio.Semaphore(QUERY_SEMAPHORE_LIMIT)

    async def _gen_with_semaphore(target):
        async with semaphore:
            tid = target["target_id"]
            stid = sanitize_target_id(tid)
            brief_path = sr / "targets" / stid / f"{stid}_brief.json"
            if brief_path.exists():
                brief = read_json(brief_path)
            else:
                brief = {"search_goals": [f"{target['canonical_label']} photograph"]}

            result = await generate_queries_for_target(
                target, brief, client, system_prompt, video_context, tracker
            )

            out_path = search_queries_path(sr, tid)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            write_json(out_path, result)

            return result

    tasks = [_gen_with_semaphore(t) for t in targets]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    valid_results = []
    for target, result in zip(targets, results):
        if isinstance(result, Exception):
            print(f"[query_gen] {target['target_id']}: FAILED: {result}")
            continue
        valid_results.append(result)

    total_queries = sum(len(r["queries"]) for r in valid_results)
    print(f"[query_gen] DONE: {len(valid_results)}/{len(targets)} targets, {total_queries} total queries")
    return valid_results


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: s4_query_generator.py <intake_path> <sector_root>")
    client = AsyncOpenAI()
    asyncio.run(generate_all_queries(Path(sys.argv[1]), Path(sys.argv[2]), client))
