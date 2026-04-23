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

        for msg in messages:
            input_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
                # reasoning={ "effort": "high" }
        response_format = {"type": "json_object"} if is_json else None

        try:

            response = await self.client.chat.completions.create(

                model=model,
                messages=input_messages, # المسمى الصحيح هو messages وليس input
                temperature=temperature,
                max_output_tokens=max_tokens,    # المسمى الصحيح هو max_tokens وليس max_output_tokens
                response_format=response_format
            )

            return response.choices[0].message.content

        except Exception as e:
            print(f"OpenAI API Error: {str(e)}")
            raise RuntimeError(f"Failed to call OpenAI: {str(e)}")

        #     if hasattr(response, "output_text"):
        #         return response.output_text
        #     texts = []
        #     for item in response.output:
        #         for content in getattr(item, "content", []):
        #             if hasattr(content, "text"):
        #                 texts.append(content.text)

        #     return "".join(texts)

        # except Exception as e:
        #     print(f"OpenAI API Error: {str(e)}")
        #     raise RuntimeError(f"Failed to call OpenAI: {str(e)}")