from abc import ABC, abstractmethod
from typing import List, Dict

class BaseLLMAdapter(ABC):
    # Abstract interface for all LLM providers to ensure method consistency
    @abstractmethod
    async def call(
        self,
        model: str,
        system_prompt: str,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
        is_json: bool = False,
    ) -> str:
        # This method must be implemented as ASYNC by any specific LLM adapter
        # to remain compatible with the Agent and Service layers.
        pass