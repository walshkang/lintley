# [![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE) [![CI](https://github.com/walsh.kang/lintley/actions/workflows/ci.yml/badge.svg)](https://github.com/walsh.kang/lintley/actions/workflows/ci.yml)

Lintley — Multi-Agent HITL Coordination

Table of Contents
- Quick Start
- Goals & Vision
- For the vibe coder
- Contributing
- Docs
- Testing


A generic, multi-provider framework for running parallel AI workflows with human-in-the-loop (HITL) checkpoints. Coordinates multiple agents (Actor, Observer) across tasks, tracks approval state, and integrates with any LLM provider (Anthropic, Google, OpenAI).

**Use case:** You're working on 3–5 parallel slices in separate terminals. Each slice runs an Actor agent to propose changes, an Observer agent to audit for hallucinations/goal drift, and a human checkpoint before execution. Lintley manages state across all of them so you can batch approvals instead of blocking on each one.

---

## Quick Start

### 1. Setup (one-time)

```bash
# Clone/enter the directory
cd lintley

# Create venv
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install anthropic google-generativeai openai

# Configure your API key (auto-detects provider)
python3 hitl_multitask.py setup
```

You'll be prompted for an API key. It auto-detects the provider (Anthropic, Google, OpenAI) and saves config to `.hitl_state/config.json`.

Quick examples for testing locally (no external API keys required):

- Sample config (subprocess mock): `docs/examples/config_example.json`
- Sample task definition: `docs/examples/sample_task.json`

To try the mock subprocess flow:

```bash
mkdir -p .hitl_state
cp docs/examples/config_example.json .hitl_state/config.json
python3 hitl_multitask.py submit docs/examples/sample_task.json
# note the returned task id, then:
python3 hitl_multitask.py execute <task_id> --provider=subprocess
```

This uses the `mock` subprocess shortcut so you can exercise the full Actor→Observer→HITL cycle without external LLMs.

### 2. Submit Tasks

Create a task definition (JSON):

```json
{
  "title": "Layout rebalance",
  "goal": "Adjust flex ratios to achieve 60/40 split",
  "context": "Current: panel 380px (flex-1 map), Target: flex-[3] / flex-[2]",
  "model_hint": "balanced"
}
```

Submit it:

```bash
python3 hitl_multitask.py submit my_task.json
```

### 3. Run Workflows

Start the Actor → Observer → HITL cycle:

```bash
python3 hitl_multitask.py execute <task_id>
```

This will:
- Run the Actor agent (proposes solution)
- Run the Observer agent (audits for issues)
- Set the task to `pending_approval`

### 4. Monitor & Approve

**Dashboard** (real-time monitoring):
```bash
python3 hitl_multitask.py dashboard
```

Shows all pending approvals with risk levels. Press Ctrl+C to exit.

**Check status anytime:**
```bash
python3 hitl_multitask.py status
```

**Approve or reject:**
```bash
python3 hitl_multitask.py approve <task_id>
python3 hitl_multitask.py reject <task_id>
```

---

## Two Modes

### Mode 1: Single-Task Interactive (`actor_observer_hitl.py`)

For one task at a time with full control. Prompts for API key on startup, lists available models, runs the full workflow interactively.

```bash
python3 actor_observer_hitl.py
```

**Use when:**
- You're testing a single task
- You want to review Actor/Observer output before approval
- You prefer interactive prompts over CLI flags

### Mode 2: Multi-Task Coordinator (`hitl_multitask.py`)

For parallel tasks across multiple terminals. Non-blocking execution, shared state file, batched approvals.

```bash
# Terminal 1: Submit task 1
python3 hitl_multitask.py submit task1.json
python3 hitl_multitask.py execute <task_id>

# Terminal 2: Submit task 2
python3 hitl_multitask.py submit task2.json
python3 hitl_multitask.py execute <task_id>

# Claude Code: Monitor all
python3 hitl_multitask.py dashboard

# When ready, batch approve
python3 hitl_multitask.py approve task1
python3 hitl_multitask.py approve task2
```

---

## Supported Providers

| Provider | API Key Format | Models |
|----------|---|---|
| **Anthropic** | `sk-ant-...` | Claude Opus, Sonnet, Haiku |
| **Google** | `AIza...` or long alphanumeric | Gemini 2.0, Gemini 1.5, Gemma |
| **OpenAI** | `sk-...` (non-Anthropic) | GPT-4, GPT-3.5 |

Get API keys:
- Anthropic: https://console.anthropic.com/
- Google: https://aistudio.google.com/app/apikey
- OpenAI: https://platform.openai.com/api-keys

---

## Task Definition Schema

```json
{
  "id": "optional-custom-id",
  "title": "Short task name",
  "goal": "What should the outcome be?",
  "context": "Code snippet, requirements, or background",
  "model_hint": "optional: 'fast' | 'balanced' | 'powerful'"
}
```

**Fields:**
- `title` — Human-readable name
- `goal` — What you're trying to achieve (used by Actor)
- `context` — Code, requirements, or background (passed to Actor)
- `model_hint` — Optional hint for model selection (currently for documentation; future: auto-select based on complexity)

---

## Workflow Stages

```
┌─────────────┐
│ Task Submitted
│ status: pending_actor
└──────┬──────┘
       │
       ▼
┌──────────────────┐
│ Actor Agent Runs
│ Proposes solution
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Observer Agent Runs
│ Audits for risks
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Human Checkpoint
│ status: pending_approval
│ Awaits your decision
└──────┬───────────┘
       │
   ┌───┴────┐
   │         │
   ▼         ▼
APPROVE    REJECT
   │         │
   ▼         ▼
status:   status:
approved  rejected
```

---

## State Files

Lintley stores all state in `.hitl_state/`:

```
.hitl_state/
├── config.json          # API key + provider config
└── tasks/
    ├── abc123.json      # Task state (actor work, observer review, etc.)
    ├── def456.json
    └── ...
```

**Don't commit these to git** — add to `.gitignore`:
```
.hitl_state/
```

---

## Examples

### Example 1: Review Code for Security

```json
{
  "title": "Security audit: user login handler",
  "goal": "Find SQL injection, XSS, or auth bypass vulnerabilities",
  "context": "def login(username, password):\n    query = f'SELECT * FROM users WHERE username={username}'\n    ...",
  "model_hint": "powerful"
}
```

### Example 2: Layout Rebalance

```json
{
  "title": "N5c — Sources layout rebalance",
  "goal": "Change desktop layout from 50/50 (380px + flex-1) to 60/40 (flex-[3] + flex-[2])",
  "context": "File: components/app/SourcesShellPaper.tsx\nLine 200: Panel container\nLine 216: Map container\nMobile: unchanged\nDon't touch: SourcesPanel.tsx, MapShell.tsx",
  "model_hint": "balanced"
}
```

### Example 3: Refactor Function

```json
{
  "title": "Extract user validation logic",
  "goal": "Move validation rules out of the endpoint handler into a reusable validator function",
  "context": "Current handler: src/api/users.ts (lines 45–120)\nNeeds: email validation, password strength check, age verification",
  "model_hint": "balanced"
}
```

---

## Typical Workflow

**Your setup:**
```
Terminal 1: Claude Code (planning)
Terminal 2: Copilot slice 1 (running in parallel)
Terminal 3: Copilot slice 2 (running in parallel)
Terminal 4: Copilot slice 3 (running in parallel)
```

**How it works:**

1. **Planning phase (Claude Code):**
   - Review your slices, shape them up
   - Write task definitions (JSON)

2. **Execution phase (Copilot tabs):**
   ```bash
   # Tab 2
   python3 hitl_multitask.py submit slice1.json
   python3 hitl_multitask.py execute <id>
   # Actor → Observer → pending_approval
   # Tab continues; doesn't block
   
   # Tab 3
   python3 hitl_multitask.py submit slice2.json
   python3 hitl_multitask.py execute <id>
   # Same, non-blocking
   
   # Tab 4
   python3 hitl_multitask.py submit slice3.json
   python3 hitl_multitask.py execute <id>
   # Same, non-blocking
   ```

3. **Approval phase (Claude Code):**
   ```bash
   python3 hitl_multitask.py dashboard
   # See all 3 tasks pending approval
   
   # Review each one
   python3 hitl_multitask.py approve slice1
   python3 hitl_multitask.py approve slice2
   python3 hitl_multitask.py approve slice3
   ```

---

## Customization

### Custom Model Selection

Edit `ProviderClient.list_models()` in `hitl_multitask.py` to control which models appear.

### Custom Risk Assessment

Edit `extract_risk_level()` in `actor_observer_hitl.py` to change how risk is determined from Observer output.

### Custom Prompts

Edit the `system_prompt` strings in `actor_agent()` and `observer_agent()` to change agent behavior.

---

## Troubleshooting

**"Could not resolve authentication method"**
- Ensure your API key is correct
- Run `python3 hitl_multitask.py setup` again

**"Provider not detected"**
- Your API key format isn't recognized
- Manually specify: `python3 hitl_multitask.py setup` and choose from the menu

**"No models available"**
- Check your API key has the right permissions
- Manually enter a model name when prompted

**Tasks stuck in `pending_approval`**
- Run `python3 hitl_multitask.py approve <task_id>`
- Or `python3 hitl_multitask.py reject <task_id>` to decline

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│ User (you)                                      │
│ Terminal 1: planning | Terminal 2-4: execution │
└────────────┬────────────────────────────────────┘
             │
     ┌───────▼────────┐
     │ CLI Interface  │
     │ (hitl_multitask.py)
     └───────┬────────┘
             │
    ┌────────▼────────┐
    │ State Manager   │
    │ (.hitl_state/) │
    └────────┬────────┘
             │
    ┌────────▼────────────┐
    │ LLM Client          │
    │ (ProviderClient)   │
    └────────┬────────────┘
             │
    ┌────────▼──────────┐
    │ LLM Provider       │
    │ (Anthropic/Google/ │
    │  OpenAI)           │
    └────────────────────┘
```

---

## Contributing

Contributions welcome — see CONTRIBUTING.md and CODE_OF_CONDUCT.md for guidelines and expectations. To propose features or fixes, open an issue or submit a PR. Small, focused PRs with tests are easiest to review.

---

## License

MIT

---

## Feedback

For issues or questions, open a GitHub issue or contact the maintainer.

## Safety
Lintley is local-first and includes basic prompt-injection mitigations by default: inputs are lightly sanitized (utils.safety.sanitize_user_input) and outputs are redacted (utils.safety.redact_secrets). Repository contents are not sent to third-party providers without explicit opt-in. See ROADMAP.md for advanced mitigations (Jinja2 templating, schema validation, review workflows) and timelines.
