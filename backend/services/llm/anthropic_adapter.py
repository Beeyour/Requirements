import os
from typing import List, Dict
import anthropic
from .base_adapter import BaseLLMAdapter

class AnthropicAdapter(BaseLLMAdapter):
    """
    Adapter for Anthropic Claude API.
    """
    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise RuntimeError("ANTHROPIC_API_KEY is not set")
        self.client = anthropic.Anthropic(api_key=self.api_key)

    def call(self, model: str, system_prompt: str, messages: List[Dict[str, str]], 
            temperature: float, max_tokens: int) -> str:
        # Anthropic specific: Ensure first message is from 'user'
        filtered_msgs = [m for m in messages if m["role"] in ("user", "assistant")]
        while filtered_msgs and filtered_msgs[0]["role"] != "user":
            filtered_msgs.pop(0)

        if not filtered_msgs:
            filtered_msgs = [{"role": "user", "content": "(Please continue.)"}]

        response = self.client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=filtered_msgs,
            temperature=min(float(temperature), 1.0),
        )
        return response.content[0].text