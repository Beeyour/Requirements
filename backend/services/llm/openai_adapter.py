import os
from typing import List, Dict
from openai import AsyncOpenAI
from backend.services.llm.base_adapter import BaseLLMAdapter


class OpenAIAdapter(BaseLLMAdapter):
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY environment variable is not set")

        self.client = AsyncOpenAI(api_key=self.api_key)

    def _is_new_model(self, model: str) -> bool:
        return any(x in model for x in ["gpt-4", "gpt-5", "o"])

    async def call(
        self,
        model: str,
        system_prompt: str,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
        is_json: bool
    ) -> str:

        input_messages = []

        if system_prompt:
            input_messages.append({
                "role": "system",
                "content": system_prompt
            })

        input_messages.extend(messages)

        try:

            if self._is_new_model(model):

                response = await self.client.chat.completions.create(
                    model=model,
                    messages=input_messages,          # <-- 1. تم تعديل input إلى messages
                    temperature=temperature,
                    max_completion_tokens=max_tokens, # <-- 2. تم تعديل max_output_tokens 
                    # response_format={"type": "json_object"} if is_json else None
                )

                if hasattr(response, "output_text"):
                    return response.output_text

                texts = []
                for item in response.output:
                    for content in getattr(item, "content", []):
                        if hasattr(content, "text"):
                            texts.append(content.text)

                return "".join(texts)
            else:

                response = await self.client.chat.completions.create(
                    model=model,
                    messages=input_messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    # response_format={"type": "json_object"} if is_json else None
                )

                return response.choices[0].message.content

        except Exception as e:
            print(f"OpenAI API Error: {str(e)}")
            raise RuntimeError(f"Failed to call OpenAI: {str(e)}")