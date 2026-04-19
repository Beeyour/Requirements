from .openai_adapter import OpenAIAdapter
from .google_adapter import GoogleAdapter
from .anthropic_adapter import AnthropicAdapter

class LLMFactory:
    """
    Registry and factory for LLM adapters.
    """
    _adapters = {
        "openai": OpenAIAdapter,
        "google": GoogleAdapter,
        "anthropic": AnthropicAdapter,
    }

    @staticmethod
    def get_adapter(provider: str):
        adapter_class = LLMFactory._adapters.get(provider.lower())
        if not adapter_class:
            raise ValueError(f"Provider '{provider}' is not supported.")
        return adapter_class()

def call_llm(provider, model, system_prompt, messages, temperature=0.7, max_tokens=500):
    """
    Global entry point to call any LLM provider.
    """
    adapter = LLMFactory.get_adapter(provider)
    return adapter.call(model, system_prompt, messages, temperature, max_tokens)