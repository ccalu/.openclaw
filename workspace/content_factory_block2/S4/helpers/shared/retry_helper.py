"""Resilient retry constants and helpers for the dataset system.

Extracted from content_factory_v3/shared/processors/bloco2v2/retry_helper.py.
Self-contained: only needs asyncio, logging (loguru), and openai (for OpenRouter calls).

Usage:
    from shared.retry_helper import (
        is_rate_limit, is_safety_block, is_invalid_key,
        handle_rate_limit_delay, compute_exclude_tiers,
        get_pool_size, get_pool_size_group,
        call_openrouter_json, call_openrouter_multimodal,
        gemini_parts_to_openai,
        MAX_ROUNDS, COOLDOWN_BETWEEN_ROUNDS,
    )
"""

import asyncio

from loguru import logger

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MAX_ROUNDS = 3
COOLDOWN_BETWEEN_ROUNDS = 60   # seconds
DELAY_AFTER_RATE_LIMIT = 5     # seconds between key attempts after 429
CONSECUTIVE_429_THRESHOLD = 15  # per-batch: consecutive 429s before circuit breaker
CIRCUIT_BREAKER_PAUSE = 40     # seconds to pause when threshold hit

# Tier escalation thresholds
FREE_429_THRESHOLD = 5   # consecutive free-tier 429s before excluding free tier
TIER1_429_THRESHOLD = 2  # consecutive tier1 429s before excluding free + tier1


# ---------------------------------------------------------------------------
# Pool size helpers
# ---------------------------------------------------------------------------

def get_pool_size(key_manager, model: str) -> int:
    """Get available key count from KMS. Fallback to 50 if unavailable."""
    try:
        if hasattr(key_manager, "get_available_key_count"):
            count = key_manager.get_available_key_count(model)
            logger.info(f"Pool size for {model}: {count} keys")
            return max(count, 10)
        if hasattr(key_manager, "get_available_keys"):
            count = len(key_manager.get_available_keys())
            return max(count, 10)
    except Exception:
        pass
    return 50


def get_pool_size_group(key_manager) -> int:
    """Get available key count for model_group queries. Fallback to 50 if unavailable.

    Uses gemini-2.5-flash as a proxy estimate since model_group spans multiple models
    but all share the same key pool.
    """
    try:
        if hasattr(key_manager, "get_available_key_count"):
            count = key_manager.get_available_key_count("gemini-2.5-flash")
            logger.info(f"Pool size for model_group (via gemini-2.5-flash estimate): {count} keys")
            return max(count, 10)
        if hasattr(key_manager, "get_available_keys"):
            count = len(key_manager.get_available_keys())
            return max(count, 10)
    except Exception:
        pass
    return 50


# ---------------------------------------------------------------------------
# Error classification helpers
# ---------------------------------------------------------------------------

def is_rate_limit(error: Exception) -> bool:
    """Check if error is a 429 rate limit."""
    msg = str(error).lower()
    return any(kw in msg for kw in ("429", "resource_exhausted", "rate limit", "quota"))


def is_safety_block(error: Exception) -> bool:
    """Check if error is a safety/content policy block."""
    msg = str(error).lower()
    return any(kw in msg for kw in ("safety", "blocked", "content_filter", "harm"))


def is_invalid_key(error: Exception) -> bool:
    """Check if error is an invalid/revoked key."""
    msg = str(error).lower()
    return ("invalid" in msg and "key" in msg) or "401" in msg


# ---------------------------------------------------------------------------
# Tier escalation
# ---------------------------------------------------------------------------

def compute_exclude_tiers(free_429s: int, tier1_429s: int) -> list:
    """Compute tiers to exclude based on consecutive 429 counters.

    Returns:
        ["free", "tier1"] if tier1_429s >= TIER1_429_THRESHOLD
        ["free"]          if free_429s  >= FREE_429_THRESHOLD
        []                otherwise
    """
    if tier1_429s >= TIER1_429_THRESHOLD:
        return ["free", "tier1"]
    if free_429s >= FREE_429_THRESHOLD:
        return ["free"]
    return []


# ---------------------------------------------------------------------------
# Rate limit delay with circuit breaker
# ---------------------------------------------------------------------------

async def handle_rate_limit_delay(consecutive_429s: int, step_label: str = "") -> int:
    """Handle delay after 429. Returns updated consecutive counter.

    Normal: 5s delay between key attempts.
    Circuit breaker: if consecutive_429s >= threshold, pause 40s and reset counter.
    """
    consecutive_429s += 1
    if consecutive_429s >= CONSECUTIVE_429_THRESHOLD:
        logger.warning(
            f"[{step_label}] Circuit breaker: {consecutive_429s} consecutive 429s, "
            f"pausing {CIRCUIT_BREAKER_PAUSE}s"
        )
        await asyncio.sleep(CIRCUIT_BREAKER_PAUSE)
        return 0
    await asyncio.sleep(DELAY_AFTER_RATE_LIMIT)
    return consecutive_429s


# ---------------------------------------------------------------------------
# OpenRouter helpers (for KMS keys routed to OpenRouter)
# ---------------------------------------------------------------------------

def gemini_parts_to_openai(parts: list) -> list:
    """Convert Gemini multimodal parts to OpenAI content array.

    Gemini format:  [{"text": "..."}, {"inline_data": {"mime_type": "image/jpeg", "data": "base64..."}}]
    OpenAI format:  [{"type": "text", "text": "..."}, {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,..."}}]
    """
    content = []
    for part in parts:
        if "text" in part:
            content.append({"type": "text", "text": part["text"]})
        elif "inline_data" in part:
            mime = part["inline_data"]["mime_type"]
            data = part["inline_data"]["data"]
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:{mime};base64,{data}"},
            })
    return content


async def call_openrouter_json(
    api_key: str,
    model_name: str,
    system_prompt: str,
    user_content: str,
    temperature: float = 0.4,
) -> tuple:
    """Call OpenRouter using the OpenAI SDK. Returns (response_text, input_tokens, output_tokens).

    Used when KMS returns an OpenRouter key instead of a Google Gemini key.
    Requests JSON output via response_format.
    """
    from openai import AsyncOpenAI

    client = AsyncOpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")
    try:
        response = await client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            temperature=temperature,
            response_format={"type": "json_object"},
            timeout=120,
        )
        text = response.choices[0].message.content
        in_tok = response.usage.prompt_tokens if response.usage else 0
        out_tok = response.usage.completion_tokens if response.usage else 0
        return text, in_tok, out_tok
    finally:
        await client.close()


async def call_openrouter_multimodal(
    api_key: str,
    model_name: str,
    gemini_parts: list,
    temperature: float = 0.3,
) -> tuple:
    """Call OpenRouter with multimodal content (text + images).

    Converts Gemini-format parts to OpenAI vision format.
    The first part with text is used as system prompt,
    remaining parts go into the user message.

    Returns (response_text, input_tokens, output_tokens).
    """
    from openai import AsyncOpenAI

    # First text part = system prompt
    system_prompt = ""
    user_parts = gemini_parts
    if gemini_parts and "text" in gemini_parts[0]:
        system_prompt = gemini_parts[0]["text"]
        user_parts = gemini_parts[1:]

    user_content = gemini_parts_to_openai(user_parts)

    client = AsyncOpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")
    try:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_content})

        response = await client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=temperature,
            response_format={"type": "json_object"},
            timeout=180,
        )
        text = response.choices[0].message.content
        in_tok = response.usage.prompt_tokens if response.usage else 0
        out_tok = response.usage.completion_tokens if response.usage else 0
        return text, in_tok, out_tok
    finally:
        await client.close()
