import os
from typing import Optional

from providers.mock_provider import MockProvider


class GPT5MiniAdapter:
    """Adapter shim for gpt-5-mini.

    By default (HITL_USE_MOCK=1 or no HITL_API_KEY) this delegates to MockProvider for
    local development and CI. In future, implement actual RPC/HTTP client here.
    """

    def __init__(
        self,
        use_mock: Optional[bool] = None,
        actor_patch: Optional[str] = None,
    ) -> None:
        env_use_mock = os.environ.get("HITL_USE_MOCK")
        if use_mock is None:
            use_mock = True if env_use_mock in (None, "1", "true", "True") else False
        self.use_mock = bool(use_mock)
        self.actor_patch = actor_patch

        if self.use_mock:
            self._mock = MockProvider(actor_patch=self.actor_patch)
        else:
            self._mock = None
            # Placeholder for real client initialization using HITL_API_KEY or local socket
            api_key = os.environ.get("HITL_API_KEY")
            if not api_key:
                raise RuntimeError(
                    "HITL_API_KEY required when HITL_USE_MOCK is false"
                )
            # Real implementation would go here

        # metadata
        self.provider = "gpt-5-mini"
        self.model = os.environ.get("HITL_MODEL", "gpt-5-mini")

    def generate(
        self,
        system_prompt: str,
        user_message: str,
        max_tokens: int = 1000,
    ) -> str:
        """Synchronous generate API returning a JSON-serializable string or raw text."""
        if self.use_mock:
            return self._mock.generate(
                system_prompt, user_message, max_tokens=max_tokens
            )
        # For now, raise; real call would integrate with LLM runtime
        raise NotImplementedError(
            "GPT5MiniAdapter real client not implemented yet"
        )

    async def stream(
        self,
        system_prompt: str,
        user_message: str,
        max_tokens: int = 1000,
    ):
        """Optional async stream API for future usage. Delegates to mock in dev."""
        if self.use_mock:
            # yield full string in one chunk to mimic streaming
            yield self._mock.generate(
                system_prompt, user_message, max_tokens=max_tokens
            )
            return
        raise NotImplementedError("stream not implemented for real client")
