import json
from agents_demo import DemoRunner


class FakeProvider:
    def generate(self, system_prompt: str, user_message: str):
        if "Actor" in system_prompt:
            patch = (
                "diff --git a/config.yml b/config.yml\n"
                "--- a/config.yml\n"
                "+++ b/config.yml\n"
                "@@ -1 +1 @@\n"
                "-old: false\n"
                "+old: true\n"
            )
            return json.dumps({
                "analysis": "Change config X to enable Y.",
                "patch": patch,
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


EXPECTED_EVENTS = 3


def test_demo_runner_prints_json_lines(capsys):
    provider = FakeProvider()
    runner = DemoRunner(provider)
    runner.run("Enable feature X")

    captured = capsys.readouterr()
    lines = [line for line in captured.out.splitlines() if line.strip()]
    assert len(lines) == EXPECTED_EVENTS

    events = [json.loads(line) for line in lines]
    assert events[0]["event"] == "actor_proposal"
    assert "analysis" in events[0]["payload"]
    assert events[1]["event"] == "observer_audit"
    assert events[1]["payload"]["risk_level"] == "low"
    assert events[2]["event"] == "patch_ready"
    assert events[2]["payload"]["applies"] is True
