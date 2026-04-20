#!/bin/bash
# Quick start script for ChoreBoss FastAPI backend

cd /srv/github/ChoreBoss

echo "🚀 ChoreBoss FastAPI Backend Startup"
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
echo "🌐 Starting FastAPI server..."
echo "    API will be available at: http://localhost:8000"
echo "    Docs at: http://localhost:8000/docs"
echo "    ReDoc at: http://localhost:8000/redoc"
echo ""
echo "Press Ctrl+C to stop"
echo ""

python api_run.py
