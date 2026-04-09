import json
import time


class MockProvider:
    """Simple synchronous Mock provider that returns deterministic JSON strings
    based on the system prompt. Used for local prototyping and CI.
    """

    def __init__(self, actor_patch=None):
        # actor_patch: optional diff string to return for Actor outputs
        self.actor_patch = actor_patch or (
            "diff --git a/foo.txt b/foo.txt\n" "--- a/foo.txt\n" "+++ b/foo.txt\n" "@@ -1 +1 @@\n" "-old\n" "+new\n"
        )
        self.provider = "mock"
        self.model = "gpt-5-mini-mock"

    def generate(self, system_prompt: str, user_message: str, max_tokens: int = 1000) -> str:
        # slight delay to simulate work
        time.sleep(0.01)
        if "Actor" in system_prompt or "SliceActor" in system_prompt:
            payload = {
                "analysis": "Make a minimal change to fix the described issue.",
                "patch": self.actor_patch,
                "instructions": "Apply the patch and run tests.",
                "confidence": "high",
                "metadata": {"model": self.model},
            }
            return json.dumps(payload)

        if "Observer" in system_prompt or "SliceObserver" in system_prompt:
            payload = {
                "verdict": "PASS",
                "findings": [],
                "risk_level": "low",
                "recommended_changes": "",
                "metadata": {"model": self.model},
            }
            return json.dumps(payload)

        if "TestAgent" in system_prompt:
            payload = {
                "total": 10,
                "passed": 10,
                "failed": 0,
                "failures": [],
                "metadata": {"model": self.model},
            }
            return json.dumps(payload)

        # Default
        return json.dumps({"ok": True})
