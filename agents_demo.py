#!/usr/bin/env python3
"""Simple in-process demo runner that executes Actor -> Observer -> PatchAgent
and emits JSON-lines events. Designed for red/green TDD with Mock/Fake providers.

Usage: python3 agents_demo.py
"""

import json
import time
from typing import Any, Dict

from prompts.loader import load_prompts

PROMPTS = load_prompts()


class DemoRunner:
    def __init__(self, provider):
        self.provider = provider

    def _emit(self, event: str, task: str, payload: Dict[str, Any]):
        envelope = {"event": event, "task": task, "payload": payload}
        print(json.dumps(envelope, ensure_ascii=False))

    def _format_prompt(self, key: str, **kwargs):
        p = PROMPTS.get(key, {})
        system = p.get("system", "")
        template = p.get("user_template", "")
        try:
            safe_kwargs = {k: (v if v is not None else "") for k, v in kwargs.items()}
            user = template.format(**safe_kwargs)
        except Exception:
            user = ""
        return system, user

    def run(self, task: str, context: str = "") -> None:
        # Actor
        actor_system, actor_user = self._format_prompt(
            "slice_actor",
            task=task,
            slice_id="demo",
            context=context,
            constraints="do not edit tests or docs",
        )
        actor_raw = self.provider.generate(actor_system, actor_user)
        try:
            actor_payload = json.loads(actor_raw)
        except Exception:
            actor_payload = {
                "analysis": actor_raw,
                "patch": "",
                "instructions": "",
                "confidence": "low",
            }

        self._emit("actor_proposal", task, actor_payload)
        time.sleep(0.01)

        # Observer
        obs_system, obs_user = self._format_prompt(
            "slice_observer",
            actor_analysis=actor_payload.get("analysis", ""),
            patch=actor_payload.get("patch", ""),
            slice_id="demo",
        )
        obs_raw = self.provider.generate(obs_system, obs_user)
        try:
            obs_payload = json.loads(obs_raw)
        except Exception:
            obs_payload = {
                "verdict": "CAUTION",
                "findings": [],
                "risk_level": "medium",
                "recommended_changes": "",
            }

        self._emit("observer_audit", task, obs_payload)
        time.sleep(0.01)

        # PatchAgent (validate/normalize)
        patch = actor_payload.get("patch", "") or ""
        applies = bool(patch.strip())
        normalized = patch
        errors = []
        if not applies:
            errors.append("no-patch-provided")

        patch_payload = {"applies": applies, "errors": errors, "normalized_patch": normalized}
        self._emit("patch_ready", task, patch_payload)


if __name__ == "__main__":
    # Demo FakeProvider for quick local runs
    class FakeProvider:
        def generate(self, system_prompt: str, user_message: str):
            if "Actor" in system_prompt or "SliceActor" in system_prompt:
                patch = (
                    "diff --git a/foo.txt b/foo.txt\n"
                    "--- a/foo.txt\n"
                    "+++ b/foo.txt\n"
                    "@@ -1 +1 @@\n"
                    "-old\n"
                    "+new\n"
                )
                return json.dumps(
                    {
                        "analysis": "Make a small change to foo.txt to fix behavior.",
                        "patch": patch,
                        "instructions": "Apply the patch and run tests.",
                        "confidence": "high",
                    }
                )
            if "Observer" in system_prompt or "SliceObserver" in system_prompt:
                return json.dumps(
                    {
                        "verdict": "PASS",
                        "findings": [],
                        "risk_level": "low",
                        "recommended_changes": "",
                    }
                )
            return "{}"

    runner = DemoRunner(FakeProvider())
    runner.run("Demo: update foo.txt")
