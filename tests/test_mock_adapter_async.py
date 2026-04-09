import pytest

from providers.mock_adapter import MockAdapter


@pytest.mark.asyncio
async def test_stream_async():
    adapter = MockAdapter(["h", "i"], delay=0)
    tokens = []
    async for t in adapter.stream("prompt"):
        tokens.append(t)
    assert "".join(tokens) == "hi"
