import pytest
from click.testing import CliRunner
from unittest.mock import AsyncMock, patch, MagicMock
import asyncio
import os
from llx.cli import llx

@pytest.fixture
def runner():
    return CliRunner()

def test_prompt_with_argument(runner):
    with patch('llx.commands.prompt_command.get_provider') as mock_get_provider:
        # Setup mock provider
        mock_provider = MagicMock()
        async def mock_invoke(*args):
            yield "response chunk"
        mock_provider.invoke = mock_invoke
        mock_get_provider.return_value = mock_provider
        
        result = runner.invoke(llx, ['prompt', '--model', 'openai:gpt4o', '--prompt', 'Hello'])
        assert result.exit_code == 0
        mock_get_provider.assert_called_once_with('openai', 'gpt4o')
        assert "response chunk" in result.output

def test_prompt_with_stdin(runner):
    with patch('llx.commands.prompt_command.get_provider') as mock_get_provider:
        # Setup mock provider
        mock_provider = MagicMock()
        async def mock_invoke(*args):
            yield "response chunk"
        mock_provider.invoke = mock_invoke
        mock_get_provider.return_value = mock_provider
        
        result = runner.invoke(llx, ['prompt', '--model', 'openai:text-davinci-003'], input='Hello from stdin')
        assert result.exit_code == 0
        mock_get_provider.assert_called_once_with('openai', 'text-davinci-003')
        assert "response chunk" in result.output

def test_prompt_without_prompt(runner):
    result = runner.invoke(llx, ['prompt', '--model', 'ollama:llama3.2'])
    assert result.exit_code != 0
    assert "Prompt is required either as an argument or via stdin." in result.output

