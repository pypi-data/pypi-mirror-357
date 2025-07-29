import asyncio
import json
import re
from typing import Dict, Any, Optional
from llx.utils import get_provider


class ResponseJudge:
    """LLM-based response evaluation system"""
    
    DEFAULT_JUDGE_PROMPT = """Evaluate this AI response on a scale of 1-10 based on accuracy, relevance, and helpfulness.

Respond ONLY with this JSON format (no other text):
{{"score": 8, "reasoning": "Good response because...", "strengths": ["accurate", "clear"], "weaknesses": ["could be more detailed"]}}

Original Prompt: {original_prompt}
Response to Evaluate: {response}

JSON evaluation:"""

    def __init__(self, judge_model: str, judge_prompt: Optional[str] = None):
        self.judge_model = judge_model
        self.judge_prompt = judge_prompt or self.DEFAULT_JUDGE_PROMPT
        
        # Initialize judge provider
        provider_name, model_name = judge_model.split(':', 1)
        self.judge_provider = get_provider(provider_name, model_name)
    
    async def judge_response(self, original_prompt: str, response: str, model_name: str) -> Dict[str, Any]:
        """Judge a response using the configured LLM judge"""
        try:
            # Format the judge prompt
            evaluation_prompt = self.judge_prompt.format(
                original_prompt=original_prompt,
                response=response
            )
            
            # Get judgment from the judge model
            judge_response, _ = await self.judge_provider.invoke_with_usage(evaluation_prompt)
            
            # Debug: print raw response (remove in production)
            # print(f"DEBUG - Raw judge response: {judge_response[:500]}...")
            
            # Parse the JSON response
            judgment = self._parse_judgment(judge_response)
            
            # Add metadata
            judgment.update({
                "model_evaluated": model_name,
                "judge_model": self.judge_model,
                "status": "success"
            })
            
            return judgment
            
        except Exception as e:
            return {
                "model_evaluated": model_name,
                "judge_model": self.judge_model,
                "score": None,
                "reasoning": f"Judgment failed: {str(e)}",
                "strengths": [],
                "weaknesses": [],
                "status": "error",
                "error": str(e)
            }
    
    def _parse_judgment(self, judge_response: str) -> Dict[str, Any]:
        """Parse the judge's JSON response"""
        try:
            # Clean up the response - remove markdown code blocks if present
            cleaned_response = re.sub(r'```(?:json)?\n?(.*?)\n?```', r'\1', judge_response, flags=re.DOTALL)
            
            # Try to find JSON in the response
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', cleaned_response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                
                # Clean up common JSON formatting issues
                json_str = re.sub(r'//.*$', '', json_str, flags=re.MULTILINE)  # Remove comments
                json_str = re.sub(r',\s*}', '}', json_str)  # Remove trailing commas
                json_str = re.sub(r',\s*]', ']', json_str)  # Remove trailing commas in arrays
                
                judgment = json.loads(json_str)
                
                # Validate required fields
                if "score" not in judgment:
                    raise ValueError("Missing 'score' field in judgment")
                
                # Ensure score is valid
                score = judgment.get("score")
                if not isinstance(score, (int, float)) or not (1 <= score <= 10):
                    raise ValueError("Score must be a number between 1 and 10")
                
                # Ensure required fields exist with defaults
                judgment.setdefault("reasoning", "No reasoning provided")
                judgment.setdefault("strengths", [])
                judgment.setdefault("weaknesses", [])
                
                return judgment
            else:
                raise ValueError("No JSON found in response")
                
        except (json.JSONDecodeError, ValueError) as e:
            # Fallback: try to extract score and basic info from text
            score_match = re.search(r'(?:score|rating)[:\s]*(\d+(?:\.\d+)?)', judge_response, re.IGNORECASE)
            score = float(score_match.group(1)) if score_match else 5.0
            
            # Try to extract reasoning
            reasoning_match = re.search(r'(?:reasoning|explanation)[:\s]*([^"]*?)(?:\n|$)', judge_response, re.IGNORECASE)
            reasoning = reasoning_match.group(1).strip() if reasoning_match else f"Parse error: {str(e)}"
            
            return {
                "score": min(max(score, 1), 10),  # Clamp between 1-10
                "reasoning": reasoning[:200] + "..." if len(reasoning) > 200 else reasoning,
                "strengths": [],
                "weaknesses": []
            }
    
    async def judge_multiple_responses(self, original_prompt: str, responses: Dict[str, str]) -> Dict[str, Dict[str, Any]]:
        """Judge multiple responses in parallel"""
        tasks = []
        for model_name, response in responses.items():
            task = self.judge_response(original_prompt, response, model_name)
            tasks.append(task)
        
        # Execute judgments in parallel
        judgments = await asyncio.gather(*tasks)
        
        # Return as dict mapping model names to judgments
        return {
            model_name: judgment 
            for model_name, judgment in zip(responses.keys(), judgments)
        }
    
    async def comparative_judge(self, original_prompt: str, responses: Dict[str, str]) -> Dict[str, Any]:
        """Perform head-to-head comparison of responses"""
        if len(responses) < 2:
            raise ValueError("Comparative judging requires at least 2 responses")
        
        model_names = list(responses.keys())
        response_texts = list(responses.values())
        
        # Create comparative prompt
        comparative_prompt = f"""Compare these {len(responses)} AI responses to the same prompt and rank them from best to worst.

Original Prompt: {original_prompt}

Responses:
"""
        for i, (model, response) in enumerate(responses.items(), 1):
            comparative_prompt += f"""
Response {i} ({model}):
{response}
"""
        
        comparative_prompt += """
Evaluate each response on accuracy, relevance, helpfulness, and completeness.
Provide a ranking and detailed comparison.

Respond ONLY with this JSON format:
{
  "ranking": ["model1", "model2", "model3"],
  "winner": "model1",
  "scores": {"model1": 9, "model2": 7, "model3": 5},
  "comparison": "Detailed comparison explaining why winner is best...",
  "strengths": {"model1": ["strength1", "strength2"], "model2": ["strength1"]},
  "weaknesses": {"model1": ["weakness1"], "model2": ["weakness1", "weakness2"]}
}"""
        
        try:
            # Get comparative judgment
            judge_response, _ = await self.judge_provider.invoke_with_usage(comparative_prompt)
            
            # Parse the comparative judgment
            comparison = self._parse_comparative_judgment(judge_response, model_names)
            
            # Add metadata
            comparison.update({
                "original_prompt": original_prompt,
                "judge_model": self.judge_model,
                "models_compared": model_names,
                "status": "success"
            })
            
            return comparison
            
        except Exception as e:
            return {
                "original_prompt": original_prompt,
                "judge_model": self.judge_model,
                "models_compared": model_names,
                "status": "error",
                "error": str(e),
                "ranking": model_names,  # Fallback to original order
                "winner": None,
                "scores": {model: None for model in model_names},
                "comparison": f"Comparative judgment failed: {str(e)}"
            }
    
    def _parse_comparative_judgment(self, judge_response: str, model_names: list) -> Dict[str, Any]:
        """Parse comparative judgment JSON response"""
        try:
            # Clean up the response - remove markdown code blocks if present
            cleaned_response = re.sub(r'```(?:json)?\n?(.*?)\n?```', r'\1', judge_response, flags=re.DOTALL)
            
            # Try to find JSON in the response
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', cleaned_response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                
                # Clean up common JSON formatting issues
                json_str = re.sub(r'//.*$', '', json_str, flags=re.MULTILINE)
                json_str = re.sub(r',\s*}', '}', json_str)
                json_str = re.sub(r',\s*]', ']', json_str)
                
                comparison = json.loads(json_str)
                
                # Validate and set defaults
                comparison.setdefault("ranking", model_names)
                comparison.setdefault("winner", model_names[0] if model_names else None)
                comparison.setdefault("scores", {model: 5 for model in model_names})
                comparison.setdefault("comparison", "No comparison provided")
                comparison.setdefault("strengths", {model: [] for model in model_names})
                comparison.setdefault("weaknesses", {model: [] for model in model_names})
                
                # Ensure ranking contains valid model names
                valid_ranking = [m for m in comparison["ranking"] if m in model_names]
                if len(valid_ranking) != len(model_names):
                    comparison["ranking"] = model_names  # Fallback
                
                # Ensure winner is valid and consistent with ranking
                ranking = comparison.get("ranking", model_names)
                if ranking and (comparison.get("winner") not in model_names or comparison.get("winner") != ranking[0]):
                    comparison["winner"] = ranking[0]  # Winner should be first in ranking
                
                return comparison
            else:
                raise ValueError("No JSON found in response")
                
        except (json.JSONDecodeError, ValueError) as e:
            # Fallback parsing
            return {
                "ranking": model_names,
                "winner": model_names[0] if model_names else None,
                "scores": {model: 5 for model in model_names},
                "comparison": f"Parse error: {str(e)}. Raw response: {judge_response[:200]}...",
                "strengths": {model: [] for model in model_names},
                "weaknesses": {model: [] for model in model_names}
            }


