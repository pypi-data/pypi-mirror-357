import os
import base64
from openai import OpenAI
from collections.abc import AsyncIterator
from typing import List, Tuple, Optional
from llx.providers.provider import Provider, UsageData

class OpenAIProvider(Provider):
    def __init__(self, model: str):
        self.model = model
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

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

        stream = self.client.chat.completions.create(
            messages=messages,
            model=self.model,
            stream=True
        )    
        for chunk in stream:
            yield chunk.choices[0].delta.content
    
    async def invoke_with_usage(self, prompt: str, attachment: str=None, conversation_history: Optional[List[Tuple[str, str]]]=None) -> Tuple[str, UsageData]:
        """Get response with actual token usage from OpenAI API"""
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

        # Use non-streaming to get usage data
        response = self.client.chat.completions.create(
            messages=messages,
            model=self.model,
            stream=False
        )
        
        response_text = response.choices[0].message.content
        usage_data = UsageData(
            input_tokens=response.usage.prompt_tokens,
            output_tokens=response.usage.completion_tokens,
            total_tokens=response.usage.total_tokens
        )
        
        return response_text, usage_data
    
    async def list_models(self) -> List[str]:
        """List available OpenAI models"""
        models = self.client.models.list()
        return [model.id for model in models.data if 'gpt' in model.id.lower()]
