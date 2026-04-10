#!/usr/bin/env bash
# Installer helper: prints instructions to source the guarded hook in your shell
set -euo pipefail
REPO_ROOT=$(cd "$(dirname "$0")/.." && pwd)
HOOK_LINE="source $REPO_ROOT/scripts/guarded_hook.sh"

cat <<'EOF'
To enable the guarded shell helpers, add the following line to your shell rc file (e.g. ~/.bashrc or ~/.zshrc):

EOF
printf "    %s\n\n" "$HOOK_LINE"
cat <<'EOF'
After adding, reload your shell (source ~/.bashrc) or open a new terminal.
You can then use:
  guard <command>     # inspect, confirm, and run
  enable_guard_alias  # create 'run' alias as shorthand

This installer will NOT modify your shell files automatically. Copy the line above into your rc file when ready.
EOF
