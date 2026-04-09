Product Requirements Document (PRD)

Project: Lintley — Multi-Agent HITL Coordinator

Vision

Make agentic engineering approachable for "vibe coders" and white-collar professionals: a lightweight, human-first framework for managing small swarms of specialized agents (Actor, Observer, operational agents) to automate routine engineering work while keeping humans in the loop.

Target user

- "Vibe coder" / white-collar professional comfortable with CLI and quick automation
- Wants to prototype agentic workflows, delegate routine code & doc tasks, and scale to coordinated teams of agents

Goals

1. Deliver a minimal, reliable local CLI that coordinates Actor → Observer → Human checkpoints for parallel tasks.
2. Provide a clean adapter layer for LLM providers so users can swap providers with config.
3. Ship developer-facing docs (README, PRD, CONTRIBUTING, API docs) so open-source contributors can extend providers, adapters, and UI layers.

Success metrics

- Time-to-first-task (git clone → run) under 10 minutes with clear setup
- At least three provider adapters (Anthropic, OpenAI, Google) documented and runnable
- Test coverage for core agent interfaces (llm-agent, patch-agent, git-agent)

Key features

- Task JSON schema and CLI for submit/execute/approve/reject
- Actor & Observer agent primitives with clear prompts and risk extraction
- Pluggable ProviderClient adapters for different LLMs
- Non-blocking multi-task coordinator and optional single-task interactive mode
- Local state persisted in .hitl_state/ with optional DB migration path

Non-goals (initial)

- Full web dashboard (prototype CLI first)
- Multi-user cloud-hosted orchestration (local-first)

Open-source priorities

- Clear CONTRIBUTING.md, CODE_OF_CONDUCT.md, and issue templates
- Tests & deterministic MockAdapter for CI
- Security: explicit opt-in before sending code to third-party APIs; redact sensitive files by default

Milestones

1. Docs and onboarding: README + PRD + CONTRIBUTING + CODE_OF_CONDUCT
2. Core refactor: pull provider adapters into a clean ProviderClient interface
3. Tests: MockAdapter + adapter tests + integration smoke tests
4. Community: advertise to developer communities, gather contributors

Constraints & Risks

- API costs — put a cost-awareness note in README and provide model_hint defaults
- Provider API breaking changes — keep adapters thin and versioned
- Privacy — default to not sending repository contents without explicit opt-in

Appendix

- Proposed file layout: docs/, examples/, providers/, agents/, hitl_multitask.py, actor_observer_hitl.py
- Contribution checklist: run tests, run formatters (black/ruff), include changelog entry
