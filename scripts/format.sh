#!/usr/bin/env bash
set -euo pipefail

# Creates an isolated venv and runs Black + Ruff to format and lint the repo.
# Use this locally when your system Python forbids --user installs.

VENV_DIR=".venv-format"
python3 -m venv "$VENV_DIR"
# shellcheck disable=SC1091
. "$VENV_DIR/bin/activate"

pip install --upgrade pip
pip install black ruff jinja2

black .
ruff check . --fix

echo "Formatting complete. Review changes and commit."
