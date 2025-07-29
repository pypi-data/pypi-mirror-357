from ollama import chat, list as ollama_list
from collections.abc import AsyncIterator
from typing import List, Tuple, Optional
from llx.providers.provider import Provider, UsageData

class OllamaProvider(Provider):
    def __init__(self, model: str):
        self.model = model

    async def invoke(self, prompt: str, attachment: str=None, conversation_history: Optional[List[Tuple[str, str]]]=None) -> AsyncIterator[str]:
        messages = []
        
        # Add conversation history if provided
        if conversation_history:
            for user_msg, assistant_msg in conversation_history:
                messages.append({'role': 'user', 'content': user_msg})
                messages.append({'role': 'assistant', 'content': assistant_msg})
        
        # Add current user message
        messages.append({'role': 'user', 'content': prompt})
        
        stream = chat(
            model=self.model,
            messages=messages,
            stream=True,
        )

        for chunk in stream:
            yield chunk['message']['content']
    
    async def invoke_with_usage(self, prompt: str, attachment: str=None, conversation_history: Optional[List[Tuple[str, str]]]=None) -> Tuple[str, UsageData]:
        """Get response from Ollama - no usage data available, use estimation"""
        messages = []
        
        # Add conversation history if provided
        if conversation_history:
            for user_msg, assistant_msg in conversation_history:
                messages.append({'role': 'user', 'content': user_msg})
                messages.append({'role': 'assistant', 'content': assistant_msg})
        
        # Add current user message
        messages.append({'role': 'user', 'content': prompt})
        
        # Use non-streaming to get complete response
        response = chat(
            model=self.model,
            messages=messages,
            stream=False
        )
        
        response_text = response['message']['content']
        
        # Estimate tokens (roughly 4 chars per token)
        input_tokens = max(1, len(prompt) // 4)
        output_tokens = max(1, len(response_text) // 4)
        
        usage_data = UsageData(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens
        )
        
        return response_text, usage_data
    
    async def list_models(self) -> List[str]:
        """List available Ollama models"""
        models_response = ollama_list()
        return [model.model for model in models_response.models]
