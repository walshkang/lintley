import asyncio
from typing import AsyncIterator, Dict, List, Optional


class MockAdapter:
    """A deterministic, test-friendly LLM adapter for CI and unit tests.

    Usage:
        adapter = MockAdapter(["hello", " ", "world", "!"])
        async for token in adapter.stream("prompt"):
            print(token)
    """

    def __init__(self, script: List[str], delay: float = 0.0) -> None:
        self.script = list(script)
        self.delay = float(delay)
        self._cancelled = False

    async def stream(self, prompt: str, metadata: Optional[Dict] = None) -> AsyncIterator[str]:
        """Yield tokens from the pre-seeded script. Non-blocking by default (delay=0).

        Kept intentionally minimal so tests remain deterministic.
        """
        self._cancelled = False
        for token in self.script:
            if self._cancelled:
                return
            if self.delay:
                await asyncio.sleep(self.delay)
            yield token

    async def cancel(self, stream_id: str) -> bool:
        """Request cancellation of an in-flight stream. Returns True if cancellation requested."""
        self._cancelled = True
        return True

    def status(self) -> Dict:
        return {"state": "idle", "stream_id": None, "progress": None}
