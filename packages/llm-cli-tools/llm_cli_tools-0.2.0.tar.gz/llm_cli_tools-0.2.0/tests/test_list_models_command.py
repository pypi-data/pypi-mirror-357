import pytest
import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch
from llx.commands.list_models_command import ListModelsCommand


class TestListModelsCommand:
    """Test the ListModelsCommand class"""

    def test_list_models_command_init(self):
        command = ListModelsCommand()
        assert len(command.providers) > 0
        assert 'openai' in command.providers
        assert 'anthropic' in command.providers
        assert 'ollama' in command.providers

    @patch('llx.commands.list_models_command.get_provider')
    def test_get_models_for_provider_success(self, mock_get_provider):
        # Mock the provider
        mock_provider = AsyncMock()
        mock_provider.list_models = AsyncMock(return_value=['model1', 'model2', 'model3'])
        mock_get_provider.return_value = mock_provider
        
        command = ListModelsCommand()
        
        # Test getting models for a provider
        async def test_get_models():
            result = await command._get_models_for_provider('openai')
            return result
        
        result = asyncio.run(test_get_models())
        
        assert result == ['model1', 'model2', 'model3']
        mock_get_provider.assert_called_once()

    @patch('llx.commands.list_models_command.get_provider')
    def test_get_models_for_provider_error(self, mock_get_provider):
        # Mock the provider to raise an exception
        mock_get_provider.side_effect = Exception("API Error")
        
        command = ListModelsCommand()
        
        # Test error handling
        async def test_get_models():
            result = await command._get_models_for_provider('openai')
            return result
        
        result = asyncio.run(test_get_models())
        
        assert result == []

    @patch('llx.commands.list_models_command.get_provider')
    def test_get_models_for_provider_empty_response(self, mock_get_provider):
        # Mock the provider to return empty list
        mock_provider = AsyncMock()
        mock_provider.list_models = AsyncMock(return_value=[])
        mock_get_provider.return_value = mock_provider
        
        command = ListModelsCommand()
        
        # Test empty response
        async def test_get_models():
            result = await command._get_models_for_provider('openai')
            return result
        
        result = asyncio.run(test_get_models())
        
        assert result == []

    @patch('llx.commands.list_models_command.get_provider')
    def test_get_all_models(self, mock_get_provider):
        # Mock different providers with different responses
        def mock_provider_factory(provider_name, model_name):
            mock_provider = AsyncMock()
            if provider_name == 'openai':
                mock_provider.list_models = AsyncMock(return_value=['gpt-4', 'gpt-3.5-turbo'])
            elif provider_name == 'anthropic':
                mock_provider.list_models = AsyncMock(return_value=['claude-3-sonnet'])
            else:
                mock_provider.list_models = AsyncMock(return_value=[])
            return mock_provider
        
        mock_get_provider.side_effect = mock_provider_factory
        
        command = ListModelsCommand()
        
        # Test getting all models
        async def test_get_all():
            result = await command._get_all_models()
            return result
        
        result = asyncio.run(test_get_all())
        
        assert 'openai' in result
        assert 'anthropic' in result
        assert result['openai'] == ['gpt-3.5-turbo', 'gpt-4']  # Should be sorted
        assert result['anthropic'] == ['claude-3-sonnet']

    @patch('asyncio.run')
    @patch('click.echo')
    def test_execute_specific_provider_table(self, mock_echo, mock_run):
        mock_run.return_value = ['model1', 'model2']
        
        command = ListModelsCommand()
        command.execute(provider='openai', output_format='table')
        
        # Check that echo was called (output was generated)
        assert mock_echo.call_count > 0

    @patch('asyncio.run')
    @patch('click.echo')
    def test_execute_specific_provider_json(self, mock_echo, mock_run):
        mock_run.return_value = ['model1', 'model2']
        
        command = ListModelsCommand()
        command.execute(provider='openai', output_format='json')
        
        # Check that echo was called with JSON output
        assert mock_echo.call_count > 0
        # Should contain JSON-formatted data
        json_calls = [call for call in mock_echo.call_args_list if call[0] and '{' in str(call[0][0])]
        assert len(json_calls) > 0

    @patch('click.echo')
    def test_execute_unknown_provider(self, mock_echo):
        command = ListModelsCommand()
        command.execute(provider='unknown', output_format='table')
        
        # Should show error message
        error_calls = [call for call in mock_echo.call_args_list 
                      if call[0] and 'Unknown provider' in str(call[0][0])]
        assert len(error_calls) > 0

    @patch('asyncio.run')
    @patch('click.echo')
    def test_execute_all_providers(self, mock_echo, mock_run):
        mock_run.return_value = {
            'openai': ['gpt-4', 'gpt-3.5-turbo'],
            'anthropic': ['claude-3-sonnet']
        }
        
        command = ListModelsCommand()
        command.execute(provider=None, output_format='table')
        
        # Check that output was generated
        assert mock_echo.call_count > 0

    def test_output_json_format(self):
        command = ListModelsCommand()
        
        # Capture the JSON output
        import io
        import sys
        from unittest.mock import patch
        
        captured_output = io.StringIO()
        
        with patch('click.echo') as mock_echo:
            mock_echo.side_effect = lambda x: captured_output.write(str(x) + '\n')
            
            test_data = {
                'openai': ['gpt-4', 'gpt-3.5-turbo'],
                'anthropic': ['claude-3-sonnet']
            }
            
            command._output_json(test_data)
        
        # Verify JSON structure
        output = captured_output.getvalue()
        parsed = json.loads(output)
        
        assert 'providers' in parsed
        assert 'summary' in parsed
        assert parsed['providers'] == test_data
        assert parsed['summary']['total_models'] == 3
        assert parsed['summary']['available_providers'] == 2

    @patch('click.echo')
    def test_output_table_format(self, mock_echo):
        command = ListModelsCommand()
        
        test_data = {
            'openai': ['gpt-4', 'gpt-3.5-turbo'],
            'anthropic': ['claude-3-sonnet'],
            'empty_provider': []
        }
        
        command._output_table(test_data)
        
        # Check that appropriate output was generated
        assert mock_echo.call_count > 0
        
        # Check for provider headers
        header_calls = [call for call in mock_echo.call_args_list 
                       if call[0] and any(provider.upper() in str(call[0][0]) 
                                        for provider in ['OPENAI', 'ANTHROPIC'])]
        assert len(header_calls) >= 2