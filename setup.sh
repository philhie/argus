#!/usr/bin/env bash
#
# ARGUS one-command setup.
#
#   ./setup.sh
#
# Creates a virtual environment, installs Argus with all dependencies,
# and prepares your .env file. Safe to re-run — it reuses an existing
# .venv and never overwrites an existing .env.

set -euo pipefail

# Always run from the repo root (the directory this script lives in),
# so it works no matter where it's invoked from.
cd "$(dirname "$0")"

say()  { printf '\033[1;36m==>\033[0m %s\n' "$1"; }
fail() { printf '\033[1;31mERROR:\033[0m %s\n' "$1" >&2; exit 1; }

say "ARGUS setup starting"

# 1. Find a usable Python (>=3.9). Prefer the newest available so we avoid
#    the LibreSSL warning that ships with the macOS system Python 3.9.
PYTHON=""
for candidate in python3.13 python3.12 python3.11 python3.10 python3.9 python3 python; do
    if command -v "$candidate" >/dev/null 2>&1; then
        PYTHON="$candidate"
        break
    fi
done
[ -n "$PYTHON" ] || fail "No Python found. Install Python 3.9+ first (on macOS: 'brew install python')."

# Enforce the >=3.9 floor from pyproject.toml.
if ! "$PYTHON" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)'; then
    have="$("$PYTHON" -c 'import sys; print("%d.%d" % sys.version_info[:2])')"
    fail "Found Python $have but Argus needs 3.9 or newer. Install a newer Python (on macOS: 'brew install python')."
fi
say "Using $PYTHON ($("$PYTHON" -c 'import platform; print(platform.python_version())'))"

# 2. Create the virtual environment (reuse if present).
if [ -d .venv ]; then
    say ".venv already exists — reusing it"
else
    say "Creating virtual environment in .venv"
    "$PYTHON" -m venv .venv
fi

VENV_PY=".venv/bin/python"
[ -x "$VENV_PY" ] || fail "Virtual environment looks broken (no $VENV_PY). Delete .venv and re-run."

# 3. Upgrade pip FIRST. The pip bundled with the macOS system Python (21.x)
#    is too old to do an editable install of a pyproject.toml-only project,
#    and fails with 'setup.py not found'. This is the step the manual
#    instructions used to miss.
say "Upgrading pip"
"$VENV_PY" -m pip install --upgrade pip

# 4. Install Argus + all optional + dev dependencies.
say "Installing Argus and dependencies (this can take a minute)"
"$VENV_PY" -m pip install -e ".[all,dev]"

# 5. Create .env from the template only if it doesn't already exist,
#    so we never clobber keys you've already filled in.
if [ -f .env ]; then
    say ".env already exists — leaving it untouched"
else
    say "Creating .env from .env.example"
    cp .env.example .env
fi

# 6. Smoke-test the CLI so a broken install fails here, not later.
say "Verifying the CLI runs"
"$VENV_PY" -m argus --help >/dev/null 2>&1 || fail "Argus installed but 'python -m argus' failed to run. Re-run with '.venv/bin/python -m argus --help' to see the error."

printf '\n\033[1;32m%s\033[0m\n' '================================================================'
printf '\033[1;32m%s\033[0m\n'   ' ARGUS is ready.'
printf '\033[1;32m%s\033[0m\n\n' '================================================================'

cat <<'EOF'
Next steps:

  1. (Optional) Add API keys to .env. All keys are optional —
     modules that need a missing key just skip themselves.

  2. Activate the environment:

       source .venv/bin/activate

  3. Run a scan:

       python -m argus scan --domain example.com --company "Example GmbH"

Prefer not to activate? Prefix commands with .venv/bin/python instead:

       .venv/bin/python -m argus scan --domain example.com --company "Example GmbH"

EOF
