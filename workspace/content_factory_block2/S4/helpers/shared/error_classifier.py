"""Unified error classifier for dataset system API calls.

Adapted from content_factory_v3/shared/processors/bloco2v2/error_classifier.py.
Returns one of: "CONTENT_BLOCK", "RATE_LIMIT", "AUTH_ERROR", "OTHER".
"""

import logging

logger = logging.getLogger(__name__)


def classify_error(error: Exception, *, api_response=None, model_type: str = "text") -> str:
    """Classify an API error into an actionable category.

    Args:
        error: The exception from the API call.
        api_response: The Gemini API response object (if available).
        model_type: One of "text", "image". Enables model-specific checks.

    Returns:
        "CONTENT_BLOCK" - prompt is the problem, no retry will help.
        "RATE_LIMIT"    - key is exhausted, try different key.
        "AUTH_ERROR"    - key is invalid/revoked, try different key.
        "OTHER"         - transient error, try different key.
    """

    # 1. Check response finish_reason (most reliable signal for Gemini)
    if api_response and hasattr(api_response, "candidates"):
        for c in api_response.candidates:
            fr = str(getattr(c, "finish_reason", "")).upper()
            if fr in ("PROHIBITED_CONTENT", "SAFETY", "OTHER"):
                return "CONTENT_BLOCK"

    # 2. Check ContentBlockedError (raised by wrappers)
    error_type_name = type(error).__name__
    if error_type_name == "ContentBlockedError":
        return "CONTENT_BLOCK"

    msg = str(error).lower()

    # 3. 429 that mentions safety = content block disguised as rate limit
    if "429" in msg and any(kw in msg for kw in ["safety", "blocked", "harm", "prohibited"]):
        return "CONTENT_BLOCK"

    # 4. Genuine rate limit / server overload
    if any(kw in msg for kw in ["429", "resource_exhausted", "quota", "rate_limit", "rate limit",
                                 "503", "unavailable", "500", "internal"]):
        return "RATE_LIMIT"

    # 5. Explicit content block
    if any(kw in msg for kw in ["safety", "blocked", "content_filter", "harm", "prohibited"]):
        return "CONTENT_BLOCK"

    # 6. Auth errors (key is bad, not content)
    if any(kw in msg for kw in ["401", "403", "unauthorized"]):
        return "AUTH_ERROR"
    if "invalid" in msg and "key" in msg:
        return "AUTH_ERROR"
    if "invalid_grant" in msg or "account not found" in msg:
        return "AUTH_ERROR"
    if "refresherror" in msg or "refresh" in error_type_name.lower():
        return "AUTH_ERROR"

    # 7. Everything else
    return "OTHER"
