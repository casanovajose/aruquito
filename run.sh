#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

if [[ ! -f ".venv/Scripts/activate" ]]; then
  echo "Virtual environment not found at .venv"
  echo "Create it with: python -m venv .venv"
  exit 1
fi

# shellcheck disable=SC1091
source ".venv/Scripts/activate"

exec python app/main.py "$@"
