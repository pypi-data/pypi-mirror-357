"""Minimal ReAct-style reasoning loop.

This is *not* a full implementation – it is intentionally lightweight so that
unit tests can stub the LLM responses. The protocol is:

1. Build a transcript containing a list of tools and the user input.
2. Ask the LLM for a response.
3. If the response starts with `ACTION:` and `ARG:` we call that tool,
   append an `OBSERVATION:` line, and loop.
4. If the response starts with `FINAL:` we stop and return the remaining text.
5. After `max_iters` fall back to returning the last model output.
"""
from __future__ import annotations

from typing import Callable, Dict

from .llm import LLM


class ReActLoop:
    """Lightweight ReAct executor."""

    def __init__(self, llm: LLM, tools: Dict[str, Callable], max_iters: int = 3):
        self.llm = llm
        self.tools = tools
        self.max_iters = max_iters

    def run(self, user_input: str) -> str:
        transcript = [f"Tools: {', '.join(self.tools)}", f"User: {user_input}"]

        for _ in range(self.max_iters):
            prompt = "\n".join(transcript + ["Assistant:"])
            model_response = self.llm.generate(prompt)

            if model_response.startswith("FINAL:"):
                return model_response[len("FINAL:") :].strip()

            if model_response.startswith("ACTION:"):
                # Parse lines
                lines = model_response.splitlines()
                try:
                    action = lines[0].split(":", 1)[1].strip()
                    arg_line = next(l for l in lines[1:] if l.startswith("ARG:"))
                    arg = arg_line.split(":", 1)[1].strip()
                except Exception:  # pragma: no cover
                    # If parsing fails, treat whole response as final.
                    return model_response

                if action not in self.tools:
                    observation = f"ERROR: unknown tool {action}"
                else:
                    try:
                        observation = str(self.tools[action](arg))
                    except Exception as exc:  # pragma: no cover
                        observation = f"ERROR: tool raised {exc}"

                transcript.extend([model_response, f"OBSERVATION: {observation}"])
                continue

            # Fallback: treat model response as final answer
            return model_response.strip()

        # Reached iteration cap
        return "ERROR: max iterations reached" 