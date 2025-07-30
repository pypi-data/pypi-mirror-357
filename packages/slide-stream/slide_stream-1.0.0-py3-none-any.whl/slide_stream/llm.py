"""LLM integration for Slide Stream."""

import os
from typing import Any

from rich.console import Console

err_console = Console(stderr=True, style="bold red")


def get_llm_client(provider: str) -> Any:
    """Get LLM client based on provider."""
    if provider == "gemini":
        try:
            import google.generativeai as genai

            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY environment variable not set.")
            genai.configure(api_key=api_key)
            return genai.GenerativeModel("gemini-1.5-flash")
        except ImportError:
            raise ImportError(
                "Gemini library not found. Please install with: pip install slide-stream[gemini]"
            )

    elif provider == "openai":
        try:
            from openai import OpenAI

            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable not set.")
            return OpenAI(api_key=api_key)
        except ImportError:
            raise ImportError(
                "OpenAI library not found. Please install with: pip install slide-stream[openai]"
            )

    elif provider == "claude":
        try:
            import anthropic

            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY environment variable not set.")
            return anthropic.Anthropic(api_key=api_key)
        except ImportError:
            raise ImportError(
                "Anthropic library not found. Please install with: pip install slide-stream[claude]"
            )

    elif provider == "groq":
        try:
            from groq import Groq

            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError("GROQ_API_KEY environment variable not set.")
            return Groq(api_key=api_key)
        except ImportError:
            raise ImportError(
                "Groq library not found. Please install with: pip install slide-stream[groq]"
            )

    elif provider == "ollama":
        try:
            from openai import OpenAI

            base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            return OpenAI(base_url=f"{base_url}/v1", api_key="ollama")
        except ImportError:
            raise ImportError(
                "OpenAI library not found. Please install with: pip install slide-stream[openai]"
            )

    else:
        raise ValueError(f"Unknown LLM provider: {provider}")


def query_llm(
    client: Any, provider: str, prompt_text: str, rich_console: Console
) -> str | None:
    """Query LLM with given prompt."""
    rich_console.print("  - Querying LLM...")

    try:
        if provider == "gemini":
            response = client.generate_content(prompt_text)
            return response.text

        elif provider in ["openai", "ollama"]:
            model = "gpt-4o" if provider == "openai" else "llama3.1"
            response = client.chat.completions.create(
                model=model, messages=[{"role": "user", "content": prompt_text}]
            )
            return response.choices[0].message.content

        elif provider == "claude":
            response = client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt_text}],
            )
            return response.content[0].text

        elif provider == "groq":
            response = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[{"role": "user", "content": prompt_text}],
            )
            return response.choices[0].message.content

        return None

    except Exception as e:
        err_console.print(f"  - LLM Error: {e}")
        return None
