import os
import json

from providers.gpt5_mini_adapter import GPT5MiniAdapter


def test_gpt5_adapter_uses_mock_by_default():
    # Ensure environment is set to use mock provider
    os.environ["HITL_USE_MOCK"] = "1"

    adapter = GPT5MiniAdapter()
    out = adapter.generate("You are Actor", "Task: test")

    # Should be JSON string produced by MockProvider
    parsed = json.loads(out)
    assert isinstance(parsed, dict)
    assert "analysis" in parsed or parsed.get("ok") is True


def test_gpt5_adapter_stream_yields_string():
    os.environ["HITL_USE_MOCK"] = "1"
    adapter = GPT5MiniAdapter()

    import asyncio

    async def run_stream():
        parts = []
        async for chunk in adapter.stream("You are Actor", "Task: test"):
            parts.append(chunk)
        return parts

    parts = asyncio.run(run_stream())
    assert len(parts) >= 1
    # first chunk should be JSON string
    parsed = json.loads(parts[0])
    assert isinstance(parsed, dict)
