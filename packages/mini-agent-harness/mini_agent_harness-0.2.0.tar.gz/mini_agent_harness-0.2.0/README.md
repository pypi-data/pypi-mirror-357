<p align="center">
  <img src="https://img.shields.io/pypi/v/mini-agent-harness?logo=pypi" alt="PyPI">
  <img src="https://img.shields.io/npm/v/mini-agent-harness?logo=npm" alt="NPM">
  <img src="https://github.com/HalukProductions/MiniAgentHarness/actions/workflows/ci.yml/badge.svg" alt="Build Status">
</p>

# MiniAgentHarness

> ⚡️ Small, **test-first** AI-agent starter kit with one-click deploy.

MiniAgentHarness gives you a production-ready scaffold for building ReAct-style language-model agents **with a built-in Pytest harness** so you catch prompt regressions _before_ they reach prod. Spin it up locally, run `pytest`, and deploy to Vercel in minutes.

## Features

- 🧪 **Testing harness** — Pytest plugin, DeepEval metrics, LangSmith replays (coming soon)
- 🚀 **Zero-config deploy** — FastAPI backend + React chat, ready for Vercel Edge / CF Workers
- 🧩 **Tool registry** — YAML → auto-imported Python stubs (generate via CLI)
- 📦 **Batteries included** — CLI, CI workflow, linting hooks, example agents & tests

## Quickstart

```bash
# 1. Install (Poetry recommended)
pipx install poetry  # if you don't already have it
git clone https://github.com/HalukProductions/MiniAgentHarness.git && cd MiniAgentHarness
poetry install

# 2. Run unit tests (stub passes green)
poetry run pytest -q

# 3. Generate an example agent
poetry run mini-agent init  # creates agents/quickstart.yaml

# 4. (Soon) Serve with your favourite model
poetry run mini-agent serve --model ollama/llama3
```

## CLI

| Command            | Description                                |
| ------------------ | ------------------------------------------ |
| `mini-agent init`  | Generate a stub agent YAML & tool skeleton |
| `mini-agent test`  | Run Pytest suite (wrapper)                 |
| `mini-agent serve` | Start FastAPI + React UI (TBA)             |

## Contributing

PRs welcome! Check `TASKS.md` for the active roadmap. For local development:

```bash
poetry install --with dev
pre-commit install
```

## License

MIT © Haluk Sonmezler
