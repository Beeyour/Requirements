import os
from typing import List, Dict
from openai import AsyncOpenAI
from backend.services.llm.base_adapter import BaseLLMAdapter

class OpenAIAdapter(BaseLLMAdapter):
    def __init__(self):
        # Initialize the OpenAI client by fetching the API key from environment variables
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            # Raise an error if the key is missing to avoid failed API calls at runtime
            raise RuntimeError("OPENAI_API_KEY environment variable is not set")
        
        # Change: Using AsyncOpenAI to maintain compatibility with the upper layers
        self.client = AsyncOpenAI(api_key=self.api_key)

    async def call(self, model: str, system_prompt: str, messages: List[Dict[str, str]], 
            temperature: float, max_tokens: int) -> str:
        
        # Merge the system prompt with the conversation history
        full_messages = [{"role": "system", "content": system_prompt}] + list(messages)

        # Change: Use 'await' for the async chat completion request
        response = await self.client.chat.completions.create(
            model=model,
            messages=full_messages,
            temperature=temperature,
            # Utilizing max_completion_tokens as per the 2026 SDK standards
            max_completion_tokens=max_tokens,
        )
        
        # Safely return the content or an empty string if it's missing
        return response.choices[0].message.content or ""