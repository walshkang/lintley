import os
import json
import subprocess
from pathlib import Path


def test_audit_log_written(tmp_path, monkeypatch):
    repo_root = Path(__file__).resolve().parent.parent
    audit_dir = repo_root / ".guardrails"
    # Ensure clean state
    if audit_dir.exists():
        for f in audit_dir.iterdir():
            f.unlink()
    if audit_dir.exists():
        audit_dir.rmdir()

    # Run a risky command with auto-confirm but no execution
    p = subprocess.run(["./scripts/guarded_exec", "-y", "rm", "-rf", "/tmp/some_nonexistent_path_for_test"], capture_output=True, text=True)
    assert p.returncode == 0

    audit_file = repo_root / ".guardrails" / "audit.log"
    assert audit_file.exists(), f"Expected audit log at {audit_file}"
    # Read last line and ensure it's valid JSON with risk_score > 0
    with open(audit_file, "r", encoding="utf-8") as fh:
        lines = [l.strip() for l in fh.readlines() if l.strip()]
    assert len(lines) >= 1
    data = json.loads(lines[-1])
    assert data["risk_score"] > 0
    assert data["cmd"].startswith("rm -rf")
