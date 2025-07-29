"""FastAPI server exposing chat endpoint with simple streaming.

Run via `mini-agent serve` (see CLI). This is an early skeleton: it
instantiates an Agent for each request using the quickstart manifest and
streams back text tokens separated by spaces.
"""
from __future__ import annotations

from pathlib import Path
from typing import AsyncGenerator, Iterator

import yaml # type: ignore
from fastapi import FastAPI, Form # type: ignore
from fastapi.responses import StreamingResponse # type: ignore

from .core import Agent

app = FastAPI(title="MiniAgentHarness")

_MANIFEST_PATH = Path("agents/quickstart.yaml")


def _get_agent() -> Agent:
    manifest = yaml.safe_load(_MANIFEST_PATH.read_text())
    return Agent(manifest)


def _stream_text(text: str) -> Iterator[bytes]:
    for token in text.split():
        yield f"data: {token}\n\n".encode()


@app.get("/")
async def root() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/chat")
async def chat(message: str = Form(...)):  # noqa: D401
    agent = _get_agent()
    result = agent.run(message)
    return StreamingResponse(
        _stream_text(result.response_text),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache"},
    ) 