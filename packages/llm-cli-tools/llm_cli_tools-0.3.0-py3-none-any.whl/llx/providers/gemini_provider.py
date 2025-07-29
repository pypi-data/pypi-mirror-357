import os
from typing import List, Tuple, Optional
from google import genai
from collections.abc import AsyncIterator
from llx.providers.provider import Provider, UsageData

class GeminiProvider(Provider):
    def __init__(self, model: str):
        self.model = model
        self.client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        self.chat = self.client.chats.create(model=self.model)

    async def invoke(self, prompt: str, attachment: str=None, conversation_history: Optional[List[Tuple[str, str]]]=None) -> AsyncIterator[str]:
        response = self.chat.send_message_stream(prompt)
        for chunk in response:
            yield chunk.text

    async def invoke_with_usage(self, prompt: str, attachment: str=None, conversation_history: Optional[List[Tuple[str, str]]]=None) -> Tuple[str, UsageData]:
        """Get response with token estimation (provider doesn't expose usage data)"""
        # Collect streaming response
        stream = self.invoke(prompt, attachment, conversation_history)
        response_text = ""
        async for chunk in stream:
            response_text += chunk
        
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
        """List available Gemini models using Google's API"""
        models = self.client.models.list()
        return [model.name.replace('models/', '') for model in models]
