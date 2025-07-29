import os
import base64
import anthropic
from collections.abc import Iterator, AsyncIterator
from typing import List, Tuple, Optional
from llx.providers.provider import Provider, UsageData

class AnthropicProvider(Provider):
    def __init__(self, model):
        self.model = model
        self.client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    async def invoke(self, prompt: str, attachment: str=None, conversation_history: Optional[List[Tuple[str, str]]]=None) -> AsyncIterator[str]:        
        with self.client.messages.stream(
            model=self.model,
            max_tokens=1024,
            messages=[
                {"role": "user", "content": prompt}
            ]
        ) as stream:
            for chunk in stream.text_stream:
                yield chunk
    
    async def invoke_with_usage(self, prompt: str, attachment: str=None, conversation_history: Optional[List[Tuple[str, str]]]=None) -> Tuple[str, UsageData]:
        """Get response with actual token usage from Anthropic API"""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        response_text = response.content[0].text
        usage_data = UsageData(
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            total_tokens=response.usage.input_tokens + response.usage.output_tokens
        )
        
        return response_text, usage_data
    
    async def list_models(self) -> List[str]:
        """List available Anthropic models using their public API"""
        # Use Anthropic's models API
        models = self.client.models.list()
        return [model.id for model in models.data]
