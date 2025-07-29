import pytest
import pytest_asyncio
from unittest.mock import patch, MagicMock
import os
from llx.utils import get_provider, fetch_api_response
from llx.providers.openai_provider import OpenAIProvider
from llx.providers.anthropic_provider import AnthropicProvider
from llx.providers.ollama_provider import OllamaProvider
from llx.providers.deepseek_provider import DeepseekProvider
from llx.providers.mistral_provider import MistralProvider
from llx.providers.gemini_provider import GeminiProvider
from llx.providers.xai_provider import XAIProvider
from llx.providers.perplexity_provider import PerplexityProvider


class TestGetProvider:
    """Test the get_provider function"""

    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'})
    def test_get_provider_openai(self):
        provider = get_provider("openai", "gpt-4")
        assert isinstance(provider, OpenAIProvider)

    def test_get_provider_anthropic(self):
        provider = get_provider("anthropic", "claude-3-sonnet")
        assert isinstance(provider, AnthropicProvider)

    def test_get_provider_ollama(self):
        provider = get_provider("ollama", "llama3.2")
        assert isinstance(provider, OllamaProvider)

    @patch.dict('os.environ', {'DEEPSEEK_API_KEY': 'test-key'})
    def test_get_provider_deepseek(self):
        provider = get_provider("deepseek", "deepseek-chat")
        assert isinstance(provider, DeepseekProvider)

    def test_get_provider_mistral(self):
        provider = get_provider("mistral", "mistral-large")
        assert isinstance(provider, MistralProvider)

    @patch.dict('os.environ', {'GEMINI_API_KEY': 'test-key'})
    def test_get_provider_gemini(self):
        provider = get_provider("gemini", "gemini-pro")
        assert isinstance(provider, GeminiProvider)

    @patch.dict('os.environ', {'XAI_API_KEY': 'test-key'})
    def test_get_provider_xai(self):
        provider = get_provider("xai", "grok-beta")
        assert isinstance(provider, XAIProvider)

    @patch.dict('os.environ', {'PERPLEXITY_API_KEY': 'test-key'})
    def test_get_provider_perplexity(self):
        provider = get_provider("perplexity", "llama-3.1-sonar-small-128k-online")
        assert isinstance(provider, PerplexityProvider)

    def test_get_provider_unsupported(self):
        with pytest.raises(ValueError, match="Unsupported provider: unknown"):
            get_provider("unknown", "model")


class TestFetchApiResponse:
    """Test the fetch_api_response function"""

    @pytest.mark.asyncio
    async def test_fetch_api_response_openai(self):
        with patch('llx.utils.OpenAIProvider') as mock_provider_class:
            mock_provider = MagicMock()
            mock_provider_class.return_value = mock_provider
            
            async def mock_invoke():
                yield "test response"
            
            mock_provider.invoke.return_value = mock_invoke()
            
            response_chunks = []
            async for chunk in fetch_api_response("openai", "gpt-4", "test prompt"):
                response_chunks.append(chunk)
            
            assert response_chunks == ["test response"]
            mock_provider_class.assert_called_once_with("gpt-4", "test prompt", None)

    @pytest.mark.asyncio
    async def test_fetch_api_response_with_attachment(self):
        with patch('llx.utils.AnthropicProvider') as mock_provider_class:
            mock_provider = MagicMock()
            mock_provider_class.return_value = mock_provider
            
            async def mock_invoke():
                yield "test response with attachment"
            
            mock_provider.invoke.return_value = mock_invoke()
            
            response_chunks = []
            async for chunk in fetch_api_response("anthropic", "claude-3-sonnet", "test prompt", "image.jpg"):
                response_chunks.append(chunk)
            
            assert response_chunks == ["test response with attachment"]
            mock_provider_class.assert_called_once_with("claude-3-sonnet", "test prompt", "image.jpg")

    @pytest.mark.asyncio
    async def test_fetch_api_response_unsupported_provider(self):
        with pytest.raises(ValueError, match="Unsupported provider: unknown"):
            async for chunk in fetch_api_response("unknown", "model", "prompt"):
                pass