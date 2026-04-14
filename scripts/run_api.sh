#!/bin/bash
set -euo pipefail

# Run the main FastAPI service used by Travelbook.
# Supports optional .venv activation and standard uvicorn startup.

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

if [ -d ".venv" ]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

HOST="${API_HOST:-0.0.0.0}"
PORT="${API_PORT:-8000}"

exec uvicorn main:app --host "$HOST" --port "$PORT"
