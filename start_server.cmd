@echo off
REM Batch script to start the server with web interface enabled
cd C:\code\openenv
set ENABLE_WEB_INTERFACE=true
python -m uvicorn server.app:app --host 0.0.0.0 --port 8000
