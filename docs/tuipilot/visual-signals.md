Visual signals & statuses

Goal

Define a small, consistent set of visual tokens and micro-animations to communicate system state clearly.

Statuses

- idle: no activity (token: "idle", color: #6B7280 - gray)
- streaming: LLM streaming tokens (token: "streaming", color: #0EA5A4 - teal) + spinner
- success: completed action (token: "success", color: #16A34A - green)
- error: failure (token: "error", color: #DC2626 - red)
- syncing: background sync (token: "sync", color: #2563EB - blue)
- pending: awaiting user input/confirmation (token: "pending", color: #F59E0B - amber)

Micro-animations

- Spinner: single-character spinner cycle "|/-\\" at 100ms per frame for streaming.
- Pulse: subtle color fade (200ms) used for success confirmation.

Guidelines

- Keep animations short; avoid distracting the developer flow.
- Use color tokens consistently across status bar, toast, and assistant headers.
- Provide textual status fallback for terminals without color support.

Example status bar layout

[branch] [file: line:col] • [token: streaming] • LLM: streaming…

Design note: map these signals to accessible text and tooltips so screen readers can convey state.

Docs & todo links

- This file is the canonical source for visual tokens. Maps to todo ID: visual-signals-doc.
- Implementations should reference these tokens and provide a textual fallback for accessibility.

ASCII spinner example (use for headless tests)

- Frames: ["|", "/", "-", "\\"]
- Use 100ms per frame for a smooth but unobtrusive effect.