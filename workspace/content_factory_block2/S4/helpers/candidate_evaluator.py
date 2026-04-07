# DEPRECATED — This file is no longer part of the active S4 pipeline.
# Replaced by the V3 asset_pipeline (s4_query_generator + s4_image_collector + s4_visual_evaluator).
# Retained temporarily for reference. See S4_ARCHITECTURE_V2.md for current architecture.
"""S4 Candidate Evaluator -- uses LLM to evaluate candidate relevance and classify."""
import json
import re
import sys
import time
from pathlib import Path

import httpx

from artifact_io import read_json, write_json, utc_now
from paths import evaluated_set_path
from schema_validator import validate_artifact_strict

KMS_URL = "https://web-production-0a8dd.up.railway.app"
KMS_MACHINE_ID = "M1"
KMS_MODEL_GROUP = "bloco2_text"
KMS_TIMEOUT = 30.0
KMS_MAX_RETRIES = 3
KMS_BACKOFF_BASE = 0.5

VALID_CLASSIFICATIONS = {"factual_evidence", "visual_reference", "stylistic_inspiration", "reject"}


def _kms_acquire_key(client: httpx.Client) -> dict:
    """Acquire a key from KMS. Returns full key_info dict."""
    payload = {
        "service": "llm",
        "machine_id": KMS_MACHINE_ID,
        "model_group": KMS_MODEL_GROUP,
    }
    for attempt in range(KMS_MAX_RETRIES + 1):
        try:
            resp = client.post("/api/v1/acquire", json=payload)
            resp.raise_for_status()
            data = resp.json()

            # Handle throttled
            if data.get("status") == "throttled":
                wait_ms = data.get("wait_ms", 1000)
                print(f"[candidate_evaluator] KMS throttled, waiting {wait_ms}ms")
                time.sleep(wait_ms / 1000.0)
                resp = client.post("/api/v1/acquire", json=payload)
                resp.raise_for_status()
                data = resp.json()

            keys = data.get("keys", [])
            if not keys:
                raise RuntimeError(f"KMS returned no keys: status={data.get('status')}")
            return keys[0]

        except (httpx.ConnectError, httpx.ConnectTimeout, httpx.ReadTimeout) as exc:
            if attempt < KMS_MAX_RETRIES:
                wait = KMS_BACKOFF_BASE * (2 ** attempt)
                print(f"[candidate_evaluator] KMS retry {attempt + 1}: {exc}")
                time.sleep(wait)
            else:
                raise


def _kms_report_success(client: httpx.Client, key_id: int, model: str,
                        input_tokens: int = 0, output_tokens: int = 0) -> None:
    """Report success to KMS."""
    payload = {
        "key_id": key_id,
        "machine_id": KMS_MACHINE_ID,
        "model": model,
        "agent_name": "s4_candidate_evaluator",
        "system_name": "content_factory_block2",
    }
    if input_tokens:
        payload["input_tokens"] = input_tokens
    if output_tokens:
        payload["output_tokens"] = output_tokens
    try:
        client.post("/api/v1/report", json=payload)
    except Exception as exc:
        print(f"[candidate_evaluator] KMS report warning: {exc}")


def _kms_report_error(client: httpx.Client, key_id: int, model: str, error: Exception) -> None:
    """Report error to KMS."""
    msg = str(error)[:500]
    http_status = 500
    match = re.search(r'\b(4\d{2}|5\d{2})\b', msg)
    if match:
        http_status = int(match.group(1))

    payload = {
        "key_id": key_id,
        "machine_id": KMS_MACHINE_ID,
        "model": model,
        "http_status": http_status,
        "error_code": type(error).__name__,
        "error_message": msg,
        "agent_name": "s4_candidate_evaluator",
        "system_name": "content_factory_block2",
    }
    try:
        client.post("/api/v1/report-error", json=payload)
    except Exception as exc:
        print(f"[candidate_evaluator] KMS error report warning: {exc}")


