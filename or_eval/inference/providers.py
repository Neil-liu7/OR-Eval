"""Multi-provider inference adapters for OR-Eval.

Supported providers:
- ebill: Baidu internal eBill proxy (Gemini-style + OpenAI fallback)
- openai: OpenAI API direct (GPT-4o, o3, etc.) or Azure OpenAI
- anthropic: Anthropic Messages API (Claude)
- vllm: Local vLLM / Ollama / any OpenAI-compatible endpoint
- auto: Route by model name heuristic
"""
from __future__ import annotations

import json
import os
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

import requests


@dataclass
class ModelResponse:
    text: str
    model: str
    latency: float
    tokens_prompt: int | None = None
    tokens_completion: int | None = None
    tokens_total: int | None = None
    raw_usage: dict[str, Any] | None = None
    raw_response: dict[str, Any] | None = None
    error: str | None = None


@dataclass
class ProviderConfig:
    """Configuration for a single provider instance."""
    provider: str = "auto"
    model: str = ""
    api_url: str | None = None
    api_key: str | None = None
    api_key_env: str = "OR_EVAL_API_KEY"
    timeout: int = 120
    max_retries: int = 3
    temperature: float = 0
    max_tokens: int = 4096
    extra: dict[str, Any] = field(default_factory=dict)


class BaseProvider(ABC):
    """Base class for all inference providers."""

    def __init__(self, config: ProviderConfig) -> None:
        self.config = config
        self.model = config.model
        self.api_key = config.api_key or os.getenv(config.api_key_env, "")
        self.timeout = config.timeout
        self.max_retries = config.max_retries
        self.temperature = config.temperature
        self.max_tokens = config.max_tokens

    @abstractmethod
    def generate(self, prompt: str, system_prompt: str | None = None) -> ModelResponse:
        ...

    def _retry_request(self, request_fn) -> tuple[dict | None, str | None, float]:
        last_error = None
        start = time.time()
        for attempt in range(self.max_retries):
            try:
                data = request_fn()
                return data, None, time.time() - start
            except Exception as exc:
                last_error = f"{type(exc).__name__}: {exc}"
                if attempt < self.max_retries - 1:
                    time.sleep(2 * (attempt + 1))
        return None, last_error, time.time() - start


class OpenAIProvider(BaseProvider):
    """OpenAI Chat Completions API (works with OpenAI, Azure, vLLM, Ollama)."""

    DEFAULT_URL = "https://api.openai.com/v1/chat/completions"

    def __init__(self, config: ProviderConfig) -> None:
        super().__init__(config)
        self.api_url = config.api_url or self.DEFAULT_URL
        if not self.api_url.endswith("/chat/completions"):
            self.api_url = self.api_url.rstrip("/") + "/chat/completions"

    def generate(self, prompt: str, system_prompt: str | None = None) -> ModelResponse:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "stream": False,
        }

        def do_request():
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            resp = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=self.timeout,
            )
            resp.raise_for_status()
            return resp.json()

        data, error, latency = self._retry_request(do_request)
        if error or data is None:
            return ModelResponse(text="", model=self.model, latency=latency, error=error)

        text = _extract_openai_text(data)
        usage = data.get("usage") or {}
        return ModelResponse(
            text=text,
            model=self.model,
            latency=latency,
            tokens_prompt=usage.get("prompt_tokens"),
            tokens_completion=usage.get("completion_tokens"),
            tokens_total=usage.get("total_tokens"),
            raw_usage=usage,
            raw_response=data,
        )


