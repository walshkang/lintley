from guardrails.timeline import annotate_command, find_agent_events


def sample_timeline():
    return [
        {"type": "message", "actor": "ActorAgent", "source": "agent", "command": "rm -rf /tmp/foo", "chain_of_thought": "I should remove the temp dir to clean up before patching."},
        {"type": "message", "actor": "Observer", "source": "agent", "text": "This patch looks risky."},
        {"type": "message", "actor": "dev", "source": "user", "command": "echo hello"},
    ]


def test_find_agent_events():
    tl = sample_timeline()
    events = find_agent_events(tl)
    assert len(events) == 2


def test_annotate_command_matches():
    tl = sample_timeline()
    ann = annotate_command("rm -rf /tmp/foo", tl)
    assert ann["cmd"] == "rm -rf /tmp/foo"
    assert len(ann["matched_events"]) == 1
    assert "remove the temp dir" in ann["cot"]
