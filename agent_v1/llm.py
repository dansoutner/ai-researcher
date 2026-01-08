import os
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

def get_llm():
    """
    Choose provider via env:
      LLM_PROVIDER=openai|anthropic
    And set provider keys as usual:
      OPENAI_API_KEY=...
      ANTHROPIC_API_KEY=...

    You can also swap this to any LangChain-compatible chat model.
    """
    provider = os.getenv("LLM_PROVIDER").lower()
    model = os.getenv("LLM_MODEL")  # example default
    temperature = float(os.getenv("LLM_TEMPERATURE", 0))
    if not model:
        raise ValueError("LLM_MODEL is required.")
    if not provider:
        raise ValueError("LLM_PROVIDER is required.")

    if provider == "anthropic":
        ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
        return ChatAnthropic(model=model, temperature=temperature, api_key=ANTHROPIC_API_KEY)
    if provider == "openai":
        return ChatOpenAI(model=model, temperature=temperature)

    raise ValueError(f"Unsupported LLM_PROVIDER={provider!r}")