class AnthropicProvider(BaseProvider):
    """Anthropic Messages API for Claude models."""

    DEFAULT_URL = "https://api.anthropic.com/v1/messages"

    def __init__(self, config: ProviderConfig) -> None:
        super().__init__(config)
        self.api_url = config.api_url or self.DEFAULT_URL
        if not self.api_key:
            self.api_key = os.getenv("ANTHROPIC_API_KEY", "")

    def generate(self, prompt: str, system_prompt: str | None = None) -> ModelResponse:
        payload: dict[str, Any] = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system_prompt:
            payload["system"] = system_prompt

        def do_request():
            headers = {
                "Content-Type": "application/json",
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
            }
            resp = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=self.timeout,
            )
            resp.raise_for_status()
            return resp.json()

        data, error, latency = self._retry_request(do_request)
        if error or data is None:
            return ModelResponse(text="", model=self.model, latency=latency, error=error)

        text = _extract_anthropic_text(data)
        usage = data.get("usage") or {}
        return ModelResponse(
            text=text,
            model=self.model,
            latency=latency,
            tokens_prompt=usage.get("input_tokens"),
            tokens_completion=usage.get("output_tokens"),
            tokens_total=(usage.get("input_tokens") or 0) + (usage.get("output_tokens") or 0) or None,
            raw_usage=usage,
            raw_response=data,
        )


class EBillProvider(BaseProvider):
    """Baidu eBill proxy with Gemini-style + OpenAI fallback."""

    DEFAULT_URL = "http://ebill.baidu-int.com/v1/models/{model}"

    def __init__(self, config: ProviderConfig) -> None:
        super().__init__(config)
        self.api_url = config.api_url or self.DEFAULT_URL

    def generate(self, prompt: str, system_prompt: str | None = None) -> ModelResponse:
        errors = []
        if _prefer_openai_first(self.model):
            result = self._try_openai(prompt, system_prompt)
            if result.error is None:
                return result
            errors.append(f"openai={result.error}")
            result = self._try_gemini(prompt, system_prompt)
            if result.error is None:
                return result
            errors.append(f"gemini={result.error}")
            result.error = "; ".join(errors)
            return result

        result = self._try_gemini(prompt, system_prompt)
        if result.error is None:
            return result
        errors.append(f"gemini={result.error}")
        result = self._try_openai(prompt, system_prompt)
        if result.error is None:
            return result
        errors.append(f"openai={result.error}")
        result.error = "; ".join(errors)
        return result

    def _try_gemini(self, prompt: str, system_prompt: str | None) -> ModelResponse:
        contents = []
        if system_prompt:
            contents.append({"role": "user", "parts": [{"text": system_prompt}]})
        contents.append({"role": "user", "parts": [{"text": prompt}]})
        payload = {
            "contents": contents,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "stream": False,
        }

        def do_request():
            resp = requests.post(
                self.api_url.format(model=self.model),
                headers={"x-api-key": self.api_key, "Content-Type": "application/json"},
                json=payload,
                timeout=self.timeout,
            )
            resp.raise_for_status()
            return resp.json()

        data, error, latency = self._retry_request(do_request)
        if error or data is None:
            return ModelResponse(text="", model=self.model, latency=latency, error=error)

        text = _extract_gemini_text(data)
        usage = data.get("usageMetadata") or data.get("usage") or {}
        return ModelResponse(
            text=text,
            model=self.model,
            latency=latency,
            tokens_prompt=usage.get("promptTokenCount") or usage.get("prompt_tokens"),
            tokens_completion=usage.get("candidatesTokenCount") or usage.get("completion_tokens"),
            tokens_total=usage.get("totalTokenCount") or usage.get("total_tokens"),
            raw_usage=usage,
            raw_response=data,
        )

    def _try_openai(self, prompt: str, system_prompt: str | None) -> ModelResponse:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "stream": False,
        }
        url = _openai_chat_url(self.api_url)

        def do_request():
            resp = requests.post(
                url,
                headers={"x-api-key": self.api_key, "Content-Type": "application/json"},
                json=payload,
                timeout=self.timeout,
            )
            resp.raise_for_status()
            return resp.json()

        data, error, latency = self._retry_request(do_request)
        if error or data is None:
            return ModelResponse(text="", model=self.model, latency=latency, error=error)

        text = _extract_openai_text(data)
        usage = data.get("usage") or {}
        return ModelResponse(
            text=text,
            model=self.model,
            latency=latency,
            tokens_prompt=usage.get("prompt_tokens"),
            tokens_completion=usage.get("completion_tokens"),
            tokens_total=usage.get("total_tokens"),
            raw_usage=usage,
            raw_response=data,
        )


