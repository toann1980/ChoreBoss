#!/usr/bin/env bash
#
# Envestero Phase 1 Quick-Start Setup
#
# This script prepares the environment for running Phase 1 backfill.
# Assumes: Python 3.10+, PostgreSQL 14+ with TimescaleDB, git repo cloned
#
# Usage:
#   cd /srv/github/Envestero
#   bash ../../.openclaw/workspace/PHASE-1-QUICKSTART.sh
#

set -e

echo "=================================================="
echo "  Envestero Phase 1 — Quick-Start Setup"
echo "=================================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Step 1: Check Python version
echo -e "\n${YELLOW}Step 1: Checking Python version...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 not found${NC}"
    exit 1
fi
PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo -e "${GREEN}✓ Python $PYTHON_VERSION${NC}"

# Step 2: Create virtual environment
echo -e "\n${YELLOW}Step 2: Setting up virtual environment...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ Created venv/${NC}"
else
    echo -e "${GREEN}✓ venv/ already exists${NC}"
fi

# Activate venv
source venv/bin/activate
echo -e "${GREEN}✓ Activated venv${NC}"

# Step 3: Install dependencies
echo -e "\n${YELLOW}Step 3: Installing dependencies...${NC}"
pip install --upgrade pip setuptools wheel > /dev/null 2>&1
pip install -e . > /dev/null 2>&1
echo -e "${GREEN}✓ Installed envestero package${NC}"

# Step 4: Check .env file
echo -e "\n${YELLOW}Step 4: Checking .env configuration...${NC}"
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating .env template...${NC}"
    cat > .env << 'EOF'
# Database
DB_HOST=localhost
DB_PORT=5432
DB_USER=envestero
DB_PASSWORD=changeme
DB_NAME=envestero

# Data paths
DATA_PATH=/data/envestero

# yfinance rate limit (2000 req/hour)
YFINANCE_HOURLY_LIMIT=2000

# Application
APP_ENV=development
LOG_LEVEL=INFO

# LLM (for sentiment analysis, Phase 2)
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2

# Optional: OpenAI fallback
# OPENAI_API_KEY=sk-...
# OPENAI_MODEL=gpt-4o-mini
EOF
    echo -e "${YELLOW}Created .env (please edit DB credentials)${NC}"
else
    echo -e "${GREEN}✓ .env already exists${NC}"
fi

# Step 5: Check PostgreSQL connection
echo -e "\n${YELLOW}Step 5: Checking PostgreSQL connection...${NC}"
if command -v psql &> /dev/null; then
    PGPASSWORD="${DB_PASSWORD:-}" psql -h "${DB_HOST:-localhost}" -U "${DB_USER:-envestero}" -d "${DB_NAME:-envestero}" -c "SELECT version();" > /dev/null 2>&1 && \
        echo -e "${GREEN}✓ PostgreSQL connection OK${NC}" || \
        echo -e "${YELLOW}⚠ PostgreSQL connection failed (may need to start DB)${NC}"
else
    echo -e "${YELLOW}⚠ psql not found (install PostgreSQL client)${NC}"
fi

# Step 6: Check Nasdaq screener CSV
echo -e "\n${YELLOW}Step 6: Checking for Nasdaq screener CSV...${NC}"
DATA_PATH="${DATA_PATH:-/data/envestero}"
SCREENER_DIR="$DATA_PATH/nasdaq_screener"

if [ -d "$SCREENER_DIR" ]; then
    CSV_COUNT=$(ls "$SCREENER_DIR"/*.csv 2>/dev/null | wc -l)
    if [ "$CSV_COUNT" -gt 0 ]; then
        LATEST_CSV=$(ls -t "$SCREENER_DIR"/*.csv | head -1)
        echo -e "${GREEN}✓ Found Nasdaq screener CSV:${NC}"
        echo "  $(basename "$LATEST_CSV")"
    else
        echo -e "${YELLOW}⚠ No CSV files in $SCREENER_DIR${NC}"
        echo -e "${YELLOW}  Download from: https://www.nasdaq.com/market-activity/stocks/screener${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Directory not found: $SCREENER_DIR${NC}"
    echo -e "${YELLOW}  Creating: mkdir -p $SCREENER_DIR${NC}"
    mkdir -p "$SCREENER_DIR"
fi

# Step 7: Run database migrations
echo -e "\n${YELLOW}Step 7: Running database migrations...${NC}"
if command -v alembic &> /dev/null; then
    alembic upgrade head > /dev/null 2>&1 && \
        echo -e "${GREEN}✓ Alembic migrations applied${NC}" || \
        echo -e "${YELLOW}⚠ Alembic migrations failed (check DB connection)${NC}"
else
    echo -e "${YELLOW}⚠ Alembic not found (should be in dependencies)${NC}"
fi

# Step 8: Summary
echo -e "\n${GREEN}=================================================="
echo "  Setup Complete!"
echo "==================================================${NC}"
echo ""
echo "Next steps:"
echo ""
echo "  1. Edit .env with your database credentials"
echo "  2. Download Nasdaq screener CSV:"
echo "     https://www.nasdaq.com/market-activity/stocks/screener"
echo "     → Save to: $SCREENER_DIR/"
echo ""
echo "  3. Run Phase 1 backfill:"
echo "     python -m envestero.cli backfill-nasdaq"
echo ""
echo "  4. Monitor progress:"
echo "     tail -f /var/log/envestero/app.log"
echo ""
echo "  5. Verify in database:"
echo "     SELECT COUNT(*) FROM ticker_info WHERE active=True;"
echo "     SELECT COUNT(*) FROM ohlcv;"
echo ""
