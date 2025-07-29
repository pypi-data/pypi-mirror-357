from abc import ABC, abstractmethod
from typing import AsyncIterator, List, Tuple, Optional, Dict, Any
from dataclasses import dataclass

@dataclass
class UsageData:
    """Token usage data from provider APIs"""
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    total_tokens: Optional[int] = None

class Provider(ABC):
    @abstractmethod
    def invoke(self, prompt: str, attachment: str=None, conversation_history: Optional[List[Tuple[str, str]]]=None) -> AsyncIterator[str]:
        pass
    
    @abstractmethod
    async def invoke_with_usage(self, prompt: str, attachment: str=None, conversation_history: Optional[List[Tuple[str, str]]]=None) -> Tuple[str, UsageData]:
        """
        Invoke the provider and return both response text and usage data.
        Default implementation collects streaming response and estimates usage.
        """
        pass
    
    async def list_models(self) -> List[str]:
        """
        List available models for this provider.
        Returns empty list if not supported by provider.
        """
        return []

