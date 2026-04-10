"""Timeline integration PoC for Copilot agent timelines.
Provides helpers to detect whether a shell command was proposed by an agent and
extract the agent's chain-of-thought / reasoning for display alongside guardrails warnings.
"""
from typing import List, Dict, Any, Optional


def find_agent_events(timeline: List[Dict[str, Any]], agent_name: Optional[str] = None) -> List[Dict[str, Any]]:
    """Return timeline events that appear to originate from an agent.

    Heuristics: event.get('source') == 'agent' or 'agent' in actor string.
    """
    events = []
    for ev in timeline:
        actor = ev.get("actor", "")
        source = ev.get("source", "")
        if source == "agent" or (isinstance(actor, str) and "agent" in actor.lower()):
            if agent_name is None or agent_name.lower() in actor.lower():
                events.append(ev)
    return events


def annotate_command(cmd: str, timeline: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Annotate a command with any matching agent events from the timeline.

    Returns a dict with keys:
      - cmd: original command
      - matched_events: list of events that mention/produce the command
      - cot: concatenated chain-of-thought strings (if any)
    """
    matched = []
    cots: List[str] = []
    for ev in find_agent_events(timeline):
        # look for explicit command field or text that contains the command
        ev_cmd = ev.get("command") or ev.get("text") or ev.get("content") or ""
        if isinstance(ev_cmd, list):
            ev_cmd = " ".join(ev_cmd)
        if ev_cmd and cmd.strip() and cmd.strip() in str(ev_cmd):
            matched.append(ev)
            cot = ev.get("chain_of_thought") or ev.get("cot") or ev.get("reasoning") or ev.get("analysis")
            if cot:
                cots.append(str(cot))
    return {"cmd": cmd, "matched_events": matched, "cot": "\n---\n".join(cots) if cots else ""}


# Utility: pretty-print annotation for CLI display
def format_annotation(annotation: Dict[str, Any]) -> str:
    parts = [f"Command: {annotation.get('cmd')}"]
    if annotation.get("matched_events"):
        parts.append(f"Matched {len(annotation['matched_events'])} agent event(s)")
    if annotation.get("cot"):
        parts.append("Chain-of-thought:\n" + annotation["cot"])
    return "\n\n".join(parts)
