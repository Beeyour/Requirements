import os
from typing import List, Dict
from openai import AsyncOpenAI
# Using absolute import for container-to-container reliability
from backend.services.llm.base_adapter import BaseLLMAdapter

class OpenAIAdapter(BaseLLMAdapter):
    def __init__(self):
        """
        Initialize the OpenAI client. 
        Fetches the key from the environment which must be set in the .env file.
        """
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            # Crucial: This ensures the server crashes early if the key is missing
            raise RuntimeError("OPENAI_API_KEY environment variable is not set")

        # AsyncOpenAI is used to prevent blocking the main FastAPI event loop
        self.client = AsyncOpenAI(api_key=self.api_key)

    async def call(
        self,
        model: str,
        system_prompt: str,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int
    ) -> str:
        """
        Executes an asynchronous call to OpenAI Chat Completion API.
        """
        # Combine the system instructions with the user message history
        full_messages = [{"role": "system", "content": system_prompt}] + list(messages)

        try:
            # FIX: Reverted 'max_completion_tokens' to 'max_tokens'
            # to maintain compatibility with standard GPT models (GPT-4o, GPT-3.5).
            response = await self.client.chat.completions.create(
                model=model,
                messages=full_messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )



            # Extract and return the string content from the response object
            return response.choices[0].message.content or ""

        except Exception as e:
            # Log the error and raise for the service layer to handle
            print(f"OpenAI API Error: {str(e)}")
            raise RuntimeError(f"Failed to call OpenAI: {str(e)}")