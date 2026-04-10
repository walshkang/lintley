import os
import json
from pathlib import Path
from typing import Optional


def repo_root() -> str:
    # Assume this file is in <repo>/guardrails/
    return str(Path(__file__).resolve().parent.parent)


def default_audit_path() -> str:
    return os.path.join(repo_root(), ".guardrails", "audit.log")


def ensure_audit_dir(path: Optional[str] = None) -> str:
    path = path or default_audit_path()
    d = os.path.dirname(path)
    os.makedirs(d, exist_ok=True)
    return path


def load_config(path: Optional[str] = None) -> dict:
    # Future: read JSON/YAML configuration for rules and thresholds
    # For PoC return minimal config
    cfg = {
        "audit_path": default_audit_path(),
        "block_threshold": 0
    }
    if path and os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as fh:
                user_cfg = json.load(fh)
                cfg.update(user_cfg)
        except Exception:
            pass
    return cfg
