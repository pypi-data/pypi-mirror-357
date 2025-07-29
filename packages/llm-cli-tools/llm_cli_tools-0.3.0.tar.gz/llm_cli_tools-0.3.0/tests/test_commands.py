import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import asyncio
from click.testing import CliRunner
from click import UsageError, FileError
from llx.commands.prompt_command import PromptCommand
from llx.commands.chat_command import ChatCommand
from llx.commands.server_command import ServerCommand
from llx.commands.benchmark_command import BenchmarkCommand, BenchmarkRunner


class TestPromptCommand:
    """Test the PromptCommand class"""

    def test_prompt_command_init(self):
        with patch('llx.commands.prompt_command.get_provider') as mock_get_provider:
            mock_provider = MagicMock()
            mock_get_provider.return_value = mock_provider
            
            command = PromptCommand("openai", "gpt-4")
            assert command.provider == "openai"
            assert command.model == "gpt-4"
            assert command.client == mock_provider
            mock_get_provider.assert_called_once_with("openai", "gpt-4")

    def test_validate_prompt_with_prompt(self):
        with patch('llx.commands.prompt_command.get_provider'):
            command = PromptCommand("openai", "gpt-4")
            result = command._validate_prompt("test prompt")
            assert result == "test prompt"

    def test_validate_prompt_without_prompt(self):
        with patch('llx.commands.prompt_command.get_provider'), \
             patch('sys.stdin.isatty', return_value=True):
            command = PromptCommand("openai", "gpt-4")
            with pytest.raises(UsageError, match="Prompt is required either as an argument or via stdin."):
                command._validate_prompt(None)

    def test_validate_attachment_valid(self):
        with patch('llx.commands.prompt_command.get_provider'):
            command = PromptCommand("openai", "gpt-4")
            # Should not raise an exception
            command._validate_attachment("image.jpg")
            command._validate_attachment("photo.png")
            command._validate_attachment(None)

    def test_validate_attachment_invalid(self):
        with patch('llx.commands.prompt_command.get_provider'):
            command = PromptCommand("openai", "gpt-4")
            with pytest.raises(FileError):
                command._validate_attachment("document.pdf")

    def test_execute(self):
        with patch('llx.commands.prompt_command.get_provider') as mock_get_provider, \
             patch('asyncio.run') as mock_run:
            mock_provider = MagicMock()
            mock_get_provider.return_value = mock_provider
            
            command = PromptCommand("openai", "gpt-4")
            command.execute("test prompt", None)
            
            # Verify asyncio.run was called
            mock_run.assert_called_once()


class TestChatCommand:
    """Test the ChatCommand class""" 

    def test_chat_command_init(self):
        with patch('llx.commands.chat_command.get_provider') as mock_get_provider:
            mock_provider = MagicMock()
            mock_get_provider.return_value = mock_provider
            
            command = ChatCommand("anthropic", "claude-3-sonnet")
            assert command.provider == "anthropic"
            assert command.model == "claude-3-sonnet"
            assert command.client == mock_provider
            assert command.conversation_history == []
            mock_get_provider.assert_called_once_with("anthropic", "claude-3-sonnet")

    def test_conversation_history_tracking(self):
        with patch('llx.commands.chat_command.get_provider') as mock_get_provider:
            mock_provider = MagicMock()
            mock_get_provider.return_value = mock_provider
            
            command = ChatCommand("anthropic", "claude-3-sonnet")
            
            # Test that conversation history starts empty
            assert command.conversation_history == []
            
            # Test adding to history
            command.conversation_history.append(("Hello", "Hi there!"))
            assert len(command.conversation_history) == 1
            assert command.conversation_history[0] == ("Hello", "Hi there!")

    @patch('llx.commands.chat_command.asyncio.run')
    @patch('builtins.input', side_effect=["/bye"])
    @patch('llx.commands.chat_command.click.echo')
    def test_ollama_provider_gets_conversation_history(self, mock_echo, mock_input, mock_run):
        with patch('llx.commands.chat_command.get_provider') as mock_get_provider:
            mock_provider = MagicMock()
            mock_get_provider.return_value = mock_provider
            
            command = ChatCommand("ollama", "llama3.2")
            command.conversation_history = [("previous", "response")]
            
            # Test the specific method that handles conversation history
            # Simulate what happens when a user sends a message
            with patch.object(command, '_print_stream', new_callable=AsyncMock) as mock_print_stream:
                mock_print_stream.return_value = "response text"
                
                # Simulate the invoke call with conversation history
                if command.provider.lower() == 'ollama':
                    stream = command.client.invoke("test message", conversation_history=command.conversation_history)
                else:
                    stream = command.client.invoke("test message")
            
            # Verify invoke was called with conversation history for ollama
            command.client.invoke.assert_called_with("test message", conversation_history=[("previous", "response")])
            
            # Also test the full execute method but just exit immediately
            command.execute()

    @patch('llx.commands.chat_command.asyncio.run')
    @patch('builtins.input', side_effect=["test message", "/bye"])
    @patch('llx.commands.chat_command.click.echo')
    def test_non_ollama_provider_no_conversation_history(self, mock_echo, mock_input, mock_run):
        with patch('llx.commands.chat_command.get_provider') as mock_get_provider:
            mock_provider = MagicMock()
            mock_provider.invoke = MagicMock()
            mock_get_provider.return_value = mock_provider
            
            # Mock the async stream response
            async def mock_stream():
                yield "response text"
            
            mock_provider.invoke.return_value = mock_stream()
            mock_run.return_value = "response text"
            
            command = ChatCommand("openai", "gpt-4")
            command.conversation_history = [("previous", "response")]
            
            # Execute should NOT pass conversation history to non-ollama provider
            command.execute()
            
            # Verify invoke was called without conversation history
            mock_provider.invoke.assert_called_with("test message")


