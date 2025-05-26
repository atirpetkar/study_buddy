#!/bin/bash

# Start Study Buddy Backend and Frontend

# Default port configuration
PORT=8000
ALTERNATIVE_PORT=8080
USE_ALTERNATIVE_PORT=0

# Process command line options
while getopts "ap:" opt; do
  case $opt in
    a) USE_ALTERNATIVE_PORT=1 ;;
    p) PORT=$OPTARG ;;
    \?) echo "Invalid option: -$OPTARG" >&2; exit 1 ;;
  esac
done

if [ $USE_ALTERNATIVE_PORT -eq 1 ]; then
    PORT=$ALTERNATIVE_PORT
    echo "Using alternative port: $PORT"
fi

echo "Stopping any existing Study Buddy services..."
# Kill any running uvicorn (backend) processes
pkill -f "uvicorn main:app" 2>/dev/null || true
# Kill any running npm dev (frontend) processes
pkill -f "npm run dev" 2>/dev/null || true

# More aggressively check for processes using port 8000
BACKEND_PROCESS=$(lsof -i:$PORT -t 2>/dev/null)
if [ -n "$BACKEND_PROCESS" ]; then
    echo "Process(es) still using port $PORT. Attempting to terminate..."
    kill -9 $BACKEND_PROCESS 2>/dev/null
    sleep 2
    # Check again
    BACKEND_PROCESS=$(lsof -i:$PORT -t 2>/dev/null)
    if [ -n "$BACKEND_PROCESS" ]; then
        if [ $PORT -eq $ALTERNATIVE_PORT ] || [ $USE_ALTERNATIVE_PORT -eq 1 ]; then
            echo "Error: Unable to free port $PORT. Please manually terminate the process or specify a different port with -p option."
            exit 1
        else
            # Try alternative port
            echo "Port $PORT is busy. Trying alternative port $ALTERNATIVE_PORT..."
            PORT=$ALTERNATIVE_PORT
            BACKEND_PROCESS=$(lsof -i:$PORT -t 2>/dev/null)
            if [ -n "$BACKEND_PROCESS" ]; then
                echo "Error: Alternative port $PORT is also busy. Please manually terminate the processes or specify a different port with -p option."
                exit 1
            fi
        fi
    fi
fi

echo "Starting Study Buddy services..."

# Function to handle cleanup on exit
cleanup() {
    echo "Stopping services..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

# Set trap for cleanup on SIGINT (Ctrl+C)
trap cleanup SIGINT

# Start Backend
echo "Starting FastAPI backend on http://localhost:$PORT..."
cd "$(dirname "$0")"

# Create a .env file with the PORT if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file with PORT=$PORT"
    echo "PORT=$PORT" > .env
elif ! grep -q "^PORT=" .env; then
    echo "Adding PORT=$PORT to .env"
    echo "PORT=$PORT" >> .env
else
    echo "Updating PORT in .env"
    sed -i '' "s/^PORT=.*/PORT=$PORT/" .env
fi

# Activate virtual environment before running uvicorn
echo "Activating Python virtual environment..."
if [ -d ".venv" ]; then
    source .venv/bin/activate || source .venv/Scripts/activate
    echo "Virtual environment activated"
else
    echo "Warning: .venv directory not found. The server may not start correctly."
fi

uvicorn main:app --reload --host 0.0.0.0 --port $PORT &
BACKEND_PID=$!

# Check if backend started successfully
sleep 2
if ! ps -p $BACKEND_PID > /dev/null || ! curl -s http://localhost:$PORT/healthcheck > /dev/null; then
    echo "Failed to start backend! Check if port $PORT is available."
    exit 1
fi

# Update frontend configuration
echo "Configuring frontend to use backend at port $PORT..."
FRONTEND_CONFIG_FILE="$(dirname "$0")/frontend/client/src/lib/config.ts"
if [ -f "$FRONTEND_CONFIG_FILE" ]; then
    sed -i '' "s/export const API_BASE_URL = .*$/export const API_BASE_URL = '\/api';/" "$FRONTEND_CONFIG_FILE"
    sed -i '' "s/export const BACKEND_PORT = .*$/export const BACKEND_PORT = $PORT;/" "$FRONTEND_CONFIG_FILE" 2>/dev/null || true
    if ! grep -q "BACKEND_PORT" "$FRONTEND_CONFIG_FILE"; then
        echo "export const BACKEND_PORT = $PORT;" >> "$FRONTEND_CONFIG_FILE"
    fi
fi

# Start Frontend
echo "Starting React frontend..."
cd "$(dirname "$0")/frontend"
FRONTEND_PORT=3001 VITE_BACKEND_PORT=$PORT npm run dev &
FRONTEND_PID=$!

# Check if frontend started successfully
sleep 2
if ! ps -p $FRONTEND_PID > /dev/null; then
    echo "Failed to start frontend!"
    kill $BACKEND_PID
    exit 1
fi

echo "Both services started successfully!"
echo "Backend: http://localhost:$PORT"
echo "Frontend: http://localhost:3001"
echo "Press Ctrl+C to stop both services"

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID