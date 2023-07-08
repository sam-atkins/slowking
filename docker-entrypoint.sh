#!/bin/bash

set -e
source /opt/setup/.venv/bin/activate

usage() {
    echo "Usage: $0 [api|event-consumer]"
    echo "  - api: start the fastapi server and eventbus"
    echo "  - event-consumer: run db migrations, start redis event consumer (pub/sub)"
}

if [[ "$1" == "event-consumer" ]]; then
    python db_ready.py
    alembic upgrade head
    watchmedo auto-restart --directory=/home/app/slowking --pattern="*.py" -- python -m slowking.entrypoints.event_consumer
elif [[ "$1" == "api" ]]; then
    uvicorn slowking.router:app --host 0.0.0.0 --reload --port 8091
else
    echo "Unknown or missing sub-command: '$1'"
    usage
    exit 1
fi
