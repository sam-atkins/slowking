#!/bin/bash

set -e
source /opt/setup/.venv/bin/activate

uvicorn src.main:app --host 0.0.0.0 --reload --port 8283