def _build_eval_prompt(target: dict, candidate: dict) -> str:
    """Build the LLM evaluation prompt for one candidate."""
    return f"""You are an asset research evaluator for a video production pipeline.

TARGET:
- canonical_label: {target['canonical_label']}
- target_type: {target['target_type']}
- research_needs: {json.dumps(target.get('research_needs', []))}

CANDIDATE:
- candidate_id: {candidate['candidate_id']}
- source_url: {candidate['source_url']}
- page_title: {candidate['page_title']}
- source_domain: {candidate['source_domain']}
- preliminary_classification: {candidate['preliminary_classification']}
- rationale: {candidate['rationale']}
- confidence: {candidate['confidence']}

Evaluate this candidate and return ONLY a JSON object with these fields:
- "final_classification": one of "factual_evidence", "visual_reference", "stylistic_inspiration", "reject"
- "target_fitness_note": 1-2 sentences on how well it fits the target research needs
- "downstream_usefulness_note": 1-2 sentences on how useful this would be for video production
- "asset_usability_note": 1-2 sentences on practical usability (licensing, quality, format)
- "is_best_candidate": true if this is among the best candidates for this target, false otherwise

Return ONLY the JSON object, no markdown fences, no extra text."""


def _call_gemini(client: httpx.Client, api_key: str, model: str, prompt: str) -> str:
    """Call Gemini API directly with the acquired key."""
    # Determine provider from model name
    if model and model.startswith("or-"):
        # OpenRouter model
        or_model = model.removeprefix("or-")
        resp = client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": f"google/{or_model}",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 1000,
            },
            timeout=60.0,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]
    else:
        # Google Gemini API
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        resp = client.post(
            url,
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"maxOutputTokens": 1000, "temperature": 0.2},
            },
            timeout=60.0,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]


def _parse_eval_response(text: str) -> dict:
    """Parse LLM evaluation response into a dict."""
    # Strip markdown fences if present
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        result = json.loads(cleaned)
    except json.JSONDecodeError:
        # Try to extract JSON from the text
        match = re.search(r'\{[^{}]*\}', cleaned, re.DOTALL)
        if match:
            result = json.loads(match.group())
        else:
            raise ValueError(f"Could not parse LLM response as JSON: {cleaned[:200]}")

    # Validate classification
    fc = result.get("final_classification", "reject")
    if fc not in VALID_CLASSIFICATIONS:
        result["final_classification"] = "reject"

    # Ensure all required fields
    result.setdefault("final_classification", "reject")
    result.setdefault("target_fitness_note", "")
    result.setdefault("downstream_usefulness_note", "")
    result.setdefault("asset_usability_note", "")
    result.setdefault("is_best_candidate", False)

    return result


def _fallback_evaluation(candidate: dict) -> dict:
    """Heuristic fallback when LLM is unavailable."""
    # Use the preliminary classification as final
    prelim = candidate.get("preliminary_classification", "reject")
    confidence = candidate.get("confidence", 0.5)
    return {
        "final_classification": prelim,
        "target_fitness_note": f"Heuristic fallback (confidence={confidence})",
        "downstream_usefulness_note": "Not LLM-evaluated; based on preliminary classification only",
        "asset_usability_note": f"Licensing: {candidate.get('licensing_note', 'unknown')}",
        "is_best_candidate": confidence >= 0.7 and prelim != "reject",
    }