class VLLMProvider(OpenAIProvider):
    """Local vLLM / Ollama / LMStudio (OpenAI-compatible endpoint)."""

    DEFAULT_URL = "http://localhost:8000/v1/chat/completions"

    def __init__(self, config: ProviderConfig) -> None:
        if config.api_url is None:
            config.api_url = self.DEFAULT_URL
        super().__init__(config)


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

PROVIDER_REGISTRY: dict[str, type[BaseProvider]] = {
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
    "ebill": EBillProvider,
    "vllm": VLLMProvider,
    "ollama": VLLMProvider,
    "local": VLLMProvider,
}


def create_provider(config: ProviderConfig) -> BaseProvider:
    """Create a provider instance from config, with auto-detection."""
    provider_name = config.provider.lower()
    if provider_name == "auto":
        provider_name = _detect_provider(config.model, config.api_url)
    cls = PROVIDER_REGISTRY.get(provider_name)
    if cls is None:
        raise ValueError(f"Unknown provider: {provider_name!r}. Choose from: {', '.join(PROVIDER_REGISTRY)}")
    return cls(config)


def create_client(
    model: str,
    provider: str = "auto",
    api_url: str | None = None,
    api_key: str | None = None,
    api_key_env: str = "OR_EVAL_API_KEY",
    temperature: float = 0,
    max_tokens: int = 4096,
    timeout: int = 120,
    max_retries: int = 3,
    **extra,
) -> BaseProvider:
    """Convenience function matching the old GeminiStyleClient interface."""
    config = ProviderConfig(
        provider=provider,
        model=model,
        api_url=api_url,
        api_key=api_key,
        api_key_env=api_key_env,
        temperature=temperature,
        max_tokens=max_tokens,
        timeout=timeout,
        max_retries=max_retries,
        extra=extra,
    )
    return create_provider(config)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _detect_provider(model: str, api_url: str | None) -> str:
    if api_url:
        lowered_url = api_url.lower()
        if "ebill" in lowered_url or "baidu-int" in lowered_url:
            return "ebill"
        if "localhost" in lowered_url or "127.0.0.1" in lowered_url:
            return "vllm"
        if "api.anthropic.com" in lowered_url:
            return "anthropic"
        if "api.openai.com" in lowered_url or "azure" in lowered_url:
            return "openai"
    lowered = model.lower()
    if lowered.startswith(("claude",)):
        return "anthropic"
    if lowered.startswith(("gpt", "o3", "o4")):
        return "openai"
    return "ebill"


def _prefer_openai_first(model: str) -> bool:
    lowered = model.lower()
    return lowered.startswith((
        "gpt", "o3", "o4", "qwen", "qwq", "qvq", "claude",
        "gemini", "glm", "kimi", "doubao", "hunyuan", "minimax", "mimo",
    ))


def _extract_openai_text(data: dict[str, Any]) -> str:
    choices = data.get("choices") or []
    if not choices:
        return ""
    message = choices[0].get("message") or {}
    content = message.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for part in content:
            if isinstance(part, dict):
                parts.append(str(part.get("text") or part.get("content") or ""))
        return "\n".join(part for part in parts if part)
    return json.dumps(choices[0], ensure_ascii=False)


def _extract_gemini_text(data: dict[str, Any]) -> str:
    candidates = data.get("candidates") or []
    if not candidates:
        return ""
    content = candidates[0].get("content") or {}
    parts = content.get("parts") or []
    texts = [str(part.get("text", "")) for part in parts if isinstance(part, dict)]
    if texts:
        return "\n".join(texts)
    return json.dumps(candidates[0], ensure_ascii=False)


def _extract_anthropic_text(data: dict[str, Any]) -> str:
    content = data.get("content") or []
    texts = []
    for block in content:
        if isinstance(block, dict) and block.get("type") == "text":
            texts.append(block.get("text", ""))
    return "\n".join(texts) if texts else ""


def _openai_chat_url(api_url: str) -> str:
    marker = "/v1/models/"
    if marker in api_url:
        return api_url.split(marker, 1)[0].rstrip("/") + "/v1/chat/completions"
    if api_url.rstrip("/").endswith("/v1/models/{model}"):
        return api_url.rsplit("/models/{model}", 1)[0].rstrip("/") + "/chat/completions"
    return api_url
