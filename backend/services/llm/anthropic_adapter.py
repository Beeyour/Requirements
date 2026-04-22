import os
from typing import List, Dict
import anthropic
from backend.services.llm.base_adapter import BaseLLMAdapter

class AnthropicAdapter(BaseLLMAdapter):
    def __init__(self):
        # Initialize Anthropic client using environment variables
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise RuntimeError("ANTHROPIC_API_KEY environment variable is not set")
        
        # Change to AsyncAnthropic to match the Agent layer's 'await' calls
        self.client = anthropic.AsyncAnthropic(api_key=self.api_key)

    async def call(self, model: str, system_prompt: str, messages: List[Dict[str, str]], 
            temperature: float, max_tokens: int, is_json: bool) -> str:
        
        # Filter messages to include only 'user' and 'assistant' roles
        filtered_msgs = [m for m in messages if m["role"] in ("user", "assistant")]
        
        # Ensure the conversation starts with a 'user' message as required by Anthropic
        while filtered_msgs and filtered_msgs[0]["role"] != "user":
            filtered_msgs.pop(0)

        if not filtered_msgs:
            filtered_msgs = [{"role": "user", "content": "Begin analysis."}]

        # Using 'await' because the client is now async
        response = await self.client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=filtered_msgs,
            # Anthropic temperature range is 0.0 to 1.0
            temperature=min(float(temperature), 1.0),
        )
        
        return response.content[0].text