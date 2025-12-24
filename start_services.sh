#!/bin/bash

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$PROJECT_DIR/logs"
mkdir -p "$LOG_DIR"

echo -e "${GREEN}Starting AI CS Services...${NC}"

# Start Backend
echo -e "${YELLOW}Starting Backend...${NC}"
cd "$PROJECT_DIR/backend"
nohup npm run dev > "$LOG_DIR/backend.log" 2>&1 &
echo $! > "$LOG_DIR/backend.pid"
echo -e "${GREEN}✓ Backend started (PID: $(cat $LOG_DIR/backend.pid))${NC}"

# Wait for backend
sleep 5

# Start Frontend
echo -e "${YELLOW}Starting Frontend...${NC}"
cd "$PROJECT_DIR/frontend"
nohup npm start > "$LOG_DIR/frontend.log" 2>&1 &
echo $! > "$LOG_DIR/frontend.pid"
echo -e "${GREEN}✓ Frontend started (PID: $(cat $LOG_DIR/frontend.pid))${NC}"

# Start Crawler
echo -e "${YELLOW}Starting Crawler...${NC}"
cd "$PROJECT_DIR/crawler"
. venv/bin/activate
nohup python main.py > "$LOG_DIR/crawler.log" 2>&1 &
echo $! > "$LOG_DIR/crawler.pid"
deactivate 2>/dev/null || true
echo -e "${GREEN}✓ Crawler started (PID: $(cat $LOG_DIR/crawler.pid))${NC}"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  All services started!${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "Frontend: http://localhost:3000"
echo -e "Backend:  http://localhost:3001"
echo ""
echo -e "Logs: $LOG_DIR/"
echo -e "Stop: ./stop_services.sh"
