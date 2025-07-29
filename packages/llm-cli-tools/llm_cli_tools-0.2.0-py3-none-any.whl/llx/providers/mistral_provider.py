import os
import base64
from typing import List, Tuple, Optional
from mistralai import Mistral
from collections.abc import AsyncIterator
from llx.providers.provider import Provider, UsageData

class MistralProvider(Provider):
    def __init__(self, model: str):
        self.model = model
        self.client = Mistral(api_key=os.environ.get("MISTRAL_API_KEY"))

    async def invoke(self, prompt: str, attachment: str=None, conversation_history: Optional[List[Tuple[str, str]]]=None) -> AsyncIterator[str]:
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                ]
            }
        ]
        if attachment:
            with open(attachment, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode("utf-8")

            messages[0]["content"].append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                }
            })

        stream = self.client.chat.stream(
            model=self.model,
            messages=messages,
        )    
        for chunk in stream:
            yield chunk.data.choices[0].delta.content

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
        """List available Mistral models"""
        models = self.client.models.list()
        return [model.id for model in models.data]
