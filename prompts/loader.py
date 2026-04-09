import json
from pathlib import Path
from typing import Any, Dict

from utils.safety import sanitize_user_input

PROMPTS_DIR = Path(__file__).resolve().parent

# Optional Jinja2 usage: if available, use a sandboxed environment for safer
# templating. If not installed, fall back to simple format_map rendering so CI
# remains dependency-free.
try:
    from jinja2.sandbox import SandboxedEnvironment
    from jinja2 import StrictUndefined

    _JINJA_AVAILABLE = True
    _JINJA_ENV = SandboxedEnvironment(undefined=StrictUndefined, autoescape=False)
except Exception:
    _JINJA_AVAILABLE = False
    _JINJA_ENV = None


class _Missing(dict):
    def __missing__(self, key):
        return "{" + key + "}"


def load_prompts(slice_id: str) -> Dict[str, str]:
    """Load prompt templates for a given slice id from prompts/{slice_id}.json."""
    p = PROMPTS_DIR / f"{slice_id}.json"
    if not p.exists():
        raise FileNotFoundError(f"Prompt file not found: {p}")
    with p.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def render_prompt(template: str, variables: Dict[str, Any]) -> str:
    """Render a template with sanitized variables.

    If Jinja2 is installed, use a sandboxed environment with StrictUndefined to
    avoid accidental evaluation and to catch missing variables. Values are
    sanitized via utils.safety.sanitize_user_input to reduce prompt-injection
    surface. If Jinja2 isn't available, fall back to safe format_map.
    """
    safe_vars = {k: sanitize_user_input(str(v)) for k, v in variables.items()}
    # Use Jinja2 only when the template appears to use Jinja syntax ({{ }} or {% %})
    if _JINJA_AVAILABLE and _JINJA_ENV is not None and ("{{" in template or "{%" in template):
        try:
            tmpl = _JINJA_ENV.from_string(template)
            return tmpl.render(**safe_vars)
        except Exception:
            # Fall back to simple format if templating fails
            return template.format_map(_Missing(**safe_vars))
    # Default fallback: python format_map to preserve existing {var} templates
    return template.format_map(_Missing(**safe_vars))


def list_available() -> list:
    return [p.stem for p in PROMPTS_DIR.glob("*.json")]
