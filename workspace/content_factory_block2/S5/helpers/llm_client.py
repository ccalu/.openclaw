"""MiniMax M2.7-highspeed async LLM client with semaphore + retry/backoff."""
import asyncio
import json
import re
import threading
import time
from pathlib import Path

from openai import AsyncOpenAI

# ---------------------------------------------------------------------------
# MiniMax Token Plan Plus-HS config
# ---------------------------------------------------------------------------

MINIMAX_API_KEY = "sk-cp-sKXXZgxHY1zx0DVX-zO5ecxlwcdxd_msvxIM_aFr1hXFVjy6JrbtqXiz512Yacv4I96OvzCSyFMJ3Id09-Xr5WwOlqvfTNvhhKlT0dfYjAWrjuQ2fUPdSig"
MINIMAX_BASE_URL = "https://api.minimax.io/v1"
MODEL = "MiniMax-M2.7-highspeed"
MAX_CONCURRENT = 10
MAX_RETRIES = 3
BACKOFF_BASE = 2.0


# ---------------------------------------------------------------------------
# Usage tracker
# ---------------------------------------------------------------------------

class UsageTracker:
    def __init__(self):
        self._lock = threading.Lock()
        self.input_tokens = 0
        self.output_tokens = 0
        self.calls = 0

    def track(self, usage):
        with self._lock:
            self.input_tokens += getattr(usage, "prompt_tokens", 0) or 0
            self.output_tokens += getattr(usage, "completion_tokens", 0) or 0
            self.calls += 1

    def summary(self) -> dict:
        return {
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.input_tokens + self.output_tokens,
            "calls": self.calls,
            "model": MODEL,
        }


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------

def create_client() -> AsyncOpenAI:
    return AsyncOpenAI(api_key=MINIMAX_API_KEY, base_url=MINIMAX_BASE_URL)


def _extract_json(text: str) -> str:
    """Strip <think>...</think> reasoning tags and markdown fences, extract JSON.

    MiniMax M2.7 may wrap output in <think>...</think> blocks before the actual JSON,
    and sometimes wraps the JSON in ```json ... ``` markdown fences.
    """
    if not text:
        raise ValueError("Empty response from LLM")
    # Strip thinking tags
    cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
    if not cleaned:
        raise ValueError(f"No content after stripping think tags from: {text[:200]}")
    # Strip markdown code fences
    cleaned = re.sub(r"^```(?:json)?\s*\n?", "", cleaned).strip()
    cleaned = re.sub(r"\n?```\s*$", "", cleaned).strip()
    return cleaned


# ---------------------------------------------------------------------------
# Single LLM call with semaphore + retry
# ---------------------------------------------------------------------------

_semaphore = asyncio.Semaphore(MAX_CONCURRENT)


async def call_llm(
    client: AsyncOpenAI,
    system_prompt: str,
    user_content: str,
    tracker: UsageTracker | None = None,
    temperature: float = 0.3,
    max_tokens: int = 16384,
) -> dict:
    """Single LLM call with semaphore + retry/backoff. Returns parsed JSON."""
    async with _semaphore:
        last_err = None
        for attempt in range(MAX_RETRIES):
            try:
                resp = await client.chat.completions.create(
                    model=MODEL,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_content},
                    ],
                    temperature=temperature,
                    max_completion_tokens=max_tokens,
                    response_format={"type": "json_object"},
                )
                if tracker and resp.usage:
                    tracker.track(resp.usage)
                raw = resp.choices[0].message.content or ""
                finish = resp.choices[0].finish_reason
                if not raw:
                    raise ValueError(f"Empty response (finish_reason={finish}, usage={resp.usage})")
                cleaned = _extract_json(raw)
                if not cleaned:
                    raise ValueError(f"Empty after think-strip (raw_len={len(raw)}, finish={finish})")
                return json.loads(cleaned)
            except Exception as e:
                last_err = e
                if attempt < MAX_RETRIES - 1:
                    wait = BACKOFF_BASE ** (attempt + 1)
                    print(f"[llm_client] attempt {attempt + 1} failed: {e}, retrying in {wait}s...")
                    await asyncio.sleep(wait)
                else:
                    raise RuntimeError(f"LLM call failed after {MAX_RETRIES} attempts: {last_err}")


# ---------------------------------------------------------------------------
# Batch call helper
# ---------------------------------------------------------------------------

async def call_llm_batch(
    client: AsyncOpenAI,
    items: list,
    system_prompt: str,
    build_user_fn,
    tracker: UsageTracker | None = None,
    temperature: float = 0.3,
    max_tokens: int = 16384,
) -> list:
    """Process a list of items through LLM calls with concurrency control.

    Args:
        items: list of items to process
        system_prompt: system prompt for all calls
        build_user_fn: callable(item) -> str, builds user content for each item
        tracker: optional usage tracker

    Returns:
        list of (item, result_dict) tuples. On error, result_dict is {"error": str}.
    """
    async def _process(item):
        try:
            user_content = build_user_fn(item)
            result = await call_llm(client, system_prompt, user_content,
                                    tracker=tracker, temperature=temperature,
                                    max_tokens=max_tokens)
            return (item, result)
        except Exception as e:
            return (item, {"error": str(e)})

    tasks = [_process(item) for item in items]
    return await asyncio.gather(*tasks)
