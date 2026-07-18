#!/bin/zsh

set -euo pipefail

export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"

echo "======================================"
echo "       JobHunter Launcher"
echo "======================================"
echo

echo "[1/5] Checking Docker installation..."

if ! command -v docker >/dev/null 2>&1; then
    echo "ERROR: Docker CLI not found."
    exit 1
fi

echo "✓ Docker CLI found."
echo

echo "[2/5] Starting Docker Desktop..."

if ! docker info >/dev/null 2>&1; then
    open -g -a Docker
fi

echo "Waiting for Docker daemon..."

attempt=0
max_attempts=60

until docker info >/dev/null 2>&1
do
    sleep 2
    attempt=$((attempt + 1))

    printf "\rWaiting... %d/%d" "$attempt" "$max_attempts"

    if [ "$attempt" -ge "$max_attempts" ]; then
        echo
        echo "ERROR: Docker failed to start within 120 seconds."
        exit 1
    fi
done

echo
echo "✓ Docker is ready."
echo

echo "[3/5] Starting JobHunter container..."

if docker ps --format '{{.Names}}' | grep -qx "job-hunter-ai"; then
    echo "✓ Container already running."
else
    docker start job-hunter-ai >/dev/null
    echo "✓ Container started."
fi

echo

echo "[4/5] Checking FastAPI..."

if pgrep -f "uvicorn app.main:app" >/dev/null; then
    echo "✓ FastAPI already running."
else

    cd /Users/rajputana.sam/Documents/JobHunter/search-scraper

    nohup zsh -c '
        source venv/bin/activate
        exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    ' >/tmp/jobhunter_fastapi.log 2>&1 &

    sleep 3

    if pgrep -f "uvicorn app.main:app" >/dev/null; then
        echo "✓ FastAPI started."
    else
        echo
        echo "ERROR: FastAPI failed to start."
        echo
        echo "Check the log:"
        echo "/tmp/jobhunter_fastapi.log"
        exit 1
    fi
fi

echo

echo "[5/5] JobHunter is ready."

echo
echo "======================================"
echo " Launch completed successfully."
echo "======================================" 