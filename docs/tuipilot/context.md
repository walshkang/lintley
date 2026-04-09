Context

Purpose

Lintley is evolving into a keyboard-first streaming TUI assistant for code (Copilot/Claude-like). The goal: fast, low-latency developer workflows (suggestions, patches, code navigation) with strong UX and safety controls.

Scope

- Desktop TUI (terminal) using Python Textual + Rich.
- Local repo-aware features (open, edit, apply patches) and optional remote LLM backends.
- Start small: shipping a happy-path streaming assistant and patch apply flow.

Privacy & Secrets

- Do NOT commit API keys. Use environment variables or a local config file with restricted permissions.
- Recommended env vars: LINTLEY_OPENAI_KEY, LINTLEY_ANTHROPIC_KEY, LINTLEY_BACKEND (mock|openai|anthropic).
- Local config: if using a config file prefer ~/.config/lintley/config.json with permissions 600; do not commit this file.
- Store session history in ~/.local/share/lintley or repo .lintley/ (opt-in and opt-out per repo).
- Any feature that sends repo content to third-party services must require an explicit per-request confirmation.

Operational notes

- Mock streaming backend used for local dev and CI tests.
- Long-running agents run as subprocesses or asyncio tasks with restart policies.
- Telemetry is opt-in; avoid sending repo content unless explicitly approved.

Where we track next work

- Primary task tracker: session todos in the Copilot CLI session DB (todo IDs listed in plan.md).
- Canonical docs that map to todo IDs: docs/tuipilot/context.md, agents.md, design.md, visual-signals.md.
- Quick mapping (see plan.md): tui-core, editor-file-tree, llm-integration, command-palette, git-apply-patches, visual-signals-doc, context-doc, agents-doc, design-doc, docs-collection, tests-ci.

Contributors

- Follow docs in docs/tuipilot for design, agents, and visual signals.
- Open issues for UX trade-offs; prefer small, vertical slices.
- When in doubt about privacy or secrets, open an issue and do not proceed with sending repo content.