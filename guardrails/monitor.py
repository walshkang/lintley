import re
import sys
import json
from typing import List, Tuple

RISK_PATTERNS = [
    (r"\brm\s+-rf\b", "recursive force remove (rm -rf)", 10),
    (r"\bsudo\s+rm\b", "sudo rm (may remove protected files)", 9),
    (r"\brm\s+-R\b", "recursive remove (rm -R)", 8),
    (r"\bmkfs\b", "disk format (mkfs)", 10),
    (r"\bdd\b.*\bof=", "raw disk write with dd of=", 10),
    (r"\bshutdown\b", "shutdown/poweroff command", 8),
    (r"\bpoweroff\b", "poweroff command", 8),
    (r"\binit\s+[0-6]\b", "reboot/init change", 7),
]


def detect_risky_command(cmd: str) -> Tuple[int, List[str]]:
    """Return a cumulative risk score and list of matched reasons."""
    score = 0
    reasons: List[str] = []
    for pat, reason, severity in RISK_PATTERNS:
        if re.search(pat, cmd):
            score += severity
            reasons.append(reason)
    return score, reasons


def suggest_safe_alternatives(cmd: str) -> str:
    """Return a short suggestion based on detected risky commands."""
    if re.search(r"\brm\s+-rf\b|\bsudo\s+rm\b", cmd):
        return (
            "Consider using: git clean -n / dry-run, rm -i to prompt per-file, "
            "or use a trash tool (trash-cli). Double-check the path before running."
        )
    if re.search(r"\bmkfs\b|\bdd\b.*\bof=", cmd):
        return (
            "This looks like a destructive disk operation. Ensure target device is correct, "
            "use a VM/container or a drive image for testing, and unmount first."
        )
    if re.search(r"\bshutdown\b|\bpoweroff\b", cmd):
        return "This will affect system availability; confirm with the team before proceeding."
    return "No special suggestions."


def main(argv: List[str] = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if not argv:
        print(json.dumps({"error": "no command provided"}))
        return 1
    cmd = " ".join(argv)
    score, reasons = detect_risky_command(cmd)
    out = {
        "cmd": cmd,
        "risk_score": score,
        "reasons": reasons,
        "suggestion": suggest_safe_alternatives(cmd),
    }
    print(json.dumps(out, indent=2))
    # Exit code 0 = OK, 2 = blocked/unsafe
    return 2 if score > 0 else 0


def audit_event(cmd: str, score: int, reasons: list, suggestion: str, confirmed: bool, executed: bool, audit_path: str | None = None) -> None:
    """Append an audit event (JSON line) to the audit log.

    Fields: cmd, risk_score, reasons, suggestion, confirmed, executed, ts
    """
    try:
        # Lazy import to avoid cycles
        from guardrails.config import ensure_audit_dir, load_config
    except Exception:
        from guardrails import config as _cfg
        ensure_audit_dir = _cfg.ensure_audit_dir

    if audit_path is None:
        try:
            audit_path = load_config().get("audit_path")
        except Exception:
            audit_path = ensure_audit_dir()
    else:
        ensure_audit_dir(audit_path)

    event = {
        "cmd": cmd,
        "risk_score": score,
        "reasons": reasons,
        "suggestion": suggestion,
        "confirmed": bool(confirmed),
        "executed": bool(executed),
    }
    try:
        with open(audit_path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(event) + "\n")
    except Exception:
        # Do not let audit logging break main flow
        pass


if __name__ == "__main__":
    sys.exit(main())
