#!/usr/bin/env python3
"""Enhanced orchestrator that runs agent pipelines per slice in parallel.
"""
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List

from prompts.loader import load_prompts
from utils.safety import sanitize_user_input, redact_secrets, validate_agent_output

PROMPTS = load_prompts()


class EnhancedRunner:
    def __init__(self, provider):
        self.provider = provider

    def _emit(self, event: str, task: str, slice_id: str, payload: Dict[str, Any]):
        envelope = {
            "event": event,
            "task": task,
            "slice_id": slice_id,
            "payload": payload,
            "meta": {"agent": event, "model": getattr(self.provider, "model", "mock"), "ts": time.time()},
        }
        print(json.dumps(envelope, ensure_ascii=False))

    def _format_prompt(self, key: str, **kwargs) -> (str, str):
        p = PROMPTS.get(key, {})
        system = p.get("system", "")
        template = p.get("user_template", "")
        # sanitize and escape values to avoid format injection
        safe_kwargs = {}
        for k, v in kwargs.items():
            val = "" if v is None else str(v)
            val = sanitize_user_input(val)
            # escape braces so .format can't be abused by user values
            val = val.replace("{", "{{").replace("}", "}}")
            safe_kwargs[k] = val
        try:
            user = template.format(**safe_kwargs)
        except Exception:
            user = ""
        return system, user

    def run_slice(self, plan_task: str, slice_def: Dict[str, Any]):
        """Run the agent pipeline for a single slice synchronously.

        Expected slice_def has: slice_id, path, context_excerpt, agents (list)
        """
        slice_id = slice_def.get("slice_id")
        context = slice_def.get("context_excerpt", "")

        # Actor
        actor_system, actor_user = self._format_prompt(
            "slice_actor",
            task=plan_task,
            slice_id=slice_id,
            context=context,
            constraints="do not edit tests or docs",
        )
        actor_raw = self.provider.generate(actor_system, actor_user)
        try:
            actor_payload = json.loads(actor_raw)
            ok, errors = validate_agent_output('actor', actor_payload)
            if not ok:
                self._emit('schema_failure', plan_task, slice_id, {'agent': 'actor', 'errors': errors})
                actor_payload = {
                    "analysis": actor_payload.get("analysis", "")
                    if isinstance(actor_payload, dict)
                    else "",
                    "patch": "",
                    "instructions": "",
                    "confidence": "low",
                }
            else:
                actor_payload = {
                    k: redact_secrets(v) if isinstance(v, str) else v
                    for k, v in actor_payload.items()
                }
        except Exception:
            actor_payload = {
                "analysis": actor_raw,
                "patch": "",
                "instructions": "",
                "confidence": "low",
            }
        self._emit("actor_proposal", plan_task, slice_id, actor_payload)
        time.sleep(0.01)

        # Observer
        if "SliceObserver" in slice_def.get("agents", []):
            obs_system, obs_user = self._format_prompt(
                "slice_observer",
                actor_analysis=actor_payload.get("analysis", ""),
                patch=actor_payload.get("patch", ""),
                slice_id=slice_id,
            )
            obs_raw = self.provider.generate(obs_system, obs_user)
            try:
                obs_payload = json.loads(obs_raw)
                ok, errors = validate_agent_output('observer', obs_payload)
                if not ok:
                    self._emit('schema_failure', plan_task, slice_id, {'agent': 'observer', 'errors': errors})
                    obs_payload = {
                        "verdict": "CAUTION",
                        "findings": [],
                        "risk_level": "medium",
                        "recommended_changes": "",
                    }
                else:
                    obs_payload = {
                        k: redact_secrets(v) if isinstance(v, str) else v
                        for k, v in obs_payload.items()
                    }
            except Exception:
                obs_payload = {
                    "verdict": "CAUTION",
                    "findings": [],
                    "risk_level": "medium",
                    "recommended_changes": "",
                }
            self._emit("observer_audit", plan_task, slice_id, obs_payload)
            time.sleep(0.01)

        # PatchAgent
        if "PatchAgent" in slice_def.get("agents", []):
            patch = actor_payload.get("patch", "") or ""
            applies = bool(patch.strip())
            normalized = patch
            errors = []
            if not applies:
                errors.append("no-patch-provided")
            patch_payload = {"applies": applies, "errors": errors, "normalized_patch": normalized}
            self._emit("patch_ready", plan_task, slice_id, patch_payload)
            time.sleep(0.01)

        # TestAgent
        if "TestAgent" in slice_def.get("agents", []):
            test_system, test_user = self._format_prompt("test_agent", slice_id=slice_id, test_command="pytest -q", timeout=120)
            test_raw = self.provider.generate(test_system, test_user)
            try:
                test_payload = json.loads(test_raw)
                ok, errors = validate_agent_output('test', test_payload)
                if not ok:
                    self._emit('schema_failure', plan_task, slice_id, {'agent': 'test', 'errors': errors})
                    test_payload = {
                    "total": 0,
                    "passed": 0,
                    "failed": 0,
                    "failures": [],
                }
                else:
                    test_payload = {
                        k: redact_secrets(v) if isinstance(v, str) else v
                        for k, v in test_payload.items()
                    }
            except Exception:
                test_payload = {
                    "total": 0,
                    "passed": 0,
                    "failed": 0,
                    "failures": [],
                }
            self._emit("test_results", plan_task, slice_id, test_payload)
            time.sleep(0.01)

        # GitAgent
        if "GitAgent" in slice_def.get("agents", []):
            git_system, git_user = self._format_prompt("git_agent", slice_id=slice_id, normalized_patch=normalized, commit_message=f"Update {slice_id}", push=False)
            # GitAgent is offline (no provider call) in this prototype; emit safe steps
            git_payload = {
                "branch": f"lintley/{slice_id}",
                "commands": [f"git checkout -b lintley/{slice_id}", "git apply patch", "pytest -q"],
                "rollback": ["git reset --hard HEAD~1"],
            }
            self._emit("git_steps", plan_task, slice_id, git_payload)
            time.sleep(0.01)

        return True

    def run_plan_parallel(self, plan: Dict, concurrency_limit: int = 4):
        slices = plan.get("slices", [])
        task = plan.get("task")
        results = []
        with ThreadPoolExecutor(max_workers=concurrency_limit) as ex:
            futures = {ex.submit(self.run_slice, task, s): s for s in slices}
            for fut in as_completed(futures):
                try:
                    res = fut.result()
                    results.append(res)
                except Exception as e:
                    # emit error event
                    s = futures[fut]
                    self._emit(
                        "slice_error",
                        task,
                        s.get("slice_id"),
                        {"error": str(e)},
                    )
        return results
