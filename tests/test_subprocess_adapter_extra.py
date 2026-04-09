import json
import subprocess
from unittest.mock import Mock, patch

from providers.subprocess_adapter import SubprocessAdapter


def test_subprocess_run_stdout_decoded():
    adapter = SubprocessAdapter(command=["/bin/echo"])
    mock_proc = Mock()
    mock_proc.stdout = b'{"ok": true}\n'
    mock_proc.stderr = b""

    with patch("subprocess.run", return_value=mock_proc) as run_mock:
        out = adapter.generate("sys", "user")
        assert out.strip() == '{"ok": true}'
        run_mock.assert_called()


def test_subprocess_timeout_returns_error_json():
    adapter = SubprocessAdapter(command=["/bin/slow"])

    def raise_timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd=kwargs.get("args", "cmd"), timeout=kwargs.get("timeout", 1))

    with patch("subprocess.run", side_effect=raise_timeout):
        out = adapter.generate("s", "u")
        parsed = json.loads(out)
        assert parsed.get("error") == "timeout"
