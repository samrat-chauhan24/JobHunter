#!/bin/zsh

export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"

echo "======================================"
echo "      Stopping JobHunter"
echo "======================================"
echo

echo "[1/3] Stopping FastAPI..."

pkill -f "uvicorn app.main:app" || true

echo "✓ FastAPI stopped."
echo


echo

echo "[2/3] Stopping JobHunter container..."

docker stop job-hunter-ai >/dev/null 2>&1 || true

echo "✓ Container stopped."
echo

echo "[3/3] Stopping Docker Desktop..."x

docker desktop stop

echo
echo "======================================"
echo " JobHunter stopped successfully."
echo "======================================"