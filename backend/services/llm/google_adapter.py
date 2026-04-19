import os
import google.generativeai as genai
from .base_adapter import BaseLLMAdapter

class GoogleAdapter(BaseLLMAdapter):
    """
    Adapter for Google Gemini API.
    """
    def call(self, model, system_prompt, messages, temperature, max_tokens) -> str:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError("GOOGLE_API_KEY is not set")
        
        genai.configure(api_key=api_key)
        gen_model = genai.GenerativeModel(
            model_name=model,
            system_instruction=system_prompt,
        )
        # ... (Rest of your specific google logic)
        return "Result from Google"