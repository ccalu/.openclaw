"""GeminiClient: reusable wrapper for Gemini API with KMS support.

Handles API calls, JSON mode, image input, retry logic, usage tracking,
multi-model cascade via KMS, OpenRouter fallback, and tier escalation.

Usage with KMS (recommended):
    from shared.kms_client_sync import KmsSyncClient
    kms = KmsSyncClient(base_url="https://...", machine_id="M1")
    gemini = GeminiClient(kms_client=kms, model_group="dataset_collect")

Usage with local key rotation (legacy):
    from shared.services.key_manager import KeyManager
    km = KeyManager()
    gemini = GeminiClient(key_manager=km)

Usage without rotation (backward compatible):
    gemini = GeminiClient()  # single key from .env
"""

import asyncio
import base64
import json
import logging
import os
import time
from pathlib import Path

import httpx
from dotenv import load_dotenv
from tenacity import (
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

try:
    from google import genai
    from google.genai import types
except ImportError:
    raise RuntimeError("google-genai not installed -- run: pip install google-genai")

logger = logging.getLogger(__name__)

# Timeout-based retry constants (CF V3 pattern)
_TEXT_TIMEOUT = 120          # 2 min for text generation
_VISION_TIMEOUT = 120        # 2 min for single-image vision
_BATCH_VISION_TIMEOUT = 120  # 2 min for multi-image vision
_BACKOFF_RATE_LIMIT = 5      # seconds after rate limit
_BACKOFF_OTHER = 2           # seconds after transient error
_FREE_429_THRESHOLD = 2      # free 429s (cumulative, not reset on success) before adding tier1
_TIER1_429_THRESHOLD = 2     # tier1 429s before adding paid/OpenRouter


def _compute_exclude_tiers(free_429s: int, tier1_429s: int) -> list[str]:
    """Tier escalation: same logic as CF V3 step_00a."""
    if tier1_429s >= _TIER1_429_THRESHOLD:
        return ["free", "tier1"]  # Force OpenRouter / paid
    if free_429s >= _FREE_429_THRESHOLD:
        return ["free"]  # Force tier1
    return []

# Vertex AI Service Account support
_SA_DIR = Path(__file__).resolve().parent.parent / "service_accounts"  # Not used in S4 (API keys only)

# Model -> Vertex AI location mapping
_VERTEX_LOCATIONS = {
    "gemini-2.5-flash": "us-central1",
    "gemini-2.5-flash-preview-tts": "us-central1",
    "gemini-2.5-flash-image": "us-central1",
    "gemini-3-flash-preview": "global",
    "gemini-3.1-flash-lite-preview": "global",
    "gemini-3.1-flash-image-preview": "global",
}


def _create_genai_client(
    api_key: str | None = None,
    service_account_file: str | None = None,
    vertex_project_id: str | None = None,
    vertex_location: str | None = None,
    model_name: str | None = None,
) -> genai.Client:
    """Create genai.Client — AI Studio (api_key) or Vertex AI (service account).

    If service_account_file is provided, uses Vertex AI with OAuth2 credentials.
    Otherwise uses AI Studio with plain API key.
    """
    if service_account_file:
        from google.oauth2.service_account import Credentials

        sa_path = _SA_DIR / service_account_file
        if not sa_path.exists():
            logger.warning("SA file not found: %s, falling back to api_key", sa_path)
            if api_key:
                return genai.Client(api_key=api_key)
            raise FileNotFoundError(f"Service account file not found: {sa_path}")

        creds = Credentials.from_service_account_file(
            str(sa_path),
            scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )
        location = vertex_location or _VERTEX_LOCATIONS.get(model_name or "", "us-central1")
        return genai.Client(
            vertexai=True,
            project=vertex_project_id,
            location=location,
            credentials=creds,
        )

    if api_key:
        return genai.Client(api_key=api_key)

    raise ValueError("Either api_key or service_account_file must be provided")

# S4: no .env loading — config comes from KMS and caller context


def _is_retryable(exc: BaseException) -> bool:
    """Return True for transient Gemini errors (429, 500, 503)."""
    exc_str = str(exc).lower()
    if "429" in exc_str or "resource exhausted" in exc_str:
        return True
    if "500" in exc_str or "internal" in exc_str:
        return True
    if "503" in exc_str or "unavailable" in exc_str:
        return True
    return False


class GeminiClient:
    """Async-compatible Gemini client with KMS multi-model cascade.

    Supports three modes (in priority order):
    1. **KMS mode**: kms_client + model_group — full cascade with tier escalation
    2. **Key rotation**: KeyManager — local round-robin (legacy)
    3. **Single key**: api_key or GEMINI_API_KEY from .env
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "gemini-2.5-flash",
        key_manager=None,
        kms_client=None,
        model_group: str | None = None,
    ):
        self.model = model
        self.model_group = model_group
        self._key_manager = key_manager       # local fallback
        self._kms_client = kms_client         # KMS client (priority)

        # KMS context (set by orchestrator after video name resolved)
        self._kms_context: dict = {}

        if kms_client:
            # KMS mode — client created per call
            self._client = None
            self._clients: dict = {}
            logger.info(
                "GeminiClient: KMS mode enabled (model_group=%s)",
                model_group or "none",
            )
        elif key_manager and key_manager.get_pool_size() > 0:
            # Key rotation mode
            self._client = None
            self._clients: dict = {}
            self._last_key_id: str | None = None
            logger.info(
                "GeminiClient: key rotation enabled (%d keys)",
                key_manager.get_pool_size(),
            )
        else:
            # Single key mode
            key = api_key or os.getenv("GEMINI_API_KEY")
            if not key:
                raise ValueError(
                    "No Gemini API key. Set GEMINI_API_KEY in .env, "
                    "pass api_key=, or provide a KMS client or KeyManager."
                )
            self._client = genai.Client(api_key=key)
            self._clients = {}

        # Usage tracking (cumulative, for CostTracker compatibility)
        self.total_calls = 0
        self.total_input_tokens = 0
        self.total_output_tokens = 0

    # ------------------------------------------------------------------
    # KMS key acquisition
    # ------------------------------------------------------------------

    def _acquire_key(self, exclude_tiers=None):
        """Acquire API key via KMS. Returns (api_key, model_name, provider).

        KMS handles cooldowns and model cascade server-side.
        Client passes exclude_tiers for tier escalation after consecutive 429s.
        """
        kms = self._kms_client
        api_key = kms.get_next_key(
            model_group=self.model_group,
            exclude_tiers=exclude_tiers or None,
        )
        model_name, provider = kms.resolve_model_for_sdk()
        self._last_sa_file = getattr(kms, '_last_service_account_file', None)
        self._last_vertex_project = getattr(kms, '_last_vertex_project_id', None)
        self._last_vertex_location = getattr(kms, '_last_vertex_location', None)
        return api_key, model_name, provider

    def _create_client_for_call(self, api_key: str, model_name: str) -> genai.Client:
        """Create genai.Client using SA (Vertex AI) or api_key (AI Studio)."""
        return _create_genai_client(
            api_key=api_key,
            service_account_file=self._last_sa_file,
            vertex_project_id=self._last_vertex_project,
            vertex_location=self._last_vertex_location,
            model_name=model_name,
        )

    def _report_kms_success(self, model, in_tok, out_tok, step_name=""):
        """Report successful call to KMS (non-fatal)."""
        kms = self._kms_client
        if not kms or not kms.last_key_id:
            return
        try:
            ctx = self._kms_context
            kms.report_success(
                key_id=kms.last_key_id,
                model=model,
                input_tokens=in_tok,
                output_tokens=out_tok,
                agent_name="s4_asset_research",
                step_name=step_name,
                account_code=ctx.get("account_code"),
                language=ctx.get("language"),
                system_name=ctx.get("system_name", "dataset"),
                video_title=ctx.get("video_title"),
            )
        except Exception:
            pass

    def _report_kms_error(self, model, exc, step_name=""):
        """Report error to KMS (non-fatal)."""
        kms = self._kms_client
        if not kms or not kms.last_key_id:
            return
        try:
            ctx = self._kms_context
            kms.report_error(
                key_id=kms.last_key_id,
                model=model,
                error=exc,
                model_group=self.model_group,
                agent_name="s4_asset_research",
                step_name=step_name,
                account_code=ctx.get("account_code"),
                language=ctx.get("language"),
                system_name=ctx.get("system_name", "dataset"),
                video_title=ctx.get("video_title"),
            )
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Legacy key acquisition (local KeyManager)
    # ------------------------------------------------------------------

    def _get_client(self) -> genai.Client:
        """Get genai.Client for legacy mode (local KeyManager or single key)."""
        if self._key_manager:
            key = self._key_manager.get_next_key()
            if key:
                self._last_key_id = key.key_id
                if key.key_id not in self._clients:
                    self._clients[key.key_id] = genai.Client(api_key=key.api_key)
                return self._clients[key.key_id]

        if self._client is None:
            raise ValueError("No API keys available (registry empty, no .env key)")
        return self._client

    def _report_error_legacy(self, exc: Exception) -> None:
        """Report key-specific errors to local KeyManager if available."""
        if not self._key_manager or not getattr(self, "_last_key_id", None):
            return
        exc_str = str(exc).lower()
        if "429" in exc_str or "resource exhausted" in exc_str:
            self._key_manager.report_rate_limit(self._last_key_id)
        elif "api key" in exc_str and "invalid" in exc_str:
            self._key_manager.mark_invalid(self._last_key_id)
            self._clients.pop(self._last_key_id, None)

    # ------------------------------------------------------------------
    # Text generation
    # ------------------------------------------------------------------

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
        max_output_tokens: int = 8192,
    ) -> dict:
        """Call LLM with system + user prompt, return parsed JSON dict.

        KMS mode: full cascade with tier escalation + OpenRouter fallback.
        Legacy mode: tenacity retry with local KeyManager.
        """
        if self._kms_client:
            return await self._generate_kms(
                system_prompt, user_prompt, temperature, max_output_tokens,
            )
        return await self._generate_legacy(
            system_prompt, user_prompt, temperature, max_output_tokens,
        )

    async def _generate_kms(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        max_output_tokens: int,
    ) -> dict:
        """KMS path: timeout-based retry with tier escalation (CF V3 pattern).

        Timeout loop: acquire key → call → success or rotate.
        Tier escalation: after 5 free 429s → exclude free; after 2 tier1 429s → exclude both.
        """
        from shared.retry_helper import call_openrouter_json
        from shared.error_classifier import classify_error
        from shared.kms_client_sync import NoKeysAvailableError

        last_error = None
        start_time = time.time()
        free_429s = 0
        tier1_429s = 0
        exclude_tiers: list[str] = []

        while (time.time() - start_time) < _TEXT_TIMEOUT:
            remaining = _TEXT_TIMEOUT - (time.time() - start_time)
            if remaining <= 0:
                break

            # Acquire key (with tier escalation)
            try:
                api_key, model_name, provider = self._acquire_key(exclude_tiers)
            except NoKeysAvailableError as e:
                wait_s = min(e.retry_after_ms / 1000, remaining)
                logger.warning("[generate] no keys available, waiting %.0fs...", wait_s)
                await asyncio.sleep(wait_s)
                continue
            except RuntimeError:
                await asyncio.sleep(min(10, remaining))
                continue

            # Make API call
            try:
                if provider == "openrouter":
                    raw, in_tok, out_tok = await call_openrouter_json(
                        api_key, model_name, system_prompt, user_prompt,
                        temperature,
                    )
                else:
                    client = self._create_client_for_call(api_key, model_name)
                    response = await client.aio.models.generate_content(
                        model=model_name,
                        contents=user_prompt,
                        config=types.GenerateContentConfig(
                            system_instruction=system_prompt,
                            temperature=temperature,
                            max_output_tokens=max_output_tokens,
                            response_mime_type="application/json",
                        ),
                    )
                    raw = response.text
                    meta = getattr(response, "usage_metadata", None)
                    in_tok = getattr(meta, "prompt_token_count", 0) or 0
                    out_tok = getattr(meta, "candidates_token_count", 0) or 0

                # Success — don't reset 429 counters (accumulate across calls
                # so tier escalation happens even with intermittent successes)
                self._track_usage_manual(in_tok, out_tok)
                self._report_kms_success(model_name, in_tok, out_tok)
                return self._parse_json(raw)

            except Exception as e:
                last_error = e
                error_type = classify_error(e)
                self._report_kms_error(
                    self._kms_client.last_model_id or "unknown", e,
                )
                if error_type == "CONTENT_BLOCK":
                    raise

                # Tier escalation (same as CF V3 step_00a pattern)
                if error_type in ("RATE_LIMIT", "AUTH_ERROR"):
                    tier = self._kms_client.last_key_tier
                    if tier == "free":
                        free_429s += 1
                    elif tier == "tier1":
                        tier1_429s += 1
                    exclude_tiers = _compute_exclude_tiers(free_429s, tier1_429s)

                backoff = _BACKOFF_RATE_LIMIT if error_type == "RATE_LIMIT" else _BACKOFF_OTHER
                logger.warning("[generate] %s (tier=%s, free429=%d, t1_429=%d): %s, retrying in %ds",
                               error_type, self._kms_client.last_key_tier, free_429s, tier1_429s,
                               str(e)[:100], backoff)
                await asyncio.sleep(min(backoff, remaining))

        raise last_error or RuntimeError(f"generate() timed out after {_TEXT_TIMEOUT}s")

    @retry(
        retry=retry_if_exception(_is_retryable),
        wait=wait_exponential(min=5, max=90),
        stop=stop_after_attempt(5),
        reraise=True,
    )
    async def _generate_legacy(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        max_output_tokens: int,
    ) -> dict:
        """Legacy path: tenacity retry with local KeyManager."""
        client = self._get_client()
        try:
            response = await client.aio.models.generate_content(
                model=self.model,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=temperature,
                    max_output_tokens=max_output_tokens,
                    response_mime_type="application/json",
                ),
            )
        except Exception as exc:
            self._report_error_legacy(exc)
            raise

        self._track_usage(response)
        return self._parse_json(response.text)

    # ------------------------------------------------------------------
    # Single image generation
    # ------------------------------------------------------------------

    async def generate_with_image(
        self,
        system_prompt: str,
        user_prompt: str,
        image_url: str,
        temperature: float = 0.2,
        max_output_tokens: int = 8192,
    ) -> dict:
        """Call LLM with system + user prompt + image, return parsed JSON."""
        image_bytes, mime_type = await self._download_image(image_url)

        if self._kms_client:
            return await self._generate_with_image_kms(
                system_prompt, user_prompt,
                image_bytes, mime_type,
                temperature, max_output_tokens,
            )
        return await self._generate_with_image_legacy(
            system_prompt, user_prompt,
            image_bytes, mime_type,
            temperature, max_output_tokens,
        )

    async def _generate_with_image_kms(
        self,
        system_prompt: str,
        user_prompt: str,
        image_bytes: bytes,
        mime_type: str,
        temperature: float,
        max_output_tokens: int,
    ) -> dict:
        """KMS path for single image vision calls (timeout-based)."""
        from shared.retry_helper import call_openrouter_multimodal
        from shared.error_classifier import classify_error
        from shared.kms_client_sync import NoKeysAvailableError

        b64_data = base64.b64encode(image_bytes).decode()
        gemini_parts = [
            {"text": system_prompt},
            {"inline_data": {"mime_type": mime_type, "data": b64_data}},
            {"text": user_prompt},
        ]

        last_error = None
        start_time = time.time()
        free_429s = 0
        tier1_429s = 0
        exclude_tiers: list[str] = []

        while (time.time() - start_time) < _VISION_TIMEOUT:
            remaining = _VISION_TIMEOUT - (time.time() - start_time)
            if remaining <= 0:
                break

            try:
                api_key, model_name, provider = self._acquire_key(exclude_tiers)
            except NoKeysAvailableError as e:
                await asyncio.sleep(min(e.retry_after_ms / 1000, remaining))
                continue
            except RuntimeError:
                await asyncio.sleep(min(10, remaining))
                continue

            try:
                if provider == "openrouter":
                    raw, in_tok, out_tok = await call_openrouter_multimodal(
                        api_key, model_name, gemini_parts, temperature,
                    )
                else:
                    client = self._create_client_for_call(api_key, model_name)
                    contents = [
                        types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                        user_prompt,
                    ]
                    response = await client.aio.models.generate_content(
                        model=model_name,
                        contents=contents,
                        config=types.GenerateContentConfig(
                            system_instruction=system_prompt,
                            temperature=temperature,
                            max_output_tokens=max_output_tokens,
                            response_mime_type="application/json",
                        ),
                    )
                    raw = response.text
                    meta = getattr(response, "usage_metadata", None)
                    in_tok = getattr(meta, "prompt_token_count", 0) or 0
                    out_tok = getattr(meta, "candidates_token_count", 0) or 0

                free_429s = 0
                tier1_429s = 0
                exclude_tiers = []
                self._track_usage_manual(in_tok, out_tok)
                self._report_kms_success(model_name, in_tok, out_tok)
                return self._parse_json(raw)

            except Exception as e:
                last_error = e
                error_type = classify_error(e)
                self._report_kms_error(self._kms_client.last_model_id or "unknown", e)
                if error_type == "CONTENT_BLOCK":
                    raise
                if error_type in ("RATE_LIMIT", "AUTH_ERROR"):
                    tier = self._kms_client.last_key_tier
                    if tier == "free":
                        free_429s += 1
                    elif tier == "tier1":
                        tier1_429s += 1
                    exclude_tiers = _compute_exclude_tiers(free_429s, tier1_429s)
                backoff = _BACKOFF_RATE_LIMIT if error_type == "RATE_LIMIT" else _BACKOFF_OTHER
                logger.warning("[vision] %s (free429=%d, t1_429=%d): %s, retrying in %ds",
                               error_type, free_429s, tier1_429s, str(e)[:100], backoff)
                await asyncio.sleep(min(backoff, remaining))

        raise last_error or RuntimeError(f"generate_with_image() timed out after {_VISION_TIMEOUT}s")

    @retry(
        retry=retry_if_exception(_is_retryable),
        wait=wait_exponential(min=5, max=90),
        stop=stop_after_attempt(5),
        reraise=True,
    )
    async def _generate_with_image_legacy(
        self,
        system_prompt: str,
        user_prompt: str,
        image_bytes: bytes,
        mime_type: str,
        temperature: float,
        max_output_tokens: int,
    ) -> dict:
        """Legacy path for single image vision calls."""
        contents = [
            types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
            user_prompt,
        ]
        client = self._get_client()
        try:
            response = await client.aio.models.generate_content(
                model=self.model,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=temperature,
                    max_output_tokens=max_output_tokens,
                    response_mime_type="application/json",
                ),
            )
        except Exception as exc:
            self._report_error_legacy(exc)
            raise

        self._track_usage(response)
        return self._parse_json(response.text)

    # ------------------------------------------------------------------
    # Multi-image generation (batch vision)
    # ------------------------------------------------------------------

    async def generate_with_images(
        self,
        system_prompt: str,
        user_prompt: str,
        images: list[tuple[bytes, str]],
        temperature: float = 0.2,
        max_output_tokens: int = 8192,
    ) -> dict | list:
        """Call LLM with system + user prompt + multiple images."""
        if self._kms_client:
            return await self._generate_with_images_kms(
                system_prompt, user_prompt, images,
                temperature, max_output_tokens,
            )
        return await self._generate_with_images_legacy(
            system_prompt, user_prompt, images,
            temperature, max_output_tokens,
        )

    async def _generate_with_images_kms(
        self,
        system_prompt: str,
        user_prompt: str,
        images: list[tuple[bytes, str]],
        temperature: float,
        max_output_tokens: int,
    ) -> dict | list:
        """KMS path for batch image vision calls (timeout-based)."""
        from shared.retry_helper import call_openrouter_multimodal
        from shared.error_classifier import classify_error
        from shared.kms_client_sync import NoKeysAvailableError

        gemini_parts = [{"text": system_prompt}]
        for img_bytes, mime_type in images:
            b64_data = base64.b64encode(img_bytes).decode()
            gemini_parts.append(
                {"inline_data": {"mime_type": mime_type, "data": b64_data}}
            )
        gemini_parts.append({"text": user_prompt})

        last_error = None
        start_time = time.time()
        free_429s = 0
        tier1_429s = 0
        exclude_tiers: list[str] = []

        while (time.time() - start_time) < _BATCH_VISION_TIMEOUT:
            remaining = _BATCH_VISION_TIMEOUT - (time.time() - start_time)
            if remaining <= 0:
                break

            try:
                api_key, model_name, provider = self._acquire_key(exclude_tiers)
            except NoKeysAvailableError as e:
                await asyncio.sleep(min(e.retry_after_ms / 1000, remaining))
                continue
            except RuntimeError:
                await asyncio.sleep(min(10, remaining))
                continue

            try:
                if provider == "openrouter":
                    raw, in_tok, out_tok = await call_openrouter_multimodal(
                        api_key, model_name, gemini_parts, temperature,
                    )
                else:
                    client = self._create_client_for_call(api_key, model_name)
                    contents = []
                    for img_bytes, mime_type in images:
                        contents.append(
                            types.Part.from_bytes(data=img_bytes, mime_type=mime_type)
                        )
                    contents.append(user_prompt)

                    response = await client.aio.models.generate_content(
                        model=model_name,
                        contents=contents,
                        config=types.GenerateContentConfig(
                            system_instruction=system_prompt,
                            temperature=temperature,
                            max_output_tokens=max_output_tokens,
                            response_mime_type="application/json",
                        ),
                    )
                    raw = response.text
                    meta = getattr(response, "usage_metadata", None)
                    in_tok = getattr(meta, "prompt_token_count", 0) or 0
                    out_tok = getattr(meta, "candidates_token_count", 0) or 0

                free_429s = 0
                tier1_429s = 0
                exclude_tiers = []
                self._track_usage_manual(in_tok, out_tok)
                self._report_kms_success(model_name, in_tok, out_tok)
                return self._parse_json(raw)

            except Exception as e:
                last_error = e
                error_type = classify_error(e)
                self._report_kms_error(self._kms_client.last_model_id or "unknown", e)
                if error_type == "CONTENT_BLOCK":
                    raise
                if error_type in ("RATE_LIMIT", "AUTH_ERROR"):
                    tier = self._kms_client.last_key_tier
                    if tier == "free":
                        free_429s += 1
                    elif tier == "tier1":
                        tier1_429s += 1
                    exclude_tiers = _compute_exclude_tiers(free_429s, tier1_429s)
                backoff = _BACKOFF_RATE_LIMIT if error_type == "RATE_LIMIT" else _BACKOFF_OTHER
                logger.warning("[batch_vision] %s (free429=%d, t1_429=%d): %s, retrying in %ds",
                               error_type, free_429s, tier1_429s, str(e)[:100], backoff)
                await asyncio.sleep(min(backoff, remaining))

        raise last_error or RuntimeError(f"generate_with_images() timed out after {_BATCH_VISION_TIMEOUT}s")

    @retry(
        retry=retry_if_exception(_is_retryable),
        wait=wait_exponential(min=5, max=90),
        stop=stop_after_attempt(5),
        reraise=True,
    )
    async def _generate_with_images_legacy(
        self,
        system_prompt: str,
        user_prompt: str,
        images: list[tuple[bytes, str]],
        temperature: float,
        max_output_tokens: int,
    ) -> dict | list:
        """Legacy path for batch image vision calls."""
        contents = []
        for img_bytes, mime_type in images:
            contents.append(
                types.Part.from_bytes(data=img_bytes, mime_type=mime_type)
            )
        contents.append(user_prompt)

        client = self._get_client()
        try:
            response = await client.aio.models.generate_content(
                model=self.model,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=temperature,
                    max_output_tokens=max_output_tokens,
                    response_mime_type="application/json",
                ),
            )
        except Exception as exc:
            self._report_error_legacy(exc)
            raise

        self._track_usage(response)
        return self._parse_json(response.text)

    # ------------------------------------------------------------------
    # Image download
    # ------------------------------------------------------------------

    async def _download_image(self, url: str) -> tuple[bytes, str]:
        """Download image bytes from URL."""
        async with httpx.AsyncClient(
            timeout=30,
            headers={
                "User-Agent": (
                    "DatasetSystem/1.0 "
                    "(https://example.org/dataset-system/; "
                    "dataset-system@example.org)"
                )
            },
        ) as client:
            resp = await client.get(url, follow_redirects=True)
            resp.raise_for_status()

        content_type = resp.headers.get("content-type", "image/jpeg")
        mime = content_type.split(";")[0].strip()
        if mime not in ("image/jpeg", "image/png", "image/gif", "image/webp"):
            mime = "image/jpeg"

        return resp.content, mime

    # ------------------------------------------------------------------
    # Usage tracking
    # ------------------------------------------------------------------

    def get_usage_stats(self) -> dict:
        """Return cumulative usage statistics."""
        return {
            "total_calls": self.total_calls,
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
        }

    def reset_usage(self) -> None:
        """Reset usage counters to zero."""
        self.total_calls = 0
        self.total_input_tokens = 0
        self.total_output_tokens = 0

    def _track_usage(self, response) -> None:
        """Update cumulative token counts from Gemini response metadata."""
        self.total_calls += 1
        meta = getattr(response, "usage_metadata", None)
        if meta:
            self.total_input_tokens += getattr(meta, "prompt_token_count", 0)
            self.total_output_tokens += getattr(
                meta, "candidates_token_count", 0
            )

    def _track_usage_manual(self, in_tok: int, out_tok: int) -> None:
        """Update cumulative token counts from manual values (KMS/OpenRouter)."""
        self.total_calls += 1
        self.total_input_tokens += in_tok
        self.total_output_tokens += out_tok

    # ------------------------------------------------------------------
    # JSON parsing
    # ------------------------------------------------------------------

    def _parse_json(self, text: str) -> dict:
        """Parse JSON from LLM response text, with truncation repair."""
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            if "```json" in text:
                try:
                    start = text.index("```json") + 7
                    end = text.index("```", start)
                    return json.loads(text[start:end].strip())
                except (ValueError, json.JSONDecodeError):
                    pass

            # Attempt to repair truncated JSON (output token limit hit)
            repaired = self._repair_truncated_json(text)
            if repaired is not None:
                return repaired

            raise

    def _repair_truncated_json(self, text: str) -> dict | None:
        """Try to repair JSON truncated by output token limit.

        Strategy: find the last complete object in an array, close the
        array and outer object.
        """
        last_brace = text.rfind("}")
        if last_brace < 0:
            return None

        for i in range(last_brace, 0, -1):
            if text[i] == "}":
                candidate = text[: i + 1] + "]}"
                try:
                    result = json.loads(candidate)
                    logger.warning(
                        "Repaired truncated JSON (trimmed %d chars)",
                        len(text) - i - 1,
                    )
                    return result
                except json.JSONDecodeError:
                    continue
        return None
