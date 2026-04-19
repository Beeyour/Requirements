from abc import ABC, abstractmethod
from typing import List, Dict

class BaseLLMAdapter(ABC):
    """
    Abstract base class defining the interface for all LLM adapters.
    """
    @abstractmethod
    def call(
        self, 
        model: str, 
        system_prompt: str, 
        messages: List[Dict[str, str]], 
        temperature: float, 
        max_tokens: int
    ) -> str:
        """
        Executes a call to the LLM provider.
        """
        pass