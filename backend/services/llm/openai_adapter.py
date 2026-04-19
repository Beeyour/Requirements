import os
from typing import List, Dict
from openai import OpenAI
from .base_adapter import BaseLLMAdapter

class OpenAIAdapter(BaseLLMAdapter):
    """
    Adapter for OpenAI Chat Completion API.
    """
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY is not set")
        self.client = OpenAI(api_key=self.api_key)

    def call(self, model: str, system_prompt: str, messages: List[Dict[str, str]], 
             temperature: float, max_tokens: int) -> str:
        # Prepare message history with system instruction
        full_messages = [{"role": "system", "content": system_prompt}] + list(messages)
        
        response = self.client.chat.completions.create(
            model=model,
            messages=full_messages,
            temperature=temperature,
            max_completion_tokens=max_tokens,
        )
        return response.choices[0].message.content or ""