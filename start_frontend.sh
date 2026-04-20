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

# Set database to SQLite (async)
export DATABASE_URL="sqlite+aiosqlite:///choreboss.db"

echo "✅ Database: $DATABASE_URL"
echo ""
echo "🌐 Starting Flask frontend..."
echo "    Frontend will be available at: http://localhost:8055"
echo "    API backend should be running at: http://localhost:8000"
echo ""
echo "Login credentials:"
echo "    Person ID: 1"
echo "    PIN: 1234"
echo ""
echo "Press Ctrl+C to stop"
echo ""

python flask_bridge.py
