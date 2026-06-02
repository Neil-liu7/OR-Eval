"""OR-Eval inference layer — multi-provider model API clients.

Public API:
- create_client(model, provider, ...) -> BaseProvider  (recommended)
- GeminiStyleClient(model, ...)  (legacy compat, delegates to EBillProvider)
- ModelResponse  (returned by all providers)
- ProviderConfig  (typed config for provider construction)
"""
from __future__ import annotations

from or_eval.inference.providers import (
    AnthropicProvider,
    BaseProvider,
    EBillProvider,
    ModelResponse,
    OpenAIProvider,
    ProviderConfig,
    VLLMProvider,
    create_client,
    create_provider,
)


DEFAULT_API_URL = "http://ebill.baidu-int.com/v1/models/{model}"


class GeminiStyleClient:
    """Legacy-compatible client that delegates to the provider system.

    Existing code that uses GeminiStyleClient will continue to work unchanged.
    New code should use create_client() instead.
    """

    def __init__(
        self,
        model: str,
        api_url: str = DEFAULT_API_URL,
        api_key: str | None = None,
        api_key_env: str = "OR_EVAL_API_KEY",
        timeout: int = 120,
        max_retries: int = 3,
        temperature: float = 0,
        max_tokens: int = 4096,
        provider: str = "auto",
    ) -> None:
        self.model = model
        self._provider = create_client(
            model=model,
            provider=provider,
            api_url=api_url,
            api_key=api_key,
            api_key_env=api_key_env,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
            max_retries=max_retries,
        )

    def generate(self, prompt: str, system_prompt: str | None = None) -> ModelResponse:
        return self._provider.generate(prompt, system_prompt)
