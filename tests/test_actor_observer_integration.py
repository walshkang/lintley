from actor_observer_hitl import run_workflow


class FakeProvider:
    """Minimal provider shim used for integration tests.

    It implements the same generate(system_prompt, user_message) -> str API
    used by the Actor and Observer functions in actor_observer_hitl.py.
    Also exposes attributes `provider` and `model` expected by run_workflow.
    """

    def __init__(self, actor_text: str, observer_text: str):
        self.actor_text = actor_text
        self.observer_text = observer_text
        self.provider = "fake"
        self.model = "mock-model"

    def generate(self, system_prompt: str, user_message: str, max_tokens: int = 1000) -> str:
        # Heuristic detection used by actor/observer prompts
        if "Actor Agent" in system_prompt or "You are the Actor Agent" in system_prompt:
            return self.actor_text
        if "Observer Agent" in system_prompt or "You are the Observer Agent" in system_prompt:
            return self.observer_text
        return ""


def test_actor_observer_integration_auto_approve():
    actor_text = "ANALYSIS:\nSteps...\nDECISION:\nApply patch X\nCONFIDENCE:\nhigh"
    observer_text = "AUDIT_SUMMARY: PASS\nFINDINGS: None\nRISK_LEVEL: low\nRECOMMENDATION: Proceed"
    provider = FakeProvider(actor_text, observer_text)

    result = run_workflow(provider, "Test task", context="", allow_auto_approve=True)

    assert result["status"] == "approved"
    assert result["risk_level"] == "low"
