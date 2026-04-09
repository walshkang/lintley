import json

import hitl_multitask as hm


def test_submit_and_execute_workflow(tmp_path):
    # Isolate state dir to tmp_path
    state_dir = tmp_path / ".hitl_state"
    hm.STATE_DIR = state_dir
    hm.CONFIG_FILE = state_dir / "config.json"
    hm.TASKS_DIR = state_dir / "tasks"

    # Prepare config so run_workflow_cmd doesn't exit
    hm.save_config({"provider": "mock", "api_key": "", "model": "mock-model"})

    # Create a sample task definition file
    task_def = {
        "title": "Sample: Change greeting",
        "goal": "Update greeting text",
        "context": "file: hello.txt\ncontent: Hello World",
        "model_hint": "balanced",
    }
    task_file = tmp_path / "task.json"
    with task_file.open("w", encoding="utf-8") as fh:
        json.dump(task_def, fh)

    # Submit task (creates state)
    hm.submit_cmd(str(task_file))

    # There should be one task file in TASKS_DIR
    tasks = list(hm.TASKS_DIR.glob("*.json"))
    assert len(tasks) == 1

    task_id = tasks[0].stem

    # Execute workflow
    hm.run_workflow_cmd(task_id)

    # Load task and assert actor/observer populated
    task_state = hm.load_task(task_id)
    assert task_state is not None
    assert task_state["status"] == "pending_approval"
    assert isinstance(task_state["actor_work"], dict)
    assert "analysis" in task_state["actor_work"]
    assert isinstance(task_state["observer_review"], dict)
    assert "verdict" in task_state["observer_review"]
    assert task_state["risk_level"] in ("low", "medium", "high")
