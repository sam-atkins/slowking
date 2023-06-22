#!/bin/bash

set -e
source /opt/setup/.venv/bin/activate

usage() {
    echo "Usage: $0 [eventbus|api]"
    echo "  - api: start the fastapi server and eventbus"
    echo "  - event-consumer: start redis event consumer (pub/sub)"
}

if [[ "$1" == "event-consumer" ]]; then
    # tail -f /dev/null
    watchmedo auto-restart --directory=/home/app/src --pattern="*.py" -- python -m src.entrypoints.event_consumer
elif [[ "$1" == "api" ]]; then
    uvicorn src.entrypoints.api:app --host 0.0.0.0 --reload --port 8080
else
    echo "Unknown or missing sub-command: '$1'"
    usage
    exit 1
fi
