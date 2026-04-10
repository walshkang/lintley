#!/usr/bin/env bash
# Guarded shell helpers (opt-in)
# Source this file in your shell to get a `guard` wrapper and helpers.
# Usage:
#   source scripts/guarded_hook.sh
#   guard rm -rf /tmp/something   # inspects, prompts, then executes if confirmed
#   enable_guard_alias            # creates alias 'run' -> 'guard'

guard() {
  if [ "$#" -eq 0 ]; then
    echo "Usage: guard <command> [args...]"
    return 1
  fi
  local cmd=("$@")

  # Run the guarded_exec inspector (non-executing) in repo context
  if [ -x "./scripts/guarded_exec" ]; then
    out=$(./scripts/guarded_exec -y -- "${cmd[@]}" 2>/dev/null || true)
    # Print the JSON report for visibility
    printf "%s\n" "$out"
    risk=$(printf "%s" "$out" | sed -n 's/.*"risk_score":[[:space:]]*\([0-9][0-9]*\).*/\1/p')
  else
    echo "Warning: ./scripts/guarded_exec not found or not executable; skipping analysis"
    risk=0
  fi

  if [ -n "$risk" ] && [ "$risk" -gt 0 ]; then
    printf "Guardrails: risky command detected (score=%s). Proceed? [y/N]: " "$risk"
    read -r resp
    if [[ "$resp" != "y" && "$resp" != "Y" ]]; then
      echo "Aborted by guard"
      return 2
    fi
  fi

  # Execute the command
  "${cmd[@]}"
  return $?
}

enable_guard_alias() {
  alias run='guard'
  echo "Alias 'run' -> 'guard' created; use 'run <cmd>' to inspect before executing."
}
