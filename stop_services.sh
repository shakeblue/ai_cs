#!/bin/bash

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$PROJECT_DIR/logs"

echo -e "${RED}Stopping AI CS Services...${NC}"

# Stop Backend
if [ -f "$LOG_DIR/backend.pid" ]; then
    kill $(cat "$LOG_DIR/backend.pid") 2>/dev/null
    rm "$LOG_DIR/backend.pid"
    echo -e "${GREEN}✓ Backend stopped${NC}"
fi

# Stop Frontend
if [ -f "$LOG_DIR/frontend.pid" ]; then
    kill $(cat "$LOG_DIR/frontend.pid") 2>/dev/null
    rm "$LOG_DIR/frontend.pid"
    echo -e "${GREEN}✓ Frontend stopped${NC}"
fi

# Stop Crawler
if [ -f "$LOG_DIR/crawler.pid" ]; then
    kill $(cat "$LOG_DIR/crawler.pid") 2>/dev/null
    rm "$LOG_DIR/crawler.pid"
    echo -e "${GREEN}✓ Crawler stopped${NC}"
fi

# Kill any remaining processes
pkill -f "node.*backend" 2>/dev/null || true
pkill -f "react-scripts" 2>/dev/null || true
pkill -f "python.*main.py" 2>/dev/null || true

echo -e "${GREEN}All services stopped${NC}"
