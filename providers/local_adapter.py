"""Local adapter wrapper used for local, deterministic runs in CI/tests.

This is a thin shim around the existing MockProvider to provide a stable
"adapter" surface for later real provider implementations.
"""
# fmt: off
from providers.mock_provider import MockProvider


class LocalAdapter:
    """Thin adapter that delegates to MockProvider for deterministic output.

    Future: replace with real local LLM or subprocess-based adapter.
    """

    def __init__(self, model: str | None = None) -> None:
        self.model = model or "local-mock"
        self._mock = MockProvider(model=self.model)

    def generate(self, system_prompt: str, user_message: str) -> str:
        """Generate a response string for the given prompts.

        Returns a JSON string (mock) to match existing providers' contract.
        """
        return self._mock.generate(system_prompt, user_message)

# fmt: on
