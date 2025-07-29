"""Dynamic tool registry.

Tools are defined by YAML spec files and backed by Python callables.
Each tool spec looks like:

```yaml
name: echo
description: Echo the user input
python: mini_agent_harness.tools.echo:echo_tool
```

At runtime we import the callable and expose it via `load_tools`.
"""
from __future__ import annotations

import importlib
import inspect
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, Iterable, List

import yaml  # type: ignore


@dataclass
class ToolSpec:
    name: str
    description: str
    python: str  # module:path e.g. path.to.mod:function_name
    func: Callable | None = None  # populated after import

    def import_func(self) -> Callable:
        if self.func is not None:
            return self.func
        module_path, _, attr = self.python.partition(":")
        if not module_path or not attr:
            raise ValueError(f"Invalid python path in tool spec: {self.python}")
        module = importlib.import_module(module_path)
        func: Callable = getattr(module, attr)
        if not callable(func):
            raise TypeError(f"Tool target {self.python} is not callable")
        # Basic signature check: first param should be str or none
        sig = inspect.signature(func)
        if len(sig.parameters) == 0:
            raise TypeError("Tool callable must accept at least one argument (input string)")
        self.func = func
        return func


def _load_tool_yaml(path: Path) -> ToolSpec:
    data = yaml.safe_load(path.read_text())
    return ToolSpec(**data)


def discover_tools(tool_paths: Iterable[str | Path]) -> Dict[str, ToolSpec]:
    """Load multiple tool YAMLs into a registry keyed by tool name."""
    registry: Dict[str, ToolSpec] = {}
    for p in tool_paths:
        spec = _load_tool_yaml(Path(p))
        if spec.name in registry:
            raise ValueError(f"Duplicate tool name {spec.name}")
        registry[spec.name] = spec
    return registry


def load_tools_from_manifest(manifest: dict) -> Dict[str, Callable]:
    """Given the agent manifest dict, import and return callable tools."""
    tools_field: List[str] = manifest.get("tools", [])
    registry = discover_tools(tools_field)
    return {name: spec.import_func() for name, spec in registry.items()}


__all__ = [
    "ToolSpec",
    "discover_tools",
    "load_tools_from_manifest",
] 