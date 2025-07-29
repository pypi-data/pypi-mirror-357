"""LLM provider abstraction used by the Agent core loop.

For now supports a trivial Echo provider and optionally OpenAI Chat API if
`openai` is installed and `OPENAI_API_KEY` is set.
"""
from __future__ import annotations

import os
from typing import Protocol, runtime_checkable


@runtime_checkable
class LLM(Protocol):
    """Protocol for language model backends."""

    def generate(self, prompt: str) -> str:  # pragma: no cover
        """Return the model text completion for the given prompt."""
        ...


class EchoLLM:
    """Simplest possible provider that just echoes the prompt."""

    def generate(self, prompt: str) -> str:  # noqa: D401
        return f"[ECHO] {prompt}"


class OpenAILLM:  # pragma: no cover — requires network
    """Thin wrapper around the OpenAI chat completion endpoint."""

    def __init__(self, model: str = "gpt-3.5-turbo") -> None:
        try:
            import openai  # type: ignore
        except ModuleNotFoundError:  # pragma: no cover
            raise ImportError("openai package not installed. Run `poetry add openai`. ") from None

        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError("OPENAI_API_KEY environment variable not set.")

        self._openai = openai
        self._model = model

    def generate(self, prompt: str) -> str:  # pragma: no cover
        completion = self._openai.ChatCompletion.create(
            model=self._model,
            messages=[{"role": "user", "content": prompt}],
        )
        # Newer openai>=1.0 might differ; adapt when upgrading.
        return completion.choices[0].message.content


# ---------------- Google Gemini -----------------


class GeminiLLM:  # pragma: no cover
    """Wrapper around Google Generative AI Gemini models."""

    def __init__(self, model: str = "gemini-pro") -> None:
        try:
            import google.generativeai as genai  # type: ignore
        except ModuleNotFoundError:  # pragma: no cover
            raise ImportError(
                "google-generativeai not installed. Run `poetry add google-generativeai`."
            ) from None

        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY environment variable not set.")

        genai.configure(api_key=api_key)
        self._model = genai.GenerativeModel(model)

    def generate(self, prompt: str) -> str:  # noqa: D401
        response = self._model.generate_content(prompt)
        # Newer client returns text in .text
        return response.text  # type: ignore[attr-defined]


_DEF_PROVIDER = "echo"  # default provider if nothing specified

_PROVIDERS: dict[str, type[LLM]] = {
    "openai": OpenAILLM,
    "gemini": GeminiLLM,
    "echo": EchoLLM,
}


def get_default_llm() -> LLM:
    """Return an LLM instance based on env vars.

    Priority order:
    1. `MINI_AGENT_LLM` env var ("openai" or "echo").
    2. If `OPENAI_API_KEY` is set → "openai".
    3. If `GEMINI_API_KEY` or `GOOGLE_API_KEY` is set → "gemini".
    4. Fallback to "echo".
    """

    provider = os.getenv("MINI_AGENT_LLM")

    if not provider:
        if os.getenv("OPENAI_API_KEY"):
            provider = "openai"
        elif os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"):
            provider = "gemini"
        else:
            provider = _DEF_PROVIDER

    cls = _PROVIDERS.get(provider, EchoLLM)
    return cls() 