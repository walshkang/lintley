Provider selection and CLI usage

The CLI supports selecting which provider/adapter to run a workflow with the `--provider` flag.

Supported values:

- `mock` or `local` — uses the deterministic LocalAdapter (default)
- `subprocess` — runs a local command as the model; configure `command` in the saved config or pass via SubprocessAdapter

Examples

Run a workflow using the mock adapter (default):

    python3 hitl_multitask.py execute <task_id>

Run a workflow and override provider to subprocess:

    python3 hitl_multitask.py execute <task_id> --provider=subprocess

To configure a subprocess command for the adapter, save a config file at `.hitl_state/config.json` with:

```json
{
  "provider": "subprocess",
  "command": ["/path/to/local-llm", "--arg", "value"]
}
```

Testing notes

- Tests include `tests/test_adapter_selection.py` to assert adapter selection.
- Use `pytest -q` to run the test suite.
