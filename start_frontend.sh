#!/bin/bash
# Quick start script for ChoreBoss Flask frontend bridge

cd /srv/github/ChoreBoss

echo "🚀 ChoreBoss Flask Frontend Startup"
echo "===================================="
echo ""

# Check if venv exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Creating venv..."
    python3.14 -m venv .venv
fi

# Activate venv
echo "✅ Activating virtual environment..."
source .venv/bin/activate

# Set defaults for the ChoreBoss integration harness
export DATABASE_URL="${DATABASE_URL:-sqlite+aiosqlite:///choreboss.db}"
export API_BASE_URL="${API_BASE_URL:-http://localhost:8055/api}"
export FLASK_PORT="${FLASK_PORT:-8056}"

LAN_IP=$(hostname -I 2>/dev/null | awk '{print $1}')

echo "✅ Database: $DATABASE_URL"
echo "✅ API backend: $API_BASE_URL"
echo "✅ Frontend port: $FLASK_PORT"
echo ""
echo "🌐 Starting Flask frontend..."
echo "    Binding: 0.0.0.0:${FLASK_PORT}"
echo "    Frontend will be available at: http://${LAN_IP:-<this-machine-ip>}:${FLASK_PORT}"
echo "    API backend should be running at: ${API_BASE_URL}"
echo ""
echo "Login credentials:"
echo "    Login name: john"
echo "    PIN: 1234"
echo ""
echo "Press Ctrl+C to stop"
echo ""

python flask_bridge.py
