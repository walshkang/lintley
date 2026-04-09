import uuid
from datetime import datetime
from typing import Dict

from agents_orchestrator import EnhancedRunner as DemoRunner

# Tunable constants
MAX_SMALL_SIZE = 400
MAX_EXCERPT_LINES = 200


class Planner:
    """Simple Planner prototype.

    - Splits context_files into slices (one per file)
    - Chooses agents per slice based on model_hint and simple heuristics
    - Can dispatch a plan to a provider using DemoRunner (Actor->Observer->Patch)
    """

    DEFAULT_AGENTS = [
        "SliceActor",
        "SliceObserver",
        "PatchAgent",
        "TestAgent",
    ]

    def plan(
        self,
        task: str,
        context_files: Dict[str, str],
        model_hint: str = "balanced",
        concurrency_limit: int = 4,
    ) -> Dict:
        run_id = str(uuid.uuid4())[:8]
        ts = datetime.utcnow().isoformat() + "Z"

        # Simple split: one slice per file
        slices = []
        for i, (path, content) in enumerate(context_files.items(), start=1):
            slice_id = f"s{i:03}"
            # choose effort based on model_hint and file size
            size = len(content.splitlines())
            if model_hint == "fast":
                effort = "low"
                agents = ["SliceActor", "PatchAgent"]
            elif model_hint == "powerful":
                effort = "high"
                agents = self.DEFAULT_AGENTS
            else:
                # balanced
                effort = "medium" if size < MAX_SMALL_SIZE else "high"
                agents = self.DEFAULT_AGENTS if effort != "low" else ["SliceActor", "PatchAgent"]

            slices.append(
                {
                    "slice_id": slice_id,
                    "path": path,
                    "files": [path],
                    "context_excerpt": "\n".join(content.splitlines()[:MAX_EXCERPT_LINES]),
                    "agents": agents,
                    "effort": effort,
                    "metadata": {"size_lines": size},
                }
            )

        model_map = {"actor": "gpt-5-mini", "observer": "gpt-5-mini"}

        plan = {
            "run_id": run_id,
            "task": task,
            "slices": slices,
            "model_hint": model_hint,
            "model_map": model_map,
            "concurrency_limit": concurrency_limit,
            "created_at": ts,
        }
        return plan

    def dispatch(self, plan: Dict, provider) -> None:
        """Dispatch the Actor->Observer->Patch flow for each slice using DemoRunner.

        This uses EnhancedRunner.run_plan_parallel to execute slices concurrently up to
        the configured concurrency_limit.
        """
        runner = DemoRunner(provider)
        concurrency = plan.get("concurrency_limit", 4)
        runner.run_plan_parallel(plan, concurrency_limit=concurrency)
