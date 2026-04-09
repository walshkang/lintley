"""Local adapter wrapper used for local, deterministic runs in CI/tests.

This is a thin shim around the existing MockProvider to provide a stable
"adapter" surface for later real provider implementations.
"""

from providers.mock_provider import MockProvider
from utils.safety import sanitize_user_input, redact_secrets


class LocalAdapter:
    """Thin adapter that delegates to MockProvider for deterministic output.

    Future: replace with real local LLM or subprocess-based adapter.
    """

    def __init__(self, model: str | None = None) -> None:
        self.model = model or "local-mock"
        self._mock = MockProvider()
        try:
            self._mock.model = self.model
        except Exception:
            # provider may not expose model attribute
            pass

    def generate(self, system_prompt: str, user_message: str) -> str:
        """Generate a response string for the given prompts.

        Performs lightweight sanitization of inputs and redaction of outputs to
        reduce prompt-injection / secret-leakage surface for local providers.
        Returns a JSON string (mock) to match existing providers' contract.
        """
        sys_p = sanitize_user_input(system_prompt)
        user_p = sanitize_user_input(user_message)
        resp = self._mock.generate(sys_p, user_p)
        try:
            resp = redact_secrets(resp)
        except Exception:
            # be permissive: if redaction fails, return original response
            return resp
        return resp

