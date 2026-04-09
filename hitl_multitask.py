#!/usr/bin/env python3
"""
Generic Multi-Task Actor-Observer-HITL System

A collaborative agent framework for parallel task execution with human-in-the-loop checkpoints.
Supports multiple LLM providers (Anthropic, Google, OpenAI).

Usage:
  python3 hitl_multitask.py setup              # Configure API key once
  python3 hitl_multitask.py submit <task.json> # Start a workflow
  python3 hitl_multitask.py status             # Show all tasks
  python3 hitl_multitask.py approve <task_id>  # Approve a task
  python3 hitl_multitask.py dashboard          # Monitor in real-time
"""

import json
import os
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import TypedDict, Optional

# Configuration constants
GOOGLE_KEY_LENGTH = 100
MIN_ARG_COUNT = 2

# State directory
STATE_DIR = Path(".hitl_state")
CONFIG_FILE = STATE_DIR / "config.json"
TASKS_DIR = STATE_DIR / "tasks"


class TaskDefinition(TypedDict):
    """User-provided task definition."""

    id: str
    title: str
    goal: str
    context: str
    model_hint: Optional[str]  # "fast", "balanced", "powerful"


class TaskState(TypedDict):
    """Internal task state."""

    id: str
    title: str
    goal: str
    context: str
    status: str  # pending_actor, pending_approval, approved, rejected, completed
    actor_work: Optional[str]
    observer_review: Optional[str]
    risk_level: Optional[str]
    human_decision: Optional[str]
    created_at: str
    updated_at: str


def ensure_state_dir():
    """Create state directory structure."""
    STATE_DIR.mkdir(exist_ok=True)
    TASKS_DIR.mkdir(exist_ok=True)


def load_config() -> dict:
    """Load provider config."""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return {}


def save_config(config: dict):
    """Save provider config."""
    ensure_state_dir()
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


def setup_provider():  # noqa: C901, PLR0912, PLR0915
    """Configure provider from environment or interactively.

    Priority (non-interactive):
      1. Environment variables: HITL_PROVIDER, HITL_API_KEY, HITL_MODEL
      2. .env.local file with the same keys
    Falls back to the original interactive prompt if values are missing.
    """
    print("\n" + "=" * 80)
    print("🔧 PROVIDER SETUP")
    print("=" * 80)

    # Try environment variables first
    provider = os.environ.get("HITL_PROVIDER")
    api_key = os.environ.get("HITL_API_KEY")
    selected_model = os.environ.get("HITL_MODEL")

    # If any missing, try .env.local
    env_file = Path(".env.local")
    if env_file.exists():
        try:
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip('"').strip("'")
                    if k == "HITL_PROVIDER" and not provider:
                        provider = v
                    elif k == "HITL_API_KEY" and not api_key:
                        api_key = v
                    elif k == "HITL_MODEL" and not selected_model:
                        selected_model = v
        except Exception:
            pass

    # If we have an API key, try to detect provider if not provided
    if api_key and not provider:
        # best-effort detection
        if api_key.startswith("sk-ant-"):
            provider = "anthropic"
        elif api_key.startswith("sk-"):
            provider = "openai"
        elif api_key.startswith("AIza") or len(api_key) > GOOGLE_KEY_LENGTH:
            provider = "google"

    # If we have required info, save config non-interactively
    if api_key and provider:
        print(f"✅ Using provider from env/config: {provider.upper()}")
        config = {
            "provider": provider,
            "api_key": api_key,
            "model": selected_model or "",
            "saved_at": datetime.now().isoformat(),
        }
        save_config(config)
        print(f"✅ Config saved to {CONFIG_FILE}")
        return

    # Fallback: original interactive flow
    api_key = input("\n🔑 API Key (Anthropic/Google/OpenAI): ").strip()
    if not api_key:
        print("❌ No API key provided.")
        sys.exit(1)

    # Detect provider
    if api_key.startswith("sk-ant-"):
        provider = "anthropic"
    elif api_key.startswith("sk-"):
        provider = "openai"
    elif api_key.startswith("AIza") or len(api_key) > GOOGLE_KEY_LENGTH:
        provider = "google"
    else:
        print("⚠️  Could not auto-detect. Which provider?")
        print("  [1] Anthropic  [2] Google  [3] OpenAI")
        choice = {"1": "anthropic", "2": "google", "3": "openai"}.get(input("Choose: ").strip())
        if not choice:
            sys.exit(1)
        provider = choice

    print(f"✅ Provider: {provider.upper()}")

    config = {
        "provider": provider,
        "api_key": api_key,
        "saved_at": datetime.now().isoformat(),
    }
    save_config(config)
    print(f"✅ Config saved to {CONFIG_FILE}")