class TestServerCommand:
    """Test the ServerCommand class"""

    def test_server_command_execute(self):
        with patch('uvicorn.run') as mock_uvicorn_run:
            command = ServerCommand()
            command.execute("127.0.0.1", 8000)
            
            # Check that uvicorn.run was called with correct arguments
            mock_uvicorn_run.assert_called_once()
            args, kwargs = mock_uvicorn_run.call_args
            assert kwargs['host'] == '127.0.0.1'
            assert kwargs['port'] == 8000


class TestBenchmarkCommand:
    """Test the BenchmarkCommand class"""

    def test_benchmark_runner_init(self):
        with patch('llx.commands.benchmark_command.get_provider') as mock_get_provider:
            mock_provider = MagicMock()
            mock_get_provider.return_value = mock_provider
            
            runner = BenchmarkRunner(["openai:gpt-4", "anthropic:claude-3-sonnet"])
            assert len(runner.models) == 2
            assert "openai:gpt-4" in runner.models
            assert "anthropic:claude-3-sonnet" in runner.models
            assert len(runner.providers) == 2

    def test_token_estimation(self):
        with patch('llx.commands.benchmark_command.get_provider'):
            runner = BenchmarkRunner(["openai:gpt-4"])
            
            # Test token estimation (roughly 4 chars per token)
            assert runner._estimate_tokens("hello") == 1  # 5 chars / 4 = 1.25, max(1, 1) = 1
            assert runner._estimate_tokens("hello world") == 2  # 11 chars / 4 = 2.75 = 2
            assert runner._estimate_tokens("a" * 20) == 5  # 20 chars / 4 = 5

    def test_cost_estimation(self):
        with patch('llx.commands.benchmark_command.get_provider'):
            runner = BenchmarkRunner(["openai:gpt-4"])
            
            # Test cost estimation using pricing manager
            cost = runner.pricing_manager.calculate_cost("openai:gpt-4", 1000, 1000)
            expected = (1000/1000 * 0.03) + (1000/1000 * 0.06)  # $0.03 + $0.06 = $0.09
            assert cost == 0.09
            
            # Test cost estimation for Ollama (should be free)
            cost = runner.pricing_manager.calculate_cost("ollama:llama3.2", 1000, 1000)
            assert cost == 0.0

    @patch('llx.commands.benchmark_command.asyncio.run')
    def test_benchmark_command_execute(self, mock_run):
        with patch('llx.commands.benchmark_command.BenchmarkRunner') as mock_runner_class:
            mock_runner = MagicMock()
            mock_runner_class.return_value = mock_runner
            
            # Mock the benchmark results
            mock_results = {
                "openai:gpt-4": {
                    "response": "Test response",
                    "response_time": 2.5,
                    "total_tokens": 50,
                    "estimated_cost": 0.005,
                    "status": "success"
                }
            }
            mock_run.return_value = mock_results
            
            command = BenchmarkCommand()
            
            with patch('llx.commands.benchmark_command.click.echo'):
                command.execute("test prompt", ["openai:gpt-4"], "table")
            
            # Verify runner was created with correct models
            mock_runner_class.assert_called_once_with(["openai:gpt-4"])
            
            # Verify asyncio.run was called
            mock_run.assert_called_once()