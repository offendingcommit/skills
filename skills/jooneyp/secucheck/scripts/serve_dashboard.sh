#!/bin/bash
# Generate dashboard and serve it
# Usage: ./serve_dashboard.sh [port]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PORT="${1:-8766}"
OUTPUT_DIR="$HOME/.openclaw/workspace"
OUTPUT_FILE="$OUTPUT_DIR/secucheck-report.html"

# Kill any existing server on this port
pkill -f "http.server $PORT" 2>/dev/null || true

# Generate dashboard (use bash explicitly - ClawHub may strip exec permissions)
bash "$SCRIPT_DIR/generate_dashboard.sh" "$OUTPUT_FILE" >/dev/null 2>&1

# Start server in background
cd "$OUTPUT_DIR"
nohup python3 -m http.server "$PORT" --bind 0.0.0.0 > /tmp/secucheck-server.log 2>&1 &
SERVER_PID=$!

# Wait a moment for server to start
sleep 1

# Check if server started
if kill -0 $SERVER_PID 2>/dev/null; then
    echo "{"
    echo '  "status": "ok",'
    echo '  "url": "http://localhost:'"$PORT"'/secucheck-report.html",'
    echo '  "pid": '"$SERVER_PID"','
    echo '  "file": "'"$OUTPUT_FILE"'"'
    echo "}"
else
    echo '{"status": "error", "message": "Failed to start server"}'
    exit 1
fi