def create_task(task_def: TaskDefinition) -> str:
    """Create a new task. Returns task_id."""
    ensure_state_dir()

    task_id = task_def.get("id", str(uuid.uuid4())[:8])
    task_state: TaskState = {
        "id": task_id,
        "title": task_def["title"],
        "goal": task_def["goal"],
        "context": task_def["context"],
        "status": "pending_actor",
        "actor_work": None,
        "observer_review": None,
        "risk_level": None,
        "human_decision": None,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }

    task_file = TASKS_DIR / f"{task_id}.json"
    with open(task_file, "w") as f:
        json.dump(task_state, f, indent=2)

    print(f"✅ Task created: {task_id}")
    return task_id


def load_task(task_id: str) -> Optional[TaskState]:
    """Load a task from state."""
    task_file = TASKS_DIR / f"{task_id}.json"
    if task_file.exists():
        with open(task_file) as f:
            return json.load(f)
    return None


def save_task(task_state: TaskState):
    """Save task state."""
    task_state["updated_at"] = datetime.now().isoformat()
    task_file = TASKS_DIR / f"{task_state['id']}.json"
    with open(task_file, "w") as f:
        json.dump(task_state, f, indent=2)


def list_tasks() -> list[TaskState]:
    """List all tasks."""
    ensure_state_dir()
    tasks = []
    for task_file in sorted(TASKS_DIR.glob("*.json")):
        with open(task_file) as f:
            tasks.append(json.load(f))
    return tasks


def status_cmd():
    """Show all tasks and their status."""
    tasks = list_tasks()
    if not tasks:
        print("No tasks yet.")
        return

    print("\n" + "=" * 80)
    print("📊 TASK STATUS")
    print("=" * 80)

    for task in tasks:
        status_icon = {
            "pending_actor": "⏳",
            "pending_approval": "🚨",
            "approved": "✅",
            "rejected": "❌",
            "completed": "🎉",
        }.get(task["status"], "❓")

        print(f"\n{status_icon} {task['id']} — {task['title']}")
        print(f"   Status: {task['status']}")
        print(f"   Risk: {task['risk_level'] or 'N/A'}")
        print(f"   Created: {task['created_at']}")


def submit_cmd(task_file: str):
    """Submit a task definition file."""
    if not Path(task_file).exists():
        print(f"❌ File not found: {task_file}")
        sys.exit(1)

    with open(task_file) as f:
        task_def = json.load(f)

    task_id = create_task(task_def)
    print(f"\nRun: python3 hitl_multitask.py execute {task_id}")


def dashboard_cmd():
    """Real-time dashboard (polls every 5 seconds)."""
    print("\n" + "=" * 80)
    print("📡 HITL DASHBOARD (Ctrl+C to exit)")
    print("=" * 80)

    try:
        while True:
            tasks = list_tasks()
            pending_approval = [t for t in tasks if t["status"] == "pending_approval"]

            os.system("clear" if os.name != "nt" else "cls")
            print("\n" + "=" * 80)
            print("📡 HITL DASHBOARD")
            print("=" * 80)

            print("\n📈 Overview:")
            print(f"  Total tasks: {len(tasks)}")
            print(f"  Pending approval: {len(pending_approval)}")

            if pending_approval:
                print("\n🚨 Pending Approvals:")
                for i, t in enumerate(pending_approval, 1):
                    risk = t["risk_level"]
                    risk_icon = {
                        "high": "🔴",
                        "medium": "🟡",
                        "low": "🟢",
                    }.get(risk, "❓")
                    print(f"  [{i}] {t['id']} — {t['title']} {risk_icon}")

                print("\nApprove: python3 hitl_multitask.py approve <task_id>")
            else:
                print("\n✅ No pending approvals")

            print("\nLast updated: ", datetime.now().strftime("%H:%M:%S"))
            print("(Refreshes every 5 seconds)")

            import time

            time.sleep(5)
    except KeyboardInterrupt:
        print("\n\nDashboard closed.")


def approve_cmd(task_id: str, decision: str = "a"):
    """Approve/reject a task."""
    task = load_task(task_id)
    if not task:
        print(f"❌ Task not found: {task_id}")
        sys.exit(1)

    if task["status"] != "pending_approval":
        print(f"⚠️  Task is not pending approval (status: {task['status']})")
        sys.exit(1)

    if decision == "a":
        task["status"] = "approved"
        task["human_decision"] = "approved"
        print(f"✅ Task {task_id} APPROVED")
    elif decision == "r":
        task["status"] = "rejected"
        task["human_decision"] = "rejected"
        print(f"❌ Task {task_id} REJECTED")

    save_task(task)


def run_workflow_cmd(task_id: str):  # noqa: C901, PLR0915
    """Run Actor → Observer → HITL for a task.

    Loads prompt templates from prompts/, renders them safely, runs a local
    adapter (LocalAdapter) for deterministic behavior, validates outputs and
    saves them into task state.
    """
    from prompts.loader import load_prompts, render_prompt
    from providers.local_adapter import LocalAdapter
    from utils.safety import redact_secrets, validate_agent_output

    config = load_config()
    if not config:
        print("❌ Not configured. Run: python3 hitl_multitask.py setup")
        sys.exit(1)

    task = load_task(task_id)
    if not task:
        print(f"❌ Task not found: {task_id}")
        sys.exit(1)

    print("\n" + "=" * 80)
    print(f"🤖 WORKFLOW: {task['title']}")
    print("=" * 80)
    print(f"\nGoal: {task['goal']}")
    print(f"Context: {task['context'][:100]}...")

    # determine slice id (default to slice_a)
    slice_id = task.get("slice_id") or "slice_a"
    try:
        prompts = load_prompts(slice_id)
    except Exception:
        prompts = load_prompts("slice_a")

    vars = {"goal": task["goal"], "context": task["context"], "slice_id": slice_id}

    adapter = LocalAdapter(model=config.get("model") or None)

    # Run Actor
    print("\n⏳ Running Actor Agent...")
    actor_system = render_prompt(prompts.get("actor_system", ""), vars)
    actor_user = render_prompt(prompts.get("actor_user", ""), vars)
    try:
        raw_actor = adapter.generate(actor_system, actor_user)
        try:
            actor_payload = json.loads(raw_actor)
        except Exception:
            actor_payload = {
                "analysis": str(raw_actor),
                "patch": "",
                "instructions": "",
                "confidence": "low",
            }
        ok, errors = validate_agent_output("actor", actor_payload)
        if not ok:
            actor_payload.setdefault("confidence", "low")
            analysis = str(actor_payload.get("analysis", ""))
            actor_payload["analysis"] = (
                f"{analysis} (validation-issues: {','.join(errors)})"
            )
    except Exception as e:
        actor_payload = {"analysis": str(e), "patch": "", "instructions": "", "confidence": "low"}

    task["actor_work"] = actor_payload
    print("Actor result:")
    print(json.dumps(redact_secrets(actor_payload), indent=2))

    # Run Observer
    print("\n⏳ Running Observer Agent...")
    # include actor output in observer prompt for context
    obs_vars = dict(vars)
    obs_vars["actor_output"] = json.dumps(actor_payload)
    observer_system = render_prompt(prompts.get("observer_system", ""), obs_vars)
    observer_user = render_prompt(prompts.get("observer_user", ""), obs_vars)
    # append actor output if template doesn't include it
    if "actor_output" not in observer_user:
        observer_user = observer_user + "\n\nActorOutput: " + json.dumps(actor_payload)

    try:
        raw_obs = adapter.generate(observer_system, observer_user)
        try:
            obs_payload = json.loads(raw_obs)
        except Exception:
            obs_payload = {
                "verdict": "CAUTION",
                "findings": [],
                "risk_level": "medium",
                "recommended_changes": str(raw_obs),
            }
        ok2, errs2 = validate_agent_output("observer", obs_payload)
        if not ok2:
            obs_payload.setdefault("verdict", "CAUTION")
            obs_payload.setdefault("findings", []).append("validation-issues: " + ",".join(errs2))
    except Exception as e:
        obs_payload = {"verdict": "CAUTION", "findings": [str(e)], "risk_level": "medium", "recommended_changes": ""}

    task["observer_review"] = obs_payload
    task["risk_level"] = obs_payload.get("risk_level", "medium")
    task["status"] = "pending_approval"
    save_task(task)

    print("Observer result:")
    print(json.dumps(redact_secrets(obs_payload), indent=2))

    print(f"\n🚨 Awaiting approval. Run: python3 hitl_multitask.py approve {task_id}")


if __name__ == "__main__":
    if len(sys.argv) < MIN_ARG_COUNT:
        print(__doc__)
        sys.exit(0)

    cmd = sys.argv[1]

    if cmd == "setup":
        setup_provider()
    elif cmd == "submit" and len(sys.argv) > MIN_ARG_COUNT:
        submit_cmd(sys.argv[2])
    elif cmd == "status":
        status_cmd()
    elif cmd == "execute" and len(sys.argv) > MIN_ARG_COUNT:
        run_workflow_cmd(sys.argv[2])
    elif cmd == "approve" and len(sys.argv) > MIN_ARG_COUNT:
        approve_cmd(sys.argv[2], "a")
    elif cmd == "reject" and len(sys.argv) > MIN_ARG_COUNT:
        approve_cmd(sys.argv[2], "r")
    elif cmd == "dashboard":
        dashboard_cmd()
    else:
        print(__doc__)
