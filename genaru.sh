#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

# Activate venv same as app
if [[ ! -f ".venv/Scripts/activate" ]]; then
  echo "Virtual environment not found at .venv"
  echo "Create it with: python -m venv .venv"
  exit 1
fi

source ".venv/Scripts/activate"

# Parse arguments and convert to Python flags
python_args=""
for arg in "$@"; do
  case $arg in
    id=*) python_args="$python_args --id ${arg#id=}" ;;
    copies=*) python_args="$python_args --copies ${arg#copies=}" ;;
    s=*) python_args="$python_args --size ${arg#s=}" ;;
  esac
done

# Run Python generator
python genaru.py $python_args