def evaluate_candidates(
    candidate_set_path_arg: Path,
    brief_path: Path,
    sector_root: Path,
) -> Path:
    """Evaluate all candidates for a target using LLM via KMS.

    Returns:
        Path to the written evaluated_candidate_set.json.
    """
    candidate_set = read_json(candidate_set_path_arg)
    brief = read_json(brief_path)
    tid = candidate_set["target_id"]
    candidates = candidate_set["candidates"]

    print(f"[candidate_evaluator] evaluating {len(candidates)} candidates for target {tid}")

    evaluated = []
    evaluator_notes = []
    warnings = []
    best_ids = []
    llm_available = True
    kms_client = httpx.Client(base_url=KMS_URL, timeout=KMS_TIMEOUT)

    # Build target context from brief
    target_ctx = {
        "canonical_label": brief["canonical_label"],
        "target_type": brief["target_type"],
        "research_needs": brief.get("research_needs", []),
    }

    try:
        for candidate in candidates:
            cid = candidate["candidate_id"]

            if llm_available:
                try:
                    # Acquire key
                    key_info = _kms_acquire_key(kms_client)
                    api_key = key_info["api_key"]
                    key_id = key_info["key_id"]
                    model = key_info.get("model_id", "gemini-2.5-flash")
                    provider = key_info.get("provider", "gemini")

                    # Build prompt and call LLM
                    prompt = _build_eval_prompt(target_ctx, candidate)
                    response_text = _call_gemini(kms_client, api_key, model, prompt)

                    # Parse response
                    eval_result = _parse_eval_response(response_text)
                    evaluator_notes.append(f"{cid}: LLM evaluated via {model}")

                    # Report success
                    _kms_report_success(kms_client, key_id, model,
                                        input_tokens=len(prompt) // 4,
                                        output_tokens=len(response_text) // 4)

                except Exception as exc:
                    print(f"[candidate_evaluator] LLM failed for {cid}: {exc}")
                    warnings.append(f"LLM evaluation failed for {cid}: {str(exc)[:200]}")

                    # Report error if we have key_id
                    if 'key_id' in dir():
                        _kms_report_error(kms_client, key_id, model, exc)

                    # Fall back to heuristic
                    eval_result = _fallback_evaluation(candidate)
                    evaluator_notes.append(f"{cid}: heuristic fallback (LLM error)")

                    # If first candidate fails, disable LLM for rest
                    if len(evaluated) == 0:
                        llm_available = False
                        warnings.append("LLM unavailable; remaining candidates use heuristic fallback")
            else:
                eval_result = _fallback_evaluation(candidate)
                evaluator_notes.append(f"{cid}: heuristic fallback")

            eval_entry = {
                "candidate_id": cid,
                "final_classification": eval_result["final_classification"],
                "target_fitness_note": eval_result["target_fitness_note"],
                "downstream_usefulness_note": eval_result["downstream_usefulness_note"],
                "asset_usability_note": eval_result["asset_usability_note"],
                "is_best_candidate": eval_result["is_best_candidate"],
            }
            evaluated.append(eval_entry)

            if eval_result["is_best_candidate"]:
                best_ids.append(cid)

    finally:
        kms_client.close()

    if not best_ids and evaluated:
        # Pick highest-confidence non-reject as best
        for cand, ev in zip(candidates, evaluated):
            if ev["final_classification"] != "reject":
                best_ids.append(ev["candidate_id"])
                ev["is_best_candidate"] = True
                break

    evaluated_set = {
        "contract_version": "s4.evaluated_candidate_set.v1",
        "target_id": tid,
        "canonical_label": candidate_set["canonical_label"],
        "target_type": candidate_set["target_type"],
        "scene_ids": candidate_set["scene_ids"],
        "evaluated_candidates": evaluated,
        "best_candidate_ids": best_ids,
        "evaluator_notes": evaluator_notes,
        "warnings": warnings,
    }

    validate_artifact_strict(evaluated_set, "evaluated_candidate_set")

    out = evaluated_set_path(sector_root, tid)
    write_json(out, evaluated_set)
    print(f"[candidate_evaluator] wrote evaluated set: {out}")
    print(f"[candidate_evaluator] {len(best_ids)} best candidates out of {len(evaluated)}")
    return out


def main():
    if len(sys.argv) != 4:
        raise SystemExit(
            "usage: candidate_evaluator.py <candidate_set_path> <brief_path> <sector_root>"
        )
    evaluate_candidates(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]))


if __name__ == "__main__":
    main()
