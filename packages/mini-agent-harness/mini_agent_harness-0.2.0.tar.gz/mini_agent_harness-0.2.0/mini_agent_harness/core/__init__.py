"""Core components of Mini Agent Harness.

For now this only exposes a stub Agent that simply echoes the input. The
real implementation will follow a proper tool-calling loop.
"""
from __future__ import annotations

from dataclasses import dataclass

from .llm import get_default_llm, LLM
from ..tools import load_tools_from_manifest
from .loop import ReActLoop


@dataclass
class AgentResult:
    """Simple result wrapper mimicking an LLM agent response."""

    response_text: str

    # TODO: include metadata such as traces, tool calls, etc.


class Agent:
    """Extremely naive stub agent.

    Parameters
    ----------
    manifest : dict
        Parsed YAML manifest for the agent.
    """

    def __init__(self, manifest: dict, llm: LLM | None = None):
        self.manifest = manifest
        self.llm: LLM = llm or get_default_llm()
        self.tools = load_tools_from_manifest(manifest)

    def run(self, input_text: str) -> AgentResult:
        """Execute the agent for a single user prompt.

        For now this just forwards the prompt to the selected LLM provider.
        Once tool-calling logic lands, this method will orchestrate reasoning
        and tool execution steps.
        """

        if self.manifest.get("mode") == "react":
            loop = ReActLoop(self.llm, self.tools)
            return AgentResult(response_text=loop.run(input_text))

        # Simple prefix tool call mode
        if ":" in input_text:
            tool_name, _, arg = input_text.partition(":")
            tool_name = tool_name.strip()
            if tool_name in self.tools:
                result = self.tools[tool_name](arg.strip())
                return AgentResult(response_text=str(result))

        output = self.llm.generate(input_text)
        return AgentResult(response_text=output) 