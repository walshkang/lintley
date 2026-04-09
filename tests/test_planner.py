import json
from planners.planner import Planner


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
            return json.dumps(
                {
                    "analysis": "Change config X to enable Y.",
                    "patch": patch,
                    "instructions": "Apply and run config validation.",
                    "confidence": "high",
                }
            )
        if "Observer" in system_prompt:
            return json.dumps(
                {
                    "verdict": "PASS",
                    "findings": [],
                    "risk_level": "low",
                    "recommended_changes": "",
                }
            )
        return "{}"


SLICES_EXPECTED = 2


def test_planner_plan_and_dispatch(capsys):
    context_files = {
        "a.py": "def f():\n    return 1\n",
        "b.py": "def g():\n    return 2\n",
    }

    p = Planner()
    plan = p.plan("Enable feature X", context_files, model_hint="balanced", concurrency_limit=2)

    assert "run_id" in plan
    assert len(plan["slices"]) == SLICES_EXPECTED
    for s in plan["slices"]:
        assert "slice_id" in s
        assert "agents" in s

    # Dispatch with fake provider - should produce events per agent per slice
    provider = FakeProvider()
    p.dispatch(plan, provider)

    captured = capsys.readouterr()
    lines = [line for line in captured.out.splitlines() if line.strip()]
    # events count equals sum of agents for each slice
    expected = sum(len(s.get("agents", [])) for s in plan["slices"])
    assert len(lines) >= expected
    events = [json.loads(line) for line in lines]
    assert events[0]["event"] == "actor_proposal"
