from providers.local_adapter import LocalAdapter
from providers.subprocess_adapter import SubprocessAdapter
import hitl_multitask as hm


def test_prepare_prompts_and_adapter_mock(tmp_path):
    # prepare dummy task and config
    task = {"goal": "g", "context": "c", "slice_id": "slice_a"}
    config = {"provider": "mock", "model": "m"}
    prompts, vars, adapter = hm._prepare_prompts_and_adapter(task, config, provider_override="mock")
    assert isinstance(adapter, LocalAdapter)


def test_prepare_prompts_and_adapter_subprocess(tmp_path):
    task = {"goal": "g", "context": "c", "slice_id": "slice_a"}
    config = {"provider": "subprocess", "model": "m"}
    prompts, vars, adapter = hm._prepare_prompts_and_adapter(task, config, provider_override="subprocess")
    assert isinstance(adapter, SubprocessAdapter)
