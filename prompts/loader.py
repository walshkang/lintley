import json
from pathlib import Path

PROMPTS_DIR = Path(__file__).parent


def load_prompts() -> dict:
    prompts = {}
    for p in PROMPTS_DIR.glob('*.json'):
        if p.name == 'loader.py':
            continue
        try:
            with open(p) as f:
                prompts[p.stem] = json.load(f)
        except Exception:
            prompts[p.stem] = {"system": "", "user_template": ""}
    return prompts
