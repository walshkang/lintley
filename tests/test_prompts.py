from prompts.loader import load_prompts, render_prompt


def test_slice_a_prompts_render():
    prompts = load_prompts("slice_a")
    vars = {"goal": "Refactor helper for readability", "context": "def foo(x): return x*2", "slice_id": "slice_a"}
    for _k, t in prompts.items():
        out = render_prompt(t, vars)
        # basic sanity checks
        assert isinstance(out, str)
        # Only user-facing templates should include the goal
        if "user" in _k or "actor_user" in _k or "observer_user" in _k:
            assert vars["goal"] in out
        assert "run:" not in out.lower()
        assert "$" not in out
