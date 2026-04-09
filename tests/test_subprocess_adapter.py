from providers.subprocess_adapter import SubprocessAdapter


def test_subprocess_adapter_mock_actor():
    adapter = SubprocessAdapter(command=["mock"])
    sys_p = "Actor System prompt"
    user_p = "Do the thing"
    out = adapter.generate(sys_p, user_p)
    assert isinstance(out, str)
    assert "analysis" in out or "ok" in out


def test_subprocess_adapter_mock_observer():
    adapter = SubprocessAdapter(command=["mock"])
    sys_p = "Observer System prompt"
    user_p = "Check the patch"
    out = adapter.generate(sys_p, user_p)
    assert isinstance(out, str)
    assert "verdict" in out or "ok" in out
