"""Unit tests for LocalAdapter and MockProvider integration."""

import json

from providers.local_adapter import LocalAdapter
from agents_demo import DemoRunner


def test_local_adapter_returns_json_string():
    adapter = LocalAdapter()
    s = "Actor System: Actor"
    u = "User: do something"
    out = adapter.generate(s, u)
    # Should be a parseable JSON string (mock returns json.dumps)
    payload = json.loads(out)
    assert isinstance(payload, dict)
    # Basic expected keys may vary depending on prompt \n fallback
    assert "analysis" in payload or "verdict" in payload or payload == {}


def test_demo_runner_end_to_end_no_exceptions(capsys):
    adapter = LocalAdapter()
    runner = DemoRunner(adapter)
    # Should not raise and should print at least three events
    runner.run("Test: demo run")
    captured = capsys.readouterr()
    lines = [l for l in captured.out.splitlines() if l.strip()]
    assert len(lines) >= 3
    # Each line should be valid JSON
    for ln in lines:
        data = json.loads(ln)
        assert "event" in data and "task" in data and "payload" in data
