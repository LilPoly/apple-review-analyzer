#!/bin/sh
set -e

uv run python -m app.scripts.download_model

uv run alembic upgrade head

if [ "$RELOAD" = "true" ]; then
    exec uv run uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}" --reload
else
    exec uv run uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
fi
