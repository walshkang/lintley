Roadmap: Safety & Prompt-Injection Mitigations

This file summarizes the immediate changes implemented and next steps for securing lintley during local BYOK runs.

Immediate (done)
- Added utils/safety.py with:
  - sanitize_user_input(text)
  - redact_secrets(text)
  - validate_agent_output(agent_type, payload)
- Integrated sanitization, redaction, and schema validation into agents_orchestrator:
  - Prompts values are sanitized and brace-escaped before formatting
  - Agent outputs are validated against minimal schemas; failures emit "schema_failure" events
  - Redaction runs on agent string outputs to remove PEM, env-like KEY=VALUE and JWT-like tokens
- Added tests/tests_safety.py verifying sanitization, redaction, and schema validation basics

Short-term (next sprint)
- Expand adversarial corpus and CI job to run injection tests against MockProvider
- Replace naive .format templating with Jinja2 and enable auto-escaping
- Extend schema validation into a shared schema library with JSON Schema and strict enforcement
- Add human-approval gated flow for destructive GitAgent actions

Medium-term
- Implement content allowlist/denylist for files shared with remote models
- Build runtime policy engine and provenance logging (hashes + minimal metadata)
- Add optional local-only enclave mode for local LLM execution

Notes
- Default operation remains mock/local-first. Remote usage requires explicit env opt-in.
- These changes are intentionally conservative to avoid breaking current prototypes; further hardening will be iterative.
