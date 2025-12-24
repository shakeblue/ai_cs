#!/bin/bash

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$PROJECT_DIR/logs"

echo -e "${YELLOW}AI CS Services Status${NC}"
echo "================================"

# Check Backend
if [ -f "$LOG_DIR/backend.pid" ] && kill -0 $(cat "$LOG_DIR/backend.pid") 2>/dev/null; then
    echo -e "Backend:  ${GREEN}Running${NC} (PID: $(cat $LOG_DIR/backend.pid))"
else
    echo -e "Backend:  ${RED}Stopped${NC}"
fi

# Check Frontend
if [ -f "$LOG_DIR/frontend.pid" ] && kill -0 $(cat "$LOG_DIR/frontend.pid") 2>/dev/null; then
    echo -e "Frontend: ${GREEN}Running${NC} (PID: $(cat $LOG_DIR/frontend.pid))"
else
    echo -e "Frontend: ${RED}Stopped${NC}"
fi

# Check Crawler
if [ -f "$LOG_DIR/crawler.pid" ] && kill -0 $(cat "$LOG_DIR/crawler.pid") 2>/dev/null; then
    echo -e "Crawler:  ${GREEN}Running${NC} (PID: $(cat $LOG_DIR/crawler.pid))"
else
    echo -e "Crawler:  ${RED}Stopped${NC}"
fi

# Check PostgreSQL
if pg_isready &>/dev/null; then
    echo -e "PostgreSQL: ${GREEN}Running${NC}"
else
    echo -e "PostgreSQL: ${RED}Stopped${NC}"
fi

# Check Redis
if redis-cli ping 2>/dev/null | grep -q PONG; then
    echo -e "Redis:    ${GREEN}Running${NC}"
else
    echo -e "Redis:    ${YELLOW}Stopped (optional)${NC}"
fi

echo "================================"