def create_default_judge_prompts():
    """Predefined judge prompts for different use cases"""
    return {
        "general": ResponseJudge.DEFAULT_JUDGE_PROMPT,
        
        "code_quality": """You are a code review expert. Evaluate this code response based on:
1. **Correctness**: Does the code work and solve the problem?
2. **Quality**: Is it well-structured, readable, and following best practices?
3. **Efficiency**: Is it reasonably performant?
4. **Completeness**: Does it fully address the requirements?
5. **Documentation**: Are there helpful comments or explanations?

Rate 1-10 and provide JSON evaluation:
{{"score": <1-10>, "reasoning": "<explanation>", "strengths": ["..."], "weaknesses": ["..."]}}

Original Prompt: {original_prompt}
Code Response: {response}

Your evaluation:""",
        
        "factual_accuracy": """You are a fact-checker. Evaluate this response for factual accuracy:
1. **Accuracy**: Are the facts and information correct?
2. **Completeness**: Are there important missing facts?
3. **Sources**: Is the information well-sourced or commonly known?
4. **Currency**: Is the information up-to-date?
5. **Objectivity**: Is it balanced and unbiased?

Rate 1-10 and provide JSON evaluation:
{{"score": <1-10>, "reasoning": "<explanation>", "strengths": ["..."], "weaknesses": ["..."]}}

Original Prompt: {original_prompt}
Response: {response}

Your evaluation:""",
        
        "creativity": """You are a creativity evaluator. Judge this creative response on:
1. **Originality**: How unique and novel is the response?
2. **Creativity**: Does it show imaginative thinking?
3. **Engagement**: Is it interesting and engaging?
4. **Coherence**: Does it make sense and flow well?
5. **Appropriateness**: Is it suitable for the prompt?

Rate 1-10 and provide JSON evaluation:
{{"score": <1-10>, "reasoning": "<explanation>", "strengths": ["..."], "weaknesses": ["..."]}}

Original Prompt: {original_prompt}
Creative Response: {response}

Your evaluation:"""
    }