"""Tests for the multi-provider inference system."""
import os
import unittest

from or_eval.inference import GeminiStyleClient, ModelResponse, create_client
from or_eval.inference.providers import (
    AnthropicProvider,
    BaseProvider,
    EBillProvider,
    OpenAIProvider,
    ProviderConfig,
    VLLMProvider,
    _detect_provider,
    _extract_anthropic_text,
    _extract_gemini_text,
    _extract_openai_text,
    create_provider,
)


class ProviderDetectionTests(unittest.TestCase):
    def test_detect_by_model_name(self):
        self.assertEqual(_detect_provider("gpt-4o", None), "openai")
        self.assertEqual(_detect_provider("o3-mini", None), "openai")
        self.assertEqual(_detect_provider("claude-sonnet-4-20250514", None), "anthropic")
        self.assertEqual(_detect_provider("deepseek-v3", None), "ebill")
        self.assertEqual(_detect_provider("qwen-max", None), "ebill")

    def test_detect_by_url(self):
        self.assertEqual(_detect_provider("x", "https://api.openai.com/v1"), "openai")
        self.assertEqual(_detect_provider("x", "https://api.anthropic.com/v1/messages"), "anthropic")
        self.assertEqual(_detect_provider("x", "http://ebill.baidu-int.com/v1/models/{model}"), "ebill")
        self.assertEqual(_detect_provider("x", "http://localhost:8000/v1"), "vllm")
        self.assertEqual(_detect_provider("x", "http://127.0.0.1:11434/v1"), "vllm")
        self.assertEqual(_detect_provider("x", "https://my-azure.openai.azure.com/v1"), "openai")

    def test_url_takes_precedence(self):
        self.assertEqual(_detect_provider("gpt-4o", "http://localhost:8000/v1"), "vllm")
        self.assertEqual(_detect_provider("deepseek-v3", "https://api.openai.com/v1"), "openai")


class ProviderFactoryTests(unittest.TestCase):
    def setUp(self):
        os.environ["OR_EVAL_API_KEY"] = "test-key"

    def test_creates_ebill_by_default(self):
        client = create_client("deepseek-v3")
        self.assertIsInstance(client, EBillProvider)
        self.assertEqual(client.model, "deepseek-v3")

    def test_creates_openai(self):
        client = create_client("gpt-4o", provider="openai", api_key="sk-test")
        self.assertIsInstance(client, OpenAIProvider)
        self.assertTrue(client.api_url.endswith("/chat/completions"))

    def test_creates_anthropic(self):
        client = create_client("claude-sonnet-4-20250514", provider="anthropic", api_key="sk-ant-test")
        self.assertIsInstance(client, AnthropicProvider)

    def test_creates_vllm(self):
        client = create_client("my-model", provider="vllm", api_key="x")
        self.assertIsInstance(client, VLLMProvider)
        self.assertIn("localhost:8000", client.api_url)

    def test_auto_routes_correctly(self):
        self.assertIsInstance(create_client("gpt-4o", api_key="x"), OpenAIProvider)
        self.assertIsInstance(create_client("claude-sonnet-4-20250514", api_key="x"), AnthropicProvider)
        self.assertIsInstance(create_client("deepseek-v3"), EBillProvider)
        # When eBill URL is passed, model name doesn't override
        self.assertIsInstance(
            create_client("gpt-4o", api_url="http://ebill.baidu-int.com/v1/models/{model}"),
            EBillProvider,
        )

    def test_unknown_provider_raises(self):
        config = ProviderConfig(provider="nonexistent", model="x", api_key="x")
        with self.assertRaises(ValueError):
            create_provider(config)

    def test_openai_url_normalization(self):
        client = create_client("gpt-4o", provider="openai", api_url="https://api.openai.com/v1", api_key="x")
        self.assertEqual(client.api_url, "https://api.openai.com/v1/chat/completions")

        client = create_client("gpt-4o", provider="openai", api_url="https://api.openai.com/v1/chat/completions", api_key="x")
        self.assertEqual(client.api_url, "https://api.openai.com/v1/chat/completions")


class LegacyCompatTests(unittest.TestCase):
    def setUp(self):
        os.environ["OR_EVAL_API_KEY"] = "test-key"

    def test_gemini_style_client_works(self):
        client = GeminiStyleClient(model="deepseek-v3", api_key="test-key")
        self.assertEqual(client.model, "deepseek-v3")
        self.assertTrue(hasattr(client, "generate"))

    def test_gemini_style_with_provider(self):
        client = GeminiStyleClient(model="gpt-4o", api_key="sk-test", provider="openai")
        self.assertEqual(client.model, "gpt-4o")
        self.assertIsInstance(client._provider, OpenAIProvider)


class ResponseExtractionTests(unittest.TestCase):
    def test_openai_text_extraction(self):
        data = {"choices": [{"message": {"content": "Hello world"}}]}
        self.assertEqual(_extract_openai_text(data), "Hello world")

        data = {"choices": [{"message": {"content": [{"text": "Part 1"}, {"text": "Part 2"}]}}]}
        self.assertEqual(_extract_openai_text(data), "Part 1\nPart 2")

        self.assertEqual(_extract_openai_text({"choices": []}), "")

    def test_gemini_text_extraction(self):
        data = {"candidates": [{"content": {"parts": [{"text": "Solution"}]}}]}
        self.assertEqual(_extract_gemini_text(data), "Solution")

        self.assertEqual(_extract_gemini_text({"candidates": []}), "")

    def test_anthropic_text_extraction(self):
        data = {"content": [{"type": "text", "text": "Here is code"}]}
        self.assertEqual(_extract_anthropic_text(data), "Here is code")

        data = {"content": [{"type": "text", "text": "A"}, {"type": "text", "text": "B"}]}
        self.assertEqual(_extract_anthropic_text(data), "A\nB")

        self.assertEqual(_extract_anthropic_text({"content": []}), "")


class ProviderConfigTests(unittest.TestCase):
    def test_config_defaults(self):
        config = ProviderConfig(model="test")
        self.assertEqual(config.provider, "auto")
        self.assertEqual(config.temperature, 0)
        self.assertEqual(config.max_tokens, 4096)
        self.assertEqual(config.timeout, 120)
        self.assertEqual(config.max_retries, 3)

    def test_config_overrides(self):
        config = ProviderConfig(
            provider="openai",
            model="gpt-4o",
            api_url="https://custom.api.com/v1",
            temperature=0.5,
            max_tokens=8192,
        )
        self.assertEqual(config.provider, "openai")
        self.assertEqual(config.max_tokens, 8192)
        self.assertEqual(config.temperature, 0.5)


if __name__ == "__main__":
    unittest.main()
