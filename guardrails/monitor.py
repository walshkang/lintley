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


if __name__ == "__main__":
    sys.exit(main())
