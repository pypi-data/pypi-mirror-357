import time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Literal
from fastapi.responses import StreamingResponse
import asyncio
from llx.utils import get_provider
import json
import logging

app = FastAPI()

class Message(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[Message]
    stream: Optional[bool] = False
    temperature: Optional[float] = 1.0
    top_p: Optional[float] = 1.0
    n: Optional[int] = 1
    max_tokens: Optional[int] = None

class DeltaMessage(BaseModel):
    role: Optional[str] = None
    content: Optional[str] = None

class Choice(BaseModel):
    index: int
    message: Optional[Message] = None
    delta: Optional[DeltaMessage] = None
    logprobs: Optional[Any] = None
    finish_reason: Optional[str] = None

class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[Choice]
    usage: Optional[Dict[str, int]] = None

@app.post("/v1/chat/completions", response_model=ChatCompletionResponse)
async def chat_completions(request: ChatCompletionRequest):
    if not request.messages:
        raise HTTPException(status_code=400, detail="Messages are required")

    provider, model = request.model.split(':', 1)
    client = get_provider(provider, model)
    prompt = "\n".join([f"role: {message.role}\nmessage: {message.content}" for message in request.messages])

    try:
        if request.stream:
            async def stream_generator():
                response_id = f"llx-{int(time.time())}"
                chunk_id = 0
                
                try:
                    async for chunk in client.invoke(prompt):
                        # Skip empty chunks
                        if chunk.strip():
                            response = {
                                "id": response_id,
                                "object": "chat.completion.chunk",
                                "created": int(time.time()),
                                "model": request.model,
                                "choices": [{
                                    "index": 0,
                                    "delta": {
                                        "content": chunk
                                    },
                                    "finish_reason": None
                                }]
                            }
                            yield f"data: {json.dumps(response)}\n\n"
                        chunk_id += 1
                    
                    # Final chunk
                    response = {
                        "id": response_id,
                        "object": "chat.completion.chunk",
                        "created": int(time.time()),
                        "model": request.model,
                        "choices": [{
                            "index": 0,
                            "delta": {},
                            "finish_reason": "stop"
                        }]
                    }
                    yield f"data: {json.dumps(response)}\n\n"
                    yield "data: [DONE]\n\n"
                    
                except Exception as e:
                    logging.error(f"Streaming error: {str(e)}")
                    raise HTTPException(status_code=500, detail="Internal Server Error")

            return StreamingResponse(
                stream_generator(),
                media_type="text/event-stream"
            )
        
        else:
            # Non-streaming response
            full_response = ""
            async for chunk in client.invoke(prompt):
                full_response += chunk

            return ChatCompletionResponse(
                id=f"llx-{int(time.time())}",
                created=int(time.time()),
                model=request.model,
                choices=[
                    Choice(
                        index=0,
                        message=Message(
                            role="assistant",
                            content=full_response
                        ),
                        finish_reason="stop"
                    )
                ],
                usage={
                    "prompt_tokens": len(prompt.split()),
                    "completion_tokens": len(full_response.split()),
                    "total_tokens": len(prompt.split()) + len(full_response.split())
                }
            )

    except Exception as e:
        logging.error(f"Error in chat completions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))