#!/bin/bash
# 데이터 수집 스케줄러 시작 스크립트

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "========================================"
echo "🚀 데이터 수집 스케줄러 시작"
echo "========================================"
echo "📂 작업 디렉토리: $SCRIPT_DIR"
echo "⏰ 수집 주기: 1시간마다"
echo "========================================"

cd "$SCRIPT_DIR"

# Python 가상환경 활성화 (있는 경우)
if [ -d "venv" ]; then
    echo "🐍 가상환경 활성화 중..."
    source venv/bin/activate
fi

# 필요한 패키지 확인
echo "📦 필요한 패키지 확인 중..."
python3 -c "import schedule" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  schedule 패키지가 설치되어 있지 않습니다."
    echo "📥 설치 중: pip3 install schedule"
    pip3 install schedule
fi

# 스케줄러 실행
echo "✅ 스케줄러 시작..."
python3 scheduler.py

echo "⏹️  스케줄러 종료"

