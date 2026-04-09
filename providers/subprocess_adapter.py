import json
import shlex
import subprocess
from typing import List, Optional

from providers.mock_provider import MockProvider


class SubprocessAdapter:
    """Adapter that calls a subprocess for generation.

    Usage:
      SubprocessAdapter(command=["/usr/bin/whatever"]) - runs the command and
      sends the combined system+"\n\n"+user string to the process' stdin.

    For quick local testing, pass command=["mock"] to delegate to MockProvider
    (deterministic JSON responses) without spawning a process.
    """

    def __init__(self, command: Optional[List[str]] = None, timeout: int = 30) -> None:
        self.command = command or ["mock"]
        self.timeout = timeout
        self._mock = MockProvider()

    def generate(self, system_prompt: str, user_message: str) -> str:
        # Mock shortcut
        if len(self.command) == 1 and self.command[0] == "mock":
            # Choose actor vs observer vs test by looking for keywords
            combined = (system_prompt or "")
            if "Actor" in combined or "SliceActor" in combined or "actor" in combined.lower():
                return self._mock.generate(system_prompt, user_message)
            if "Observer" in combined or "SliceObserver" in combined or "observer" in combined.lower():
                return self._mock.generate(system_prompt, user_message)
            if "TestAgent" in combined or "test_agent" in combined.lower():
                return self._mock.generate(system_prompt, user_message)
            return json.dumps({"ok": True})

        # Otherwise run the user command
        try:
            # Prepare input
            inp = f"SYSTEM:\n{system_prompt}\n\nUSER:\n{user_message}\n"
            proc = subprocess.run(
                self.command,
                input=inp.encode("utf-8"),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=self.timeout,
                check=False,
            )
            out = proc.stdout.decode("utf-8", errors="replace").strip()
            if not out:
                # include stderr if no stdout
                out = proc.stderr.decode("utf-8", errors="replace").strip() or ""
            return out
        except subprocess.TimeoutExpired as e:
            return json.dumps({"error": "timeout", "details": str(e)})
        except Exception as e:
            return json.dumps({"error": "subprocess-failed", "details": str(e)})
