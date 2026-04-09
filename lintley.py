#!/usr/bin/env python3
"""CLI prototype for running Planner -> Orchestrator using MockProvider.

Usage examples:
  python3 lintley.py --task "Enable feature X" --files a.py b.py
  python3 lintley.py --task "Enable feature X" --files-json files.json

By default runs with MockProvider. Use --mock to force mock.
"""
import argparse
import json
from pathlib import Path

from planners.planner import Planner
from providers.mock_provider import MockProvider


def load_files(paths):
    files = {}
    for p in paths:
        path = Path(p)
        if path.exists():
            files[p] = path.read_text()
        else:
            # treat as literal small content
            files[p] = p
    return files


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", required=True)
    parser.add_argument("--files", nargs="*", help="List of files or small content snippets")
    parser.add_argument("--files-json", help="JSON file with map of path->content")
    parser.add_argument("--model-hint", default="balanced")
    parser.add_argument("--concurrency", type=int, default=4)
    parser.add_argument("--mock", action="store_true", default=True)
    args = parser.parse_args()

    if args.files_json:
        files = json.loads(Path(args.files_json).read_text())
    elif args.files:
        files = load_files(args.files)
    else:
        print("No files provided. Example: --files a.py b.py or --files-json map.json")
        return

    planner = Planner()
    plan = planner.plan(args.task, files, model_hint=args.model_hint, concurrency_limit=args.concurrency)
    print(json.dumps(plan, indent=2))

    provider = MockProvider()
    print("Running plan (mock provider) — events will be printed as JSON-lines:")
    planner.dispatch(plan, provider)


if __name__ == "__main__":
    main()
