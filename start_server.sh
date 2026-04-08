#!/bin/bash
# Shell script to start the server with web interface enabled
cd "$(dirname "$0")"
export ENABLE_WEB_INTERFACE=true
python -m uvicorn server.app:app --host 0.0.0.0 --port 8000
