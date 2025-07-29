import pytest
from unittest.mock import patch, MagicMock
import asyncio
from llx.providers.ollama_provider import OllamaProvider
from llx.providers.openai_provider import OpenAIProvider


class TestOllamaProvider:
    """Test the OllamaProvider class"""

    def test_ollama_provider_init(self):
        provider = OllamaProvider("llama3.2")
        assert provider.model == "llama3.2"

    @patch('llx.providers.ollama_provider.chat')
    def test_invoke_without_conversation_history(self, mock_chat):
        # Mock the chat stream response
        mock_chat.return_value = [
            {'message': {'content': 'Hello '}},
            {'message': {'content': 'there!'}}
        ]
        
        provider = OllamaProvider("llama3.2")
        
        # Test invoke without conversation history
        async def test_stream():
            stream = provider.invoke("Hello")
            chunks = []
            async for chunk in stream:
                chunks.append(chunk)
            return chunks
        
        result = asyncio.run(test_stream())
        assert result == ['Hello ', 'there!']
        
        # Verify chat was called with correct parameters
        mock_chat.assert_called_once_with(
            model="llama3.2",
            messages=[{'role': 'user', 'content': 'Hello'}],
            stream=True
        )

    @patch('llx.providers.ollama_provider.chat')
    def test_invoke_with_conversation_history(self, mock_chat):
        # Mock the chat stream response
        mock_chat.return_value = [
            {'message': {'content': 'I remember '}},
            {'message': {'content': 'our chat!'}}
        ]
        
        provider = OllamaProvider("llama3.2")
        
        # Test invoke with conversation history
        conversation_history = [
            ("What's your name?", "I'm an AI assistant."),
            ("Do you remember that?", "Yes, I do.")
        ]
        
        async def test_stream():
            stream = provider.invoke("Tell me more", conversation_history=conversation_history)
            chunks = []
            async for chunk in stream:
                chunks.append(chunk)
            return chunks
        
        result = asyncio.run(test_stream())
        assert result == ['I remember ', 'our chat!']
        
        # Verify chat was called with conversation history
        expected_messages = [
            {'role': 'user', 'content': "What's your name?"},
            {'role': 'assistant', 'content': "I'm an AI assistant."},
            {'role': 'user', 'content': "Do you remember that?"},
            {'role': 'assistant', 'content': "Yes, I do."},
            {'role': 'user', 'content': "Tell me more"}
        ]
        
        mock_chat.assert_called_once_with(
            model="llama3.2",
            messages=expected_messages,
            stream=True
        )

    @patch('llx.providers.ollama_provider.chat')
    def test_invoke_with_empty_conversation_history(self, mock_chat):
        # Mock the chat stream response
        mock_chat.return_value = [
            {'message': {'content': 'Response'}}
        ]
        
        provider = OllamaProvider("llama3.2")
        
        # Test invoke with empty conversation history
        async def test_stream():
            stream = provider.invoke("Hello", conversation_history=[])
            chunks = []
            async for chunk in stream:
                chunks.append(chunk)
            return chunks
        
        result = asyncio.run(test_stream())
        assert result == ['Response']
        
        # Verify chat was called with just the current message
        mock_chat.assert_called_once_with(
            model="llama3.2",
            messages=[{'role': 'user', 'content': 'Hello'}],
            stream=True
        )


class TestOpenAIProvider:
    """Test that OpenAIProvider ignores conversation history"""

    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'})
    @patch('llx.providers.openai_provider.OpenAI')
    def test_invoke_ignores_conversation_history(self, mock_openai_class):
        # Mock the OpenAI client and its response
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        mock_stream = [
            MagicMock(choices=[MagicMock(delta=MagicMock(content='Hello'))]),
            MagicMock(choices=[MagicMock(delta=MagicMock(content=' world!'))])
        ]
        mock_client.chat.completions.create.return_value = mock_stream
        
        provider = OpenAIProvider("gpt-4")
        
        # Test invoke with conversation history (should be ignored)
        conversation_history = [
            ("Previous question", "Previous answer")
        ]
        
        async def test_stream():
            stream = provider.invoke("Hello", conversation_history=conversation_history)
            chunks = []
            async for chunk in stream:
                chunks.append(chunk)
            return chunks
        
        result = asyncio.run(test_stream())
        assert result == ['Hello', ' world!']
        
        # Verify that conversation history was ignored
        # Should only have the current user message
        expected_messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Hello"},
                ]
            }
        ]
        
        mock_client.chat.completions.create.assert_called_once_with(
            messages=expected_messages,
            model="gpt-4",
            stream=True
        )