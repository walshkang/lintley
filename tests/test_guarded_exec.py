import subprocess
import json


def run_script(args):
    p = subprocess.run(["./scripts/guarded_exec"] + args, capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


def test_benign_no_execute():
    rc, out, err = run_script(["echo", "hello"])
    assert rc == 0
    data = json.loads(out)
    assert data["risk_score"] == 0


def test_risky_no_execute():
    # Risky command should be detected and return non-zero (2) without --yes
    rc, out, err = run_script(["rm", "-rf", "/tmp/some_nonexistent_path_for_test"])
    assert rc == 2
    # The script prints JSON then prompts; parse only the JSON portion before the prompt
    json_part = out.split("Risk detected. Proceed?")[0].strip()
    data = json.loads(json_part)
    assert data["risk_score"] > 0
