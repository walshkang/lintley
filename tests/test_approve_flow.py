import json
from pathlib import Path

import hitl_multitask as hm


def _create_and_execute(state_tmp, title="Flow Test", goal="Do thing"):
    # configure state paths
    hm.STATE_DIR = state_tmp
    hm.CONFIG_FILE = state_tmp / "config.json"
    hm.TASKS_DIR = state_tmp / "tasks"

    hm.save_config({"provider": "mock", "api_key": "", "model": "mock-model"})

    task_def = {"title": title, "goal": goal, "context": "ctx", "model_hint": "balanced"}
    task_file = state_tmp / "task.json"
    with task_file.open("w", encoding="utf-8") as fh:
        json.dump(task_def, fh)

    hm.submit_cmd(str(task_file))
    tasks = list(hm.TASKS_DIR.glob("*.json"))
    assert len(tasks) == 1
    task_id = tasks[0].stem
    hm.run_workflow_cmd(task_id)
    return task_id


def test_approve_flow(tmp_path):
    state_tmp = tmp_path / ".hitl_state"
    state_tmp.mkdir(parents=True)

    task_id = _create_and_execute(state_tmp)

    # now approve
    hm.approve_cmd(task_id, "a")
    task = hm.load_task(task_id)
    assert task is not None
    assert task["status"] == "approved"
    assert task["human_decision"] == "approved"


def test_reject_flow(tmp_path):
    state_tmp = tmp_path / ".hitl_state2"
    state_tmp.mkdir(parents=True)

    task_id = _create_and_execute(state_tmp, title="Reject Test", goal="Do other thing")

    # reject
    hm.approve_cmd(task_id, "r")
    task = hm.load_task(task_id)
    assert task is not None
    assert task["status"] == "rejected"
    assert task["human_decision"] == "rejected"
