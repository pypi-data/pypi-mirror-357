import pytest
import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch
from llx.response_judge import ResponseJudge
from llx.providers.provider import UsageData


class TestResponseJudge:
    """Test the ResponseJudge class"""

    @patch('llx.response_judge.get_provider')
    def test_response_judge_init(self, mock_get_provider):
        mock_get_provider.return_value = MagicMock()
        judge = ResponseJudge("openai:gpt-4")
        assert judge.judge_model == "openai:gpt-4"
        assert judge.judge_prompt == ResponseJudge.DEFAULT_JUDGE_PROMPT

    @patch('llx.response_judge.get_provider')
    def test_response_judge_init_with_custom_prompt(self, mock_get_provider):
        mock_get_provider.return_value = MagicMock()
        custom_prompt = "Rate this response: {response}"
        judge = ResponseJudge("openai:gpt-4", custom_prompt)
        assert judge.judge_prompt == custom_prompt

    @patch('llx.response_judge.get_provider')
    def test_parse_judgment_valid_json(self, mock_get_provider):
        mock_get_provider.return_value = MagicMock()
        judge = ResponseJudge("openai:gpt-4")
        
        valid_response = '''
        {"score": 8, "reasoning": "Good response", "strengths": ["clear"], "weaknesses": ["short"]}
        '''
        
        result = judge._parse_judgment(valid_response)
        assert result["score"] == 8
        assert result["reasoning"] == "Good response"
        assert result["strengths"] == ["clear"]
        assert result["weaknesses"] == ["short"]

    @patch('llx.response_judge.get_provider')
    def test_parse_judgment_json_with_markdown(self, mock_get_provider):
        mock_get_provider.return_value = MagicMock()
        judge = ResponseJudge("openai:gpt-4")
        
        markdown_response = '''
        Here's my evaluation:
        ```json
        {"score": 7, "reasoning": "Decent response", "strengths": ["accurate"]}
        ```
        '''
        
        result = judge._parse_judgment(markdown_response)
        assert result["score"] == 7
        assert result["reasoning"] == "Decent response"
        assert result["strengths"] == ["accurate"]
        assert result["weaknesses"] == []  # Should default to empty list

    @patch('llx.response_judge.get_provider')
    def test_parse_judgment_malformed_json_fallback(self, mock_get_provider):
        mock_get_provider.return_value = MagicMock()
        judge = ResponseJudge("openai:gpt-4")
        
        malformed_response = "I think this response deserves a score: 6 out of 10 because it's okay."
        
        result = judge._parse_judgment(malformed_response)
        assert result["score"] == 6
        assert "Parse error" in result["reasoning"] or "okay" in result["reasoning"]
        assert result["strengths"] == []
        assert result["weaknesses"] == []

    @patch('llx.response_judge.get_provider')
    def test_parse_judgment_no_score_fallback(self, mock_get_provider):
        mock_get_provider.return_value = MagicMock()
        judge = ResponseJudge("openai:gpt-4")
        
        no_score_response = "This is a good response but I can't provide a specific rating."
        
        result = judge._parse_judgment(no_score_response)
        assert result["score"] == 5.0  # Default fallback score
        assert result["strengths"] == []
        assert result["weaknesses"] == []

    @patch('llx.response_judge.get_provider')
    def test_parse_judgment_score_validation(self, mock_get_provider):
        mock_get_provider.return_value = MagicMock()
        judge = ResponseJudge("openai:gpt-4")
        
        # Test that invalid scores trigger fallback
        high_score_response = '{"score": 15, "reasoning": "Too high"}'
        result = judge._parse_judgment(high_score_response)
        # Invalid score should trigger fallback mechanism
        assert result["score"] == 5.0  # Fallback score
        
        # Test valid score
        valid_score_response = '{"score": 8, "reasoning": "Good"}'
        result = judge._parse_judgment(valid_score_response)
        assert result["score"] == 8  # Valid score should be preserved

    @patch('llx.response_judge.get_provider')
    def test_judge_response_success(self, mock_get_provider):
        # Mock the provider
        mock_provider = AsyncMock()
        mock_provider.invoke_with_usage = AsyncMock(
            return_value=('{"score": 8, "reasoning": "Good response"}', UsageData())
        )
        mock_get_provider.return_value = mock_provider
        
        judge = ResponseJudge("openai:gpt-4")
        
        # Test judging a response
        async def test_judge():
            result = await judge.judge_response("What is AI?", "AI is artificial intelligence", "test:model")
            return result
        
        result = asyncio.run(test_judge())
        
        assert result["score"] == 8
        assert result["reasoning"] == "Good response"
        assert result["model_evaluated"] == "test:model"
        assert result["judge_model"] == "openai:gpt-4"
        assert result["status"] == "success"

    @patch('llx.response_judge.get_provider')
    def test_judge_response_error_handling(self, mock_get_provider):
        # Mock the provider to raise an exception
        mock_provider = AsyncMock()
        mock_provider.invoke_with_usage = AsyncMock(side_effect=Exception("API Error"))
        mock_get_provider.return_value = mock_provider
        
        judge = ResponseJudge("openai:gpt-4")
        
        # Test error handling
        async def test_judge():
            result = await judge.judge_response("What is AI?", "AI is artificial intelligence", "test:model")
            return result
        
        result = asyncio.run(test_judge())
        
        assert result["status"] == "error"
        assert "API Error" in result["error"]
        assert result["score"] is None
        assert result["model_evaluated"] == "test:model"

    @patch('llx.response_judge.get_provider')
    def test_judge_multiple_responses(self, mock_get_provider):
        # Mock the provider
        mock_provider = AsyncMock()
        mock_provider.invoke_with_usage = AsyncMock(
            return_value=('{"score": 7, "reasoning": "Good"}', UsageData())
        )
        mock_get_provider.return_value = mock_provider
        
        judge = ResponseJudge("openai:gpt-4")
        
        responses = {
            "model1": "Response 1",
            "model2": "Response 2"
        }
        
        # Test judging multiple responses
        async def test_judge():
            result = await judge.judge_multiple_responses("Test prompt", responses)
            return result
        
        result = asyncio.run(test_judge())
        
        assert len(result) == 2
        assert "model1" in result
        assert "model2" in result
        assert result["model1"]["score"] == 7
        assert result["model2"]["score"] == 7

    def test_default_judge_prompts(self):
        from llx.response_judge import create_default_judge_prompts
        
        prompts = create_default_judge_prompts()
        
        assert "general" in prompts
        assert "code_quality" in prompts
        assert "factual_accuracy" in prompts
        assert "creativity" in prompts
        
        # Test that prompts contain placeholders
        assert "{original_prompt}" in prompts["general"]
        assert "{response}" in prompts["general"]
    
    @patch('llx.response_judge.get_provider')
    def test_comparative_judge_success(self, mock_get_provider):
        # Mock the provider
        mock_provider = AsyncMock()
        mock_response = '''{
            "ranking": ["model1", "model2"],
            "winner": "model1",
            "scores": {"model1": 9, "model2": 7},
            "comparison": "Model1 provides better accuracy",
            "strengths": {"model1": ["accurate"], "model2": ["clear"]},
            "weaknesses": {"model1": ["verbose"], "model2": ["incomplete"]}
        }'''
        mock_provider.invoke_with_usage = AsyncMock(
            return_value=(mock_response, UsageData())
        )
        mock_get_provider.return_value = mock_provider
        
        judge = ResponseJudge("openai:gpt-4")
        
        responses = {
            "model1": "Response 1",
            "model2": "Response 2"
        }
        
        # Test comparative judging
        async def test_comparative():
            result = await judge.comparative_judge("Test prompt", responses)
            return result
        
        result = asyncio.run(test_comparative())
        
        assert result["status"] == "success"
        assert result["winner"] == "model1"
        assert result["ranking"] == ["model1", "model2"]
        assert result["scores"]["model1"] == 9
        assert result["scores"]["model2"] == 7
        assert "Model1 provides better accuracy" in result["comparison"]
    
    @patch('llx.response_judge.get_provider')
    def test_comparative_judge_error_handling(self, mock_get_provider):
        # Mock the provider to raise an exception
        mock_provider = AsyncMock()
        mock_provider.invoke_with_usage = AsyncMock(side_effect=Exception("API Error"))
        mock_get_provider.return_value = mock_provider
        
        judge = ResponseJudge("openai:gpt-4")
        
        responses = {
            "model1": "Response 1",
            "model2": "Response 2"
        }
        
        # Test error handling
        async def test_comparative():
            result = await judge.comparative_judge("Test prompt", responses)
            return result
        
        result = asyncio.run(test_comparative())
        
        assert result["status"] == "error"
        assert "API Error" in result["error"]
        assert result["winner"] is None
        assert result["ranking"] == ["model1", "model2"]  # Fallback
    
    @patch('llx.response_judge.get_provider')
    def test_comparative_judge_insufficient_responses(self, mock_get_provider):
        mock_get_provider.return_value = MagicMock()
        judge = ResponseJudge("openai:gpt-4")
        
        # Test with only one response
        responses = {"model1": "Response 1"}
        
        async def test_comparative():
            try:
                await judge.comparative_judge("Test prompt", responses)
                return False
            except ValueError as e:
                return "requires at least 2 responses" in str(e)
        
        result = asyncio.run(test_comparative())
        assert result is True
    
    @patch('llx.response_judge.get_provider')
    def test_comparative_judge_winner_consistency(self, mock_get_provider):
        # Mock the provider with inconsistent winner and ranking
        mock_provider = AsyncMock()
        mock_response = '''{
            "ranking": ["model2", "model1"],
            "winner": "model1",
            "scores": {"model1": 7, "model2": 9},
            "comparison": "Inconsistent response"
        }'''
        mock_provider.invoke_with_usage = AsyncMock(
            return_value=(mock_response, UsageData())
        )
        mock_get_provider.return_value = mock_provider
        
        judge = ResponseJudge("openai:gpt-4")
        
        responses = {
            "model1": "Response 1",
            "model2": "Response 2"
        }
        
        # Test that winner is corrected to match ranking[0]
        async def test_comparative():
            result = await judge.comparative_judge("Test prompt", responses)
            return result
        
        result = asyncio.run(test_comparative())
        
        assert result["status"] == "success"
        assert result["ranking"] == ["model2", "model1"]
        assert result["winner"] == "model2"  # Should be corrected to ranking[0]