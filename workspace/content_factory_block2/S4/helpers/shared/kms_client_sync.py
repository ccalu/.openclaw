"""Synchronous KMS client for the dataset system.

Copied from content_factory_v3/shared/clients/kms_client_sync.py and adapted
to be self-contained (no imports from content_factory_v3).
"""

import time

import httpx
from loguru import logger

# Connection-level errors that justify retrying against the KMS server itself
_RETRYABLE_ERRORS = (
    httpx.ConnectError,
    httpx.ConnectTimeout,
    httpx.ReadTimeout,
    httpx.WriteTimeout,
    httpx.PoolTimeout,
)

_MAX_KMS_RETRIES = 3
_BACKOFF_BASE = 0.5  # seconds; doubles each retry (0.5, 1.0, 2.0)


class NoKeysAvailableError(RuntimeError):
    """Raised when KMS has no keys to provide (all in cooldown or none exist)."""

    def __init__(self, message: str, *, status: str = "none", retry_after_ms: int = 10000):
        super().__init__(message)
        self.status = status
        self.retry_after_ms = retry_after_ms


class KmsSyncClient:
    """Synchronous version of CentralizedKeyClient.
    Uses httpx.Client instead of httpx.AsyncClient.

    All HTTP calls to the KMS server are wrapped with retry logic
    (3 retries, exponential backoff) for transient connection errors.
    """

    def __init__(self, base_url: str, machine_id: str, account_id: str = None):
        self.base_url = base_url.rstrip("/")
        self.machine_id = machine_id
        self.account_id = account_id
        self._client = httpx.Client(base_url=self.base_url, timeout=10.0)
        self._last_key_id: int | None = None
        self._last_key_tier: str | None = None
        self._last_model_id: str | None = None
        self._last_provider: str | None = None

    # ------------------------------------------------------------------
    # Internal: HTTP with retry
    # ------------------------------------------------------------------

    def _request_with_retry(self, method: str, url: str, **kwargs) -> httpx.Response:
        """Send HTTP request with retry logic for connection errors.

        Retries up to _MAX_KMS_RETRIES times with exponential backoff
        on transient connection/timeout errors.  Non-retryable HTTP errors
        (4xx, 5xx) are raised immediately.
        """
        last_error: Exception | None = None
        for attempt in range(_MAX_KMS_RETRIES + 1):
            try:
                resp = self._client.request(method, url, **kwargs)
                resp.raise_for_status()
                return resp
            except _RETRYABLE_ERRORS as exc:
                last_error = exc
                if attempt < _MAX_KMS_RETRIES:
                    wait = _BACKOFF_BASE * (2 ** attempt)
                    logger.warning(
                        f"KMS connection error (attempt {attempt + 1}/{_MAX_KMS_RETRIES + 1}): "
                        f"{type(exc).__name__}: {exc} -> retrying in {wait:.1f}s"
                    )
                    time.sleep(wait)
                else:
                    logger.error(
                        f"KMS connection failed after {_MAX_KMS_RETRIES + 1} attempts: "
                        f"{type(exc).__name__}: {exc}"
                    )
        raise last_error  # type: ignore[misc]

    # ------------------------------------------------------------------
    # Acquire
    # ------------------------------------------------------------------

    def get_next_key(self, model: str = None, service: str = None, *,
                     model_group: str = None,
                     exclude_tiers: list[str] = None) -> str:
        """Acquire a single API key from the KMS.
        Calls POST /api/v1/acquire on the central service.

        Args:
            model: Model name (e.g. 'gemini-2.5-flash', 'gpt-4.1-mini')
            service: Service type override ('llm', 'tts', 'image', 'search')
                     If not provided, inferred from model name.
            model_group: Model group name (e.g. 'dataset_text'). When set,
                        KMS picks the best model+key combo automatically.
            exclude_tiers: Tiers to exclude (e.g. ['free'] after many 429s).

        Returns:
            API key string ready to use.
        """
        if service is None:
            service = self._model_to_service(model) if model else "llm"

        payload = {
            "service": service,
            "machine_id": self.machine_id,
        }

        if model_group:
            payload["model_group"] = model_group
            logger.debug(f"KMS: acquiring key for model_group={model_group}")
        else:
            payload["model"] = model or "gemini-2.5-flash"
            logger.debug(f"KMS: acquiring key for service={service}, model={model}")

        if exclude_tiers:
            payload["exclude_tiers"] = exclude_tiers

        resp = self._request_with_retry("POST", "/api/v1/acquire", json=payload)
        data = resp.json()

        # Throttled: single retry then raise NoKeysAvailableError
        if data.get("status") == "throttled":
            wait_ms = data.get("wait_ms", 1000)
            logger.debug(f"KMS throttled: waiting {wait_ms}ms (model={model or model_group})")
            time.sleep(wait_ms / 1000.0)
            resp = self._request_with_retry("POST", "/api/v1/acquire", json=payload)
            data = resp.json()

        keys = data.get("keys", [])
        if not keys:
            status = data.get("status", "none")
            retry_after_ms = data.get("wait_ms") or 10000
            raise NoKeysAvailableError(
                f"No keys available (status={status}) "
                f"for service={service}, model={model}, group={model_group}",
                status=status,
                retry_after_ms=retry_after_ms,
            )

        key_info = keys[0]
        self._last_key_id = key_info["key_id"]
        self._last_key_tier = key_info["tier"]
        self._last_model_id = key_info.get("model_id")
        self._last_provider = key_info.get("provider")
        # Vertex AI Service Account fields
        self._last_auth_type = key_info.get("auth_type", "api_key")
        self._last_service_account_file = key_info.get("sa_filename")
        self._last_vertex_project_id = key_info.get("vertex_project_id")
        logger.debug(
            f"KMS: acquired key_id={self._last_key_id}, tier={self._last_key_tier}, "
            f"model={self._last_model_id}, provider={self._last_provider}, "
            f"auth={self._last_auth_type}"
        )
        return key_info["api_key"]

    @property
    def last_key_id(self) -> int | None:
        """ID of the last acquired key (for report_success/report_error)."""
        return self._last_key_id

    @property
    def last_key_tier(self) -> str | None:
        """Tier of the last acquired key."""
        return self._last_key_tier

    @property
    def last_model_id(self) -> str | None:
        """Actual model selected by KMS (multi-model mode)."""
        return self._last_model_id

    @property
    def last_provider(self) -> str | None:
        """Provider of the last acquired key ('gemini' or 'openrouter')."""
        return self._last_provider

    def resolve_model_for_sdk(self) -> tuple[str, str]:
        """Return (model_name_for_api, provider) based on last acquire.

        OpenRouter requires 'google/' prefix on model names.
        Google AI Studio uses model name as-is.

        Returns:
            Tuple of (model_name, provider).
        """
        model_id = self._last_model_id or "gemini-2.5-flash"
        provider = self._last_provider or "gemini"

        if provider == "openrouter":
            # Strip 'or-' prefix from KMS model ID to get OpenRouter model name
            or_model = model_id.removeprefix("or-")
            return f"google/{or_model}", provider
        return model_id, provider

    def get_available_key_count(self, model: str) -> int:
        """Get count of available keys for a model.

        Args:
            model: Model name (e.g. 'gemini-2.5-flash')

        Returns:
            Number of active keys available.
        """
        resp = self._request_with_retry("GET", "/api/v1/keys/available-count", params={"model": model})
        return resp.json()["count"]

    def report_success(self, key_id: int, model: str, *,
                       input_tokens: int = 0, output_tokens: int = 0,
                       cached_tokens: int = 0, thinking_tokens: int = 0,
                       character_cost: int = 0, query_count: int = 0,
                       modality_details: list[dict] | None = None,
                       response_id: str | None = None,
                       model_version: str | None = None,
                       response_headers: dict | None = None,
                       agent_name: str | None = None,
                       step_name: str | None = None,
                       account_code: str | None = None,
                       language: str | None = None,
                       system_name: str | None = None,
                       video_title: str | None = None) -> dict:
        """Report successful API call with usage data.

        Returns dict with cost_calculated, credit_remaining, daily_calls.
        """
        payload = {
            "key_id": key_id,
            "machine_id": self.machine_id,
            "model": model,
        }
        # Only include non-zero/non-None fields
        if input_tokens: payload["input_tokens"] = input_tokens
        if output_tokens: payload["output_tokens"] = output_tokens
        if cached_tokens: payload["cached_tokens"] = cached_tokens
        if thinking_tokens: payload["thinking_tokens"] = thinking_tokens
        if character_cost: payload["character_cost"] = character_cost
        if query_count: payload["query_count"] = query_count
        if modality_details: payload["modality_details"] = modality_details
        if response_id: payload["response_id"] = response_id
        if model_version: payload["model_version"] = model_version
        if response_headers: payload["response_headers"] = response_headers
        if agent_name: payload["agent_name"] = agent_name
        if step_name: payload["step_name"] = step_name
        if account_code: payload["account_code"] = account_code
        if language: payload["language"] = language
        if system_name: payload["system_name"] = system_name
        if video_title: payload["video_title"] = video_title

        logger.debug(f"KMS: reporting success for key_id={key_id}, model={model}")
        resp = self._request_with_retry("POST", "/api/v1/report", json=payload)
        data = resp.json()
        logger.debug(
            f"KMS: report accepted -- cost=${data.get('cost_calculated', 0):.6f}, "
            f"daily_calls={data.get('daily_calls', '?')}"
        )
        return data

    def report_error(self, key_id: int, model: str, error: Exception, *,
                     http_status: int | None = None,
                     error_code: str | None = None,
                     request_payload: dict | None = None,
                     input_token_estimate: int | None = None,
                     model_group: str | None = None,
                     agent_name: str | None = None,
                     step_name: str | None = None,
                     account_code: str | None = None,
                     language: str | None = None,
                     system_name: str | None = None,
                     video_title: str | None = None) -> dict | None:
        """Report error -- returns alternative key data if available.

        Returns dict with action, alternative key info, or None.
        """
        payload = {
            "key_id": key_id,
            "machine_id": self.machine_id,
            "model": model,
            "http_status": http_status or getattr(error, "status_code", getattr(error, "code", 500)),
            "error_code": error_code or type(error).__name__,
            "error_message": str(error)[:500],
        }
        if request_payload: payload["request_payload"] = request_payload
        if input_token_estimate: payload["input_token_estimate"] = input_token_estimate
        if model_group: payload["model_group"] = model_group
        if agent_name: payload["agent_name"] = agent_name
        if step_name: payload["step_name"] = step_name
        if account_code: payload["account_code"] = account_code
        if language: payload["language"] = language
        if system_name: payload["system_name"] = system_name
        if video_title: payload["video_title"] = video_title

        logger.debug(f"KMS: reporting error for key_id={key_id}, model={model}: {type(error).__name__}")
        resp = self._request_with_retry("POST", "/api/v1/report-error", json=payload)
        data = resp.json()

        action = data.get("action", "unknown")
        if data.get("alternative"):
            alt_id = data["alternative"].get("key_id")
            logger.info(f"KMS: error reported, action={action}, alternative key_id={alt_id}")
            return data["alternative"]

        logger.info(f"KMS: error reported, action={action}, no alternative available")
        return None

    def call_with_resilience(self, model: str, call_fn, *, max_retries: int = 2,
                             service: str = None,
                             agent_name: str | None = None,
                             step_name: str | None = None,
                             account_code: str | None = None,
                             language: str | None = None,
                             system_name: str | None = None,
                             video_title: str | None = None):
        """Helper: acquire key, call function, report result, retry on failure.

        Args:
            model: Model name
            call_fn: sync function(api_key: str) -> (result, usage_dict)
                     usage_dict should have keys like input_tokens, output_tokens, etc.
            max_retries: Max retry attempts on error
            service: Service type override
            agent_name: Agent context for reporting
            step_name: Step context for reporting
            account_code: Account context for reporting
            language: Language context for reporting

        Returns:
            Result from call_fn on success.

        Raises:
            Last exception if all retries exhausted.
        """
        ctx = {}
        if agent_name: ctx["agent_name"] = agent_name
        if step_name: ctx["step_name"] = step_name
        if account_code: ctx["account_code"] = account_code
        if language: ctx["language"] = language
        if system_name: ctx["system_name"] = system_name
        if video_title: ctx["video_title"] = video_title

        last_error = None

        for attempt in range(max_retries + 1):
            try:
                api_key = self.get_next_key(model=model, service=service)
                key_id = self._last_key_id

                result, usage = call_fn(api_key)

                self.report_success(key_id, model, **usage, **ctx)
                return result

            except Exception as e:
                last_error = e
                logger.warning(f"KMS: attempt {attempt+1}/{max_retries+1} failed for {model}: {e}")

                if self._last_key_id and attempt < max_retries:
                    alt = self.report_error(self._last_key_id, model, e, **ctx)
                    if alt:
                        logger.info(f"KMS: got alternative key {alt.get('key_id')}")
                elif self._last_key_id:
                    self.report_error(self._last_key_id, model, e, **ctx)

        raise last_error

    def _model_to_service(self, model: str | None) -> str:
        """Map model name to service type."""
        if not model:
            return "llm"
        mapping = {
            "gemini-2.5-flash": "llm",
            "gemini-3-flash": "llm",
            "gemini-3.1-flash-lite": "llm",
            "gemini-2.5-flash-preview-tts": "tts",
            "gemini-2.5-flash-image": "image",
            "gemini-3.1-flash-image-preview": "image",
            "gpt-4.1-mini": "llm",
            "gpt-4.1": "llm",
            "eleven_multilingual_v2": "tts",
        }
        # Check exact match first
        if model in mapping:
            return mapping[model]
        # Check prefix match
        if "tts" in model.lower():
            return "tts"
        if "image" in model.lower() or "imagen" in model.lower():
            return "image"
        return "llm"

    def close(self):
        """Close the HTTP client."""
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
