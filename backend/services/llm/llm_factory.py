from backend.services.llm.openai_adapter import OpenAIAdapter
from backend.services.llm.google_adapter import GoogleAdapter
from backend.services.llm.anthropic_adapter import AnthropicAdapter

class LLMFactory:
    # Maps provider strings to their respective adapter classes for dynamic instantiation
    _adapters = {
        "openai": OpenAIAdapter,
        "google": GoogleAdapter,
        "anthropic": AnthropicAdapter,
    }

    @staticmethod
    def get_adapter(provider: str):
        # Retrieves the appropriate adapter class based on the provider name
        adapter_class = LLMFactory._adapters.get(provider.lower())
        if not adapter_class:
            # Raise an error to prevent execution with an unsupported provider
            raise ValueError(f"Provider '{provider}' is not supported.")
        
        # Returns a fresh instance of the requested adapter
        return adapter_class()

async def call_llm(provider: str, model: str, system_prompt: str, messages: list, temperature=0.7, max_tokens=500):
    # Change: Made this function 'async' and added 'await'
    # This ensures compatibility between the Async Adapters and the Async Agents
    adapter = LLMFactory.get_adapter(provider)
    return await adapter.call(model, system_prompt, messages, temperature, max_tokens)