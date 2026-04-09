Formatting and linting

To ensure a consistent code style, use the included script to run Black and Ruff in an isolated virtualenv.

Local formatting (recommended):

    ./scripts/format.sh

This will:
- create a virtualenv in .venv-format
- install Black, Ruff, and Jinja2
- run Black .
- run ruff check . --fix

Note: On macOS System Python, use the script (it creates the venv) rather than pip --user.

CI note: The repository's GitHub Actions run `ruff check .`, `black --check .`, and `pytest -q`. Format locally and push formatted files to avoid CI failures.