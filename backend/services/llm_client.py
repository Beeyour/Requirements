import os
import re
import json
from typing import List, Dict, Any

# ---------------------------------------------------------------------------
# Registry of supported providers and models
# ---------------------------------------------------------------------------

AVAILABLE_MODELS: Dict[str, Dict[str, str]] = {
    "openai": {
        "gpt-4o":           "gpt-5.4-nano",
        "gpt-4o-mini":      "gpt-5.4-nano",
        "gpt-5.4-nano":      "gpt-5.4-nano",
        "gpt-5.4-mini":    "gpt-5.4-nano",
    },
    # "anthropic": {
    #     "claude-opus-4-5":              "Claude Opus 4.5",
    #     "claude-sonnet-4-5":            "Claude Sonnet 4.5",
    #     "claude-3-5-sonnet-20241022":   "Claude 3.5 Sonnet",
    #     "claude-haiku-4-5":      "claude-haiku-4-5",
    # },
    # "google": {
    #     "gemini-3.1-flash-lite-preview":  "Gemini 3.1 Flash Lite",  # by omar
    #     "gemini-3-flash":    "Gemini 3 Flash",
    #     "gemini-2.5-flash":  "Gemini 2.5 Flash",
    # },
}


DEFAULT_PROVIDER = "google"  # by omar
DEFAULT_MODEL    = "gemini-3.1-flash"   # by omar
DEFAULT_PROVIDER = "openai"
DEFAULT_MODEL    = "gpt-5.4-nano"

PROVIDER_LABELS = {
    "openai":    "OpenAI",
    "anthropic": "Anthropic",
    "google":    "Google",
}


def validate_model(provider: str, model: str) -> None:
    if provider not in AVAILABLE_MODELS:
        raise ValueError(f"Unknown provider '{provider}'")
    if model not in AVAILABLE_MODELS[provider]:
        raise ValueError(f"Unknown model '{model}' for provider '{provider}'")


# ---------------------------------------------------------------------------
# Unified call entry-point
# ---------------------------------------------------------------------------

def call_llm(
    provider: str,
    model: str,
    system_prompt: str,
    messages: List[Dict[str, str]],
    temperature: float = 0.7,
    max_tokens: int = 500,
) -> str:
    if provider == "openai":
        return _call_openai(model, system_prompt, messages, temperature, max_tokens)
    elif provider == "anthropic":
        return _call_anthropic(model, system_prompt, messages, temperature, max_tokens)
    elif provider == "google":
        return _call_google(model, system_prompt, messages, temperature, max_tokens)
    else:
        raise ValueError(f"Unsupported provider: '{provider}'")


def parse_json_response(text: str) -> Any:
    """Strip optional markdown fences then parse JSON."""
    cleaned = re.sub(r"^```(?:json)?\s*", "", text.strip(), flags=re.MULTILINE)
    cleaned = re.sub(r"\s*```$", "",  cleaned.strip(), flags=re.MULTILINE)
    return json.loads(cleaned.strip())


# ---------------------------------------------------------------------------
# Provider implementations
# ---------------------------------------------------------------------------

def _call_openai(model, system_prompt, messages, temperature, max_tokens) -> str:
    from openai import OpenAI
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")
    client = OpenAI(api_key=api_key)
    full = [{"role": "system", "content": system_prompt}] + list(messages)
    resp = client.chat.completions.create(
        model=model,
        messages=full,
        temperature=temperature,
        max_completion_tokens=max_tokens,
    )
    return resp.choices[0].message.content or ""


def _call_anthropic(model, system_prompt, messages, temperature, max_tokens) -> str:
    import anthropic
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY is not set")
    client = anthropic.Anthropic(api_key=api_key)

    # Anthropic requires the first message to be from "user"
    msgs = [m for m in messages if m["role"] in ("user", "assistant")]
    while msgs and msgs[0]["role"] != "user":
        msgs.pop(0)
    if not msgs:
        msgs = [{"role": "user", "content": "(Please continue.)"}]

    resp = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=msgs,
        temperature=min(float(temperature), 1.0),
    )
    return resp.content[0].text


def _call_google(model, system_prompt, messages, temperature, max_tokens) -> str:
    import google.generativeai as genai
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY is not set")
    genai.configure(api_key=api_key)

    gen_model = genai.GenerativeModel(
        model_name=model,
        system_instruction=system_prompt,
    )
    gen_cfg = genai.types.GenerationConfig(
        temperature=float(temperature),
        max_output_tokens=max_tokens,
    )

    msgs = list(messages)
    if not msgs:
        return gen_model.generate_content("(Please continue.)", generation_config=gen_cfg).text

    # Build chat history from all messages except the last (which is sent via send_message)
    history = [
        {"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]}
        for m in msgs[:-1]
    ]
    chat = gen_model.start_chat(history=history)
    last_content = msgs[-1]["content"] if msgs[-1]["role"] == "user" else "(Please continue.)"
    return chat.send_message(last_content, generation_config=gen_cfg).text
