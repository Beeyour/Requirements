
# This file remains as the entry point to avoid changing imports in other services.

from services.llm.llm_factory import LLMFactory
from services.llm.utils import parse_json_response # We move the helper here

def call_llm(provider, model, system_prompt, messages, temperature=0.7, max_tokens=500):
    """
    Main entry point used by ai_agent.py and chat_service.py.
    It routes the call to the new clean architecture.
    """
    adapter = LLMFactory.get_adapter(provider)
    return adapter.call(
        model=model,
        system_prompt=system_prompt,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens
    )