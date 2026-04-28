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
    def _supports_json_mode(self, model: str) -> bool:
        """Check if the model supports the json_object response format."""
        # Models known to support response_format={"type": "json_object"}
        supported_prefixes = [
            "gpt-4o", "gpt-4o-mini",
            "gpt-4-turbo", "gpt-4-1106", "gpt-4-0125", "gpt-4-vision",
            "gpt-3.5-turbo-1106", "gpt-3.5-turbo-0125",
            "gpt-5",
        ]
        return any(model.startswith(p) for p in supported_prefixes)
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
            kwargs = {}
            if is_json and self._supports_json_mode(model):
                kwargs["response_format"] = {"type": "json_object"}
                # Ensure the prompt mentions JSON so OpenAI doesn't reject the request
                if system_prompt and "json" not in system_prompt.lower():
                    input_messages[0]["content"] += "\n\nYou MUST respond with valid JSON only."
            elif is_json:
                # Model doesn't support json_object mode — rely on prompt-only JSON instruction
                print(f"[OpenAIAdapter] Model '{model}' does not support JSON mode; using prompt-only JSON instruction")
                input_messages[0]["content"] += (
                    "\n\nCRITICAL: You MUST respond with ONLY valid JSON. "
                    "No markdown, no prose, no explanation — pure JSON inside curly braces."
                )
            if self._is_new_model(model):
                response = await self.client.chat.completions.create(
                    model=model,
                    messages=input_messages,
                    temperature=temperature,
                    extra_body={"max_completion_tokens": max_tokens, **({} if not kwargs else {"response_format": kwargs.get("response_format")})},
                )
                return response.choices[0].message.content
            else:
                response = await self.client.chat.completions.create(
                    model=model,
                    messages=input_messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs,
                )
                return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI API Error: {str(e)}")
            raise RuntimeError(f"Failed to call OpenAI: {str(e)}")