Testing with real models (local)

If you'd like to run Lintley locally against a real provider (e.g., Google's Gemma model), create a `.env.local` file at the repo root with the following keys:

- HITL_PROVIDER=google
- HITL_API_KEY=<your_api_key>
- HITL_MODEL=gemma-4-27b-it

Example `.env.local`:

```
HITL_PROVIDER=google
HITL_API_KEY=AIza... or <long key>
HITL_MODEL=gemma-4-27b-it
```

Options to use these values:

- Run the interactive setup and paste your API key when prompted: `python3 hitl_multitask.py setup`
- Or manually populate `.hitl_state/config.json` with the JSON below (create `.hitl_state/` first):

```
{
  "provider": "google",
  "api_key": "<your_key>",
  "model": "gemma-4-27b-it",
  "saved_at": "2026-..."
}
```

Security note: Do NOT commit `.env.local` or `.hitl_state/config.json` to git. Add them to `.gitignore`.

Running tests locally

- Use a venv: `python3 -m venv venv && source venv/bin/activate`
- Install dev deps: `python -m pip install -U pip pytest pytest-asyncio ruff black`
- Run linters: `ruff check .` and `black --check .`
- Run tests: `pytest -q`

CI will not call real provider APIs; integration tests use FakeProvider/MockAdapter for determinism.
