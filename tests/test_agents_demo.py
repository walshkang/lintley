import json
from agents_demo import DemoRunner


class FakeProvider:
    def generate(self, system_prompt: str, user_message: str):
        if "Actor" in system_prompt:
            return json.dumps({
                "analysis": "Change config X to enable Y.",
                "patch": "diff --git a/config.yml b/config.yml\n--- a/config.yml\n+++ b/config.yml\n@@ -1 +1 @@\n-old: false\n+old: true\n",
                "instructions": "Apply and run config validation.",
                "confidence": "high",
            })
        if "Observer" in system_prompt:
            return json.dumps({
                "verdict": "PASS",
                "findings": [],
                "risk_level": "low",
                "recommended_changes": "",
            })
        return "{}"


def test_demo_runner_prints_json_lines(capsys):
    provider = FakeProvider()
    runner = DemoRunner(provider)
    runner.run("Enable feature X")

    captured = capsys.readouterr()
    lines = [l for l in captured.out.splitlines() if l.strip()]
    assert len(lines) == 3

    events = [json.loads(l) for l in lines]
    assert events[0]["event"] == "actor_proposal"
    assert "analysis" in events[0]["payload"]
    assert events[1]["event"] == "observer_audit"
    assert events[1]["payload"]["risk_level"] == "low"
    assert events[2]["event"] == "patch_ready"
    assert events[2]["payload"]["applies"] is True
