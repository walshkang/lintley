Agents

Purpose

Define background agents and their responsibilities. Agents are small, single-purpose asyncio tasks or subprocesses that perform long-running or blocking work so the TUI remains responsive.

Suggested agents

- llm-agent: Manages streaming requests to the LLM backend, handles retries, backpressure, and token-level streaming events.
- patch-agent: Receives candidate patches from assistant responses, computes diffs, validates, and prepares apply/revert actions.
- filewatch-agent: Watches repo files for external changes and notifies the UI for buffer invalidation or merge prompts.
- git-agent: Executes git operations (branch, commit, revert) behind a confirmation UI; isolates potentially destructive actions.

Interfaces

- Use an in-process event bus (asyncio.Queue) or simple message broker (sqlite event table) for communication.
- Agents expose status, progress, and error channels consumed by the UI.

LLM agent interface (recommended minimal API)

The llm-agent should implement a small, testable interface used by UI and other agents:

- stream(prompt: str, metadata: dict) -> AsyncIterator[str]
  Streams token strings. Metadata may include model selection, temperature, and request id.

- cancel(stream_id: str) -> bool
  Requests cancellation of an in-flight stream.

- status() -> {state: "idle"|"streaming"|"error", stream_id: Optional[str], progress: Optional[float]}

Event envelope (message bus)

{ "type": "llm.token", "stream_id": "abc123", "token": "def", "meta": {...} }
{ "type": "llm.done",  "stream_id": "abc123", "meta": {...} }
{ "type": "llm.error", "stream_id": "abc123", "error": "timeout" }

Adapters

- Implement adapter classes that conform to the llm-agent interface: MockAdapter, OpenAIAdapter, AnthropicAdapter.
- MockAdapter must support deterministic playback for tests and CI and support error injection and adjustable token delay.

Failure modes & restart

- Agents should surface failures to the UI with human-readable messages and retry options.
- Keep side-effecting operations idempotent where possible; require explicit user confirmation for commits and branch creation.

Security

- Agents that send content to third-party services must respect privacy settings and user approval prompts.
- All adapters must provide an explicit opt-in toggle before sending repo contents. Log only metadata unless user allows content sharing.