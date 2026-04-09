Design

Overview

Keyboard-first TUI with three primary panes:
- Sidebar (left): file tree + fuzzy filter
- Editor (center): editable buffer with basic syntax highlighting
- Assistant (right/bottom): chat stream with token-level updates and actions (apply patch, request refactor)

Components

- Command palette: Ctrl-P to open fuzzy finder for files/commands.
- Status bar: shows branch, file, LLM status, and visual signal token.
- Modal dialogs: confirm apply patch, create branch, credential prompts.

Keybindings (suggested)

- Ctrl-P: command palette
- Ctrl-O: open file
- Ctrl-S: save buffer
- Ctrl-Enter: send selection or buffer to assistant
- Alt-.: accept inline suggestion (future)
- Esc: close modal/palette

Streaming UX

- Assistant pane should display tokens as they stream, with minor animation and a trailing spinner while streaming.
- Allow aborting a stream with Esc or Ctrl-C.

Acceptance criteria (tie to todos)

- tui-core: `python -m lintley.tui` launches UI with three panes and a status bar; chat pane can receive programmatic text.
- editor-file-tree: file tree lists repo files and opens/saves buffers.
- llm-integration: mock adapter streams tokens into chat pane and supports cancel.

Quickstart

- Development quickstart: python -m lintley.tui  # requires Python 3.11+, Textual installed
- Tests: pytest --maxfail=1

Theming & Accessibility

- Provide light/dark themes; use high-contrast colors for important signals.
- Ensure all actions accessible via keyboard; support basic screen-reader hints via textual label semantics.

Persistence

- Session history persisted to ~/.local/share/lintley/sessions/ by default.
- Per-repo settings may live in .lintley/ (opt-in).

Docs references

- See docs/tuipilot for mapping between todos and docs. Primary todo IDs: tui-core, editor-file-tree, llm-integration, command-palette, git-apply-patches, visual-signals-doc, context-doc, agents-doc, design-doc, docs-collection, tests-ci.