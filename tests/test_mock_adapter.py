import asyncio

from providers.mock_adapter import MockAdapter


def test_mock_adapter_streams_tokens():
    script = ["hello", " ", "world", "!"]
    adapter = MockAdapter(script, delay=0)

    async def collect():
        tokens = []
        async for t in adapter.stream("prompt"):
            tokens.append(t)
        return "".join(tokens)

    result = asyncio.run(collect())
    assert result == "hello world!"
