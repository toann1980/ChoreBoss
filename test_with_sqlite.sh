#!/bin/bash
cd /srv/github/ChoreBoss

# Set database to SQLite (async)
export DATABASE_URL="sqlite+aiosqlite:///choreboss.db"

# Start FastAPI backend
/srv/github/ChoreBoss/.venv/bin/python api_run.py &
API_PID=$!
echo "FastAPI backend started (PID: $API_PID)"
sleep 4

echo ""
echo "Running integration test..."
/srv/github/ChoreBoss/.venv/bin/python test_integration.py
TEST_RESULT=$?

kill $API_PID 2>/dev/null || true
wait $API_PID 2>/dev/null || true

exit $TEST_RESULT
