"""Real model adapters. This module needs the `providers` extra and API keys."""

import os

from langchain_core.language_models.chat_models import BaseChatModel


def build_model(provider: str) -> BaseChatModel:
    if provider == "deepseek":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            api_key=os.environ["DEEPSEEK_API"],
            base_url=os.getenv("BASE_URL", "https://api.deepseek.com"),
            model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
            max_tokens=int(os.getenv("MAX_OUTPUT_TOKENS", "4096")),
        )

    if provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(
            google_api_key=os.environ["GEMINI_API_KEY"],
            model=os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash"),
        )

    raise ValueError(f"Unsupported provider: {provider}")
