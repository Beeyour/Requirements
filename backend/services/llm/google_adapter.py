import os
from typing import List, Dict
import google.generativeai as genai
from backend.services.llm.base_adapter import BaseLLMAdapter

class GoogleAdapter(BaseLLMAdapter):
    def __init__(self):
        # Initialize Google Generative AI with the API key from environment variables
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            # Raise an error if the key is missing to prevent invalid API calls
            raise RuntimeError("GOOGLE_API_KEY environment variable is not set")
        genai.configure(api_key=self.api_key)

    async def call(self, model: str, system_prompt: str, messages: List[Dict[str, str]], 
            temperature: float, max_tokens: int, is_json: bool) -> str:
        # Initialize the generative model with system instructions
        gen_model = genai.GenerativeModel(
            model_name=model,
            system_instruction=system_prompt,
        )
        # Gemini requires roles to be 'user' or 'model' (not 'assistant')
        history = []
        for msg in messages[:-1]:
            role = "user" if msg["role"] == "user" else "model"
            history.append({"role": role, "parts": [msg["content"]]})
        # Start a chat session with the converted history
        chat = gen_model.start_chat(history=history)
        # Configure generation parameters
        config_kwargs = {
            "max_output_tokens": max_tokens,
            "temperature": temperature,
        }
        if is_json:
            config_kwargs["response_mime_type"] = "application/json"
        config = genai.types.GenerationConfig(**config_kwargs)
        # Change: Use 'send_message_async' and 'await' to match the layer requirements
        response = await chat.send_message_async(
            messages[-1]["content"], 
            generation_config=config
        )
        return response.text