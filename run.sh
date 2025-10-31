#!/bin/bash

echo "========================================="
echo "SNS 의견 동향 분석 앱 실행"
echo "========================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ 가상환경이 없습니다."
    echo "먼저 setup.sh를 실행해주세요: bash setup.sh"
    exit 1
fi

# Activate virtual environment
echo "🔧 가상환경 활성화 중..."
source venv/bin/activate

# Check if Flask is installed
if ! python3 -c "import flask" 2>/dev/null; then
    echo "❌ Flask가 설치되어 있지 않습니다."
    echo "먼저 setup.sh를 실행해주세요: bash setup.sh"
    exit 1
fi

echo "✅ 의존성 확인 완료"
echo ""
echo "🚀 서버 시작 중..."
echo "📱 브라우저에서 http://localhost:5000 을 열어주세요"
echo ""
echo "종료하려면 Ctrl+C를 누르세요"
echo "========================================="
echo ""

# Run the application
python3 app.py
