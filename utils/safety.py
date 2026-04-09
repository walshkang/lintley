import re
import hashlib
from typing import Any, List, Tuple

# Tunable constants to avoid magic-number linter complaints
MAX_LINE_LEN = 1000
MIN_SECRET_LEN = 5

INJECTION_PATTERNS = [
    r"ignore (previous )?instructions",
    r"ignore previous prompt",
    r"do not follow system",
]

SECRET_PATTERNS = [
    # PEM blocks
    r"-----BEGIN [A-Z ]+-----[\s\S]+?-----END [A-Z ]+-----",
    # env-like KEY=VALUE patterns (short key, longer value)
    r"[A-Z0-9_]{3,30}=[A-Za-z0-9\-\._~\+/]+=*",
    # long base64-ish strings
    r"[A-Za-z0-9_\-]{40,}",
]


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sanitize_user_input(text: str, max_lines: int = 200, max_chars: int = 3000) -> str:
    """Basic sanitization to reduce prompt-injection surface.

    - Lowercase-checks for known injection phrases and removes them
    - Removes obvious shell/command lines that start with `$` or `>`
    - Truncates to max_lines and max_chars
    - Collapses repeated blank lines
    """
    if not isinstance(text, str):
        return text
    t = text
    # remove explicit injection phrases
    for pat in INJECTION_PATTERNS:
        t = re.sub(pat, "", t, flags=re.IGNORECASE)
    # remove lines that look like shell commands or prompts
    lines = []
    for line in t.splitlines():
        s = line.strip()
        if not s:
            lines.append("")
            continue
        if s.startswith(("$", "!", "//", "#")):
            # drop obvious commands
            continue
        # drop lines that appear to be 'run:' directives
        if re.match(r"^run[: ].*", s, flags=re.IGNORECASE):
            continue
        # drop lines that are excessive length
        if len(s) > MAX_LINE_LEN:
            s = s[:MAX_LINE_LEN] + "..."
        lines.append(s)
        if len(lines) >= max_lines:
            break
    out = "\n".join(lines)
    if len(out) > max_chars:
        out = out[:max_chars] + "..."
    # collapse multi-blank
    out = re.sub(r"\n{3,}", "\n\n", out)
    return out


def redact_secrets(text: Any) -> Any:
    """Redacts common secret-like patterns in strings. Returns non-str inputs unchanged."""
    if not isinstance(text, str):
        return text
    t = text
    for pat in SECRET_PATTERNS:
        found = re.findall(pat, t)
        for m in found:
            if isinstance(m, tuple):
                m = m[0]
            if len(m) < MIN_SECRET_LEN:
                continue
            h = _sha256(m)
            t = t.replace(m, f"[REDACTED:{h[:8]}]")
    # redact long dot-separated tokens (JWT-like)
    jwt_like = re.findall(r"[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+", t)
    for j in jwt_like:
        h = _sha256(j)
        t = t.replace(j, f"[REDACTED:{h[:8]}]")
    return t


def validate_agent_output(agent_type: str, payload: Any) -> Tuple[bool, List[str]]:
    """Very small schema validator for agent outputs. Returns (ok, errors).

    agent_type: 'actor'|'observer'|'test'
    """
    if not isinstance(payload, dict):
        return False, ["payload-not-dict"]
    required = []
    if agent_type == "actor":
        required = ["analysis", "patch", "instructions", "confidence"]
    elif agent_type == "observer":
        required = ["verdict", "findings", "risk_level"]
    elif agent_type == "test":
        required = ["total", "passed", "failed"]
    else:
        return True, []
    missing = [k for k in required if k not in payload]
    if missing:
        return False, [f"missing:{m}" for m in missing]
    return True, []
