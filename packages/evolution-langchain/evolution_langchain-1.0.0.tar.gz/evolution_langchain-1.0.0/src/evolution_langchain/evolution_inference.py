import json
import time
from typing import Any, Dict, List, Optional, cast
from threading import Lock
from typing_extensions import override

import requests
from pydantic import SecretStr, ConfigDict
from langchain_core.outputs import LLMResult, Generation
from langchain_core.callbacks import (
    CallbackManagerForLLMRun,
    AsyncCallbackManagerForLLMRun,
)
from langchain_core.language_models.llms import BaseLLM


class TokenManager:
    """Manages access token lifecycle for Evolution Inference API"""

    def __init__(
        self,
        key_id: str,
        secret: str,
        auth_url: str = "https://iam.api.cloud.ru/api/v1/auth/token",
    ):
        self.key_id = key_id
        self.secret = secret
        self.auth_url = auth_url
        self._token: Optional[str] = None
        self._token_expires_at = 0
        self._lock = Lock()

    def get_token(self) -> str:
        """Get valid access token, refreshing if necessary"""
        with self._lock:
            current_time = time.time()

            # Check if token is still valid (with 30 second buffer)
            if self._token and current_time < (self._token_expires_at - 30):
                return self._token

            # Refresh token
            token = self._refresh_token()
            assert token is not None  # Ensure token is not None
            return token

    def _refresh_token(self) -> str:
        """Refresh access token from authentication server"""
        payload = {"keyId": self.key_id, "secret": self.secret}

        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(
                self.auth_url,
                headers=headers,
                data=json.dumps(payload),
                timeout=30,
            )
            response.raise_for_status()

            token_data = response.json()
            token = token_data["access_token"]
            self._token = token

            # Set expiration time based on expires_in
            # (subtract 30 seconds for safety)
            expires_in = token_data.get("expires_in", 3600)
            self._token_expires_at = time.time() + expires_in

            return cast(str, token)

        except requests.RequestException as e:
            raise RuntimeError(f"Failed to obtain access token: {e}") from None
        except KeyError as e:
            raise RuntimeError(f"Invalid token response format: {e}") from None


class EvolutionInference(BaseLLM):
    """Evolution Inference language model with automatic token management.

    This class provides integration with Evolution Inference API, automatically
    handling access token lifecycle and providing OpenAI-compatible interface.
    """

    model: str = ""
    """The name of the model to use."""

    key_id: SecretStr = SecretStr("")
    """API Key ID for authentication."""

    secret: SecretStr = SecretStr("")
    """Secret for authentication."""

    base_url: str
    """Base URL for the Evolution Inference API (required)."""

    auth_url: Optional[str] = "https://iam.api.cloud.ru/api/v1/auth/token"
    """Authentication URL for obtaining access tokens."""

    max_tokens: int = 512
    """Maximum number of tokens to generate."""

    temperature: float = 1.0
    """Controls randomness in generation. Range: 0.0 to 2.0."""

    top_p: float = 1.0
    """Controls diversity via nucleus sampling. Range: 0.0 to 1.0."""

    frequency_penalty: float = 0.0
    """Penalizes repeated tokens based on frequency. Range: -2.0 to 2.0."""

    presence_penalty: float = 0.0
    """Penalizes repeated tokens based on presence. Range: -2.0 to 2.0."""

    stop: Optional[List[str]] = None
    """List of stop sequences to end generation."""

    streaming: bool = False
    """Whether to stream responses."""

    n: int = 1
    """Number of completions to generate."""

    request_timeout: int = 60
    """Request timeout in seconds."""

    # Pydantic v2 configuration
    model_config = ConfigDict(arbitrary_types_allowed=True)

    _token_manager: Optional[TokenManager] = None

    def __init__(self, **kwargs: Any) -> None:
        """Initialize EvolutionInference with token manager."""
        super().__init__(**kwargs)

        # Validate credentials
        key_id = self.key_id
        secret = self.secret
        base_url = self.base_url

        key_id_str = key_id.get_secret_value()
        secret_str = secret.get_secret_value()

        if not key_id_str or not secret_str:
            raise ValueError("key_id and secret must be provided") from None

        if not base_url or not base_url.strip():
            raise ValueError("base_url must be provided") from None

        # Initialize token manager using object.__setattr__ to bypass Pydantic
        default_auth_url = "https://iam.api.cloud.ru/api/v1/auth/token"
        auth_url = self.auth_url or default_auth_url
        self._token_manager = TokenManager(
            key_id=key_id_str, secret=secret_str, auth_url=auth_url
        )

    @property
    def _default_params(self) -> Dict[str, Any]:
        """Get default parameters for API calls."""
        return {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty,
            "stop": self.stop,
            "stream": self.streaming,
            "n": self.n,
        }

    def _get_headers(self) -> Dict[str, str]:
        """Get headers with current access token."""
        token_manager = cast(TokenManager, self._token_manager)
        token: str = token_manager.get_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    @override
    def _generate(
        self,
        prompts: List[str],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> LLMResult:
        """Generate completions for the given prompts."""
        generations: List[List[Generation]] = []

        for prompt in prompts:
            # Prepare request parameters
            params = {**self._default_params, **kwargs}
            if stop is not None:
                params["stop"] = stop

            # Create messages in OpenAI format
            messages = [{"role": "user", "content": prompt}]

            payload = {
                **params,
                "messages": messages,
            }

            # Remove None values
            payload = {k: v for k, v in payload.items() if v is not None}

            try:
                # Make API request
                response = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers=self._get_headers(),
                    json=payload,
                    timeout=self.request_timeout,
                )
                response.raise_for_status()

                result = response.json()

                # Extract text from OpenAI-compatible response
                if "choices" in result and len(result["choices"]) > 0:
                    content = result["choices"][0]["message"]["content"]
                    generations.append([Generation(text=content)])
                else:
                    raise ValueError(
                        "Invalid response format from API"
                    ) from None

            except requests.RequestException as e:
                raise RuntimeError(f"API request failed: {e}") from None
            except (KeyError, IndexError) as e:
                raise ValueError(f"Invalid API response format: {e}") from None

        return LLMResult(generations=generations)

    @override
    async def _agenerate(
        self,
        prompts: List[str],
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> LLMResult:
        """Async version of generate - for now, delegates to sync version."""
        # For full async support, would need to use aiohttp
        # Convert async callback manager to sync for compatibility
        sync_run_manager: Optional[CallbackManagerForLLMRun] = None
        if run_manager is not None:
            # This is a simplified conversion - in practice, you'd need proper async handling
            sync_run_manager = None
        return self._generate(prompts, stop, sync_run_manager, **kwargs)

    @property
    @override
    def _llm_type(self) -> str:
        """Return type of LLM."""
        return "cloud-ru-tech"

    @property
    @override
    def _identifying_params(self) -> Dict[str, Any]:
        """Get identifying parameters."""
        return {
            **self._default_params,
            "base_url": self.base_url,
        }
