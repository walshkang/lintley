Contributing to Lintley

Thanks for your interest! This document explains how to contribute so maintainers can review and accept your work quickly.

Getting started

1. Fork the repo and create a topic branch: `git checkout -b feat/short-description`
2. Run locally: `python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt` (if requirements exist)
3. Run tests: `pytest` (project aims to provide tests for core agents)

Commit & PR guidelines

- Use clear commit messages. Keep subject line <= 72 chars.
- Include the required Co-authored-by trailer for automated commits when applicable:
  Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
- Open a PR against main; link related issues and describe rationale

Code style & tests

- Use idiomatic Python 3.11+. Prefer explicit typing where helpful.
- Add unit tests for new behavior. Use MockAdapter for deterministic LLM behavior.
- Run linters/formatters: `ruff . && black .`

Design & API changes

- For public interface changes (ProviderClient, llm-agent API), include a short design note in PR description and update docs/ accordingly.

Security & privacy

- Any change that sends repo content to an external API must include an explicit opt-in toggle in the CLI and documented rationale.

Thanks — small, clear PRs are easiest to review.