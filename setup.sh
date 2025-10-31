#!/bin/bash

echo "========================================="
echo "SNS 의견 동향 분석 앱 설치 스크립트"
echo "========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3가 설치되어 있지 않습니다."
    echo "Python 3.8 이상을 설치해주세요."
    exit 1
fi

echo "✅ Python3 발견: $(python3 --version)"
echo ""

# Create virtual environment
echo "📦 가상환경 생성 중..."
python3 -m venv venv

if [ $? -ne 0 ]; then
    echo "❌ 가상환경 생성 실패"
    exit 1
fi

echo "✅ 가상환경 생성 완료"
echo ""

# Activate virtual environment
echo "🔧 가상환경 활성화 중..."
source venv/bin/activate

# Upgrade pip
echo "📦 pip 업그레이드 중..."
pip install --upgrade pip > /dev/null 2>&1

# Install requirements
echo "📦 의존성 패키지 설치 중..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ 패키지 설치 실패"
    exit 1
fi

echo "✅ 패키지 설치 완료"
echo ""

# Download TextBlob corpora
echo "📥 TextBlob 데이터 다운로드 중..."
python3 -c "import textblob; textblob.download_corpora()" > /dev/null 2>&1

if [ $? -ne 0 ]; then
    echo "⚠️  TextBlob 데이터 다운로드 실패 (나중에 수동으로 다운로드하세요)"
else
    echo "✅ TextBlob 데이터 다운로드 완료"
fi

echo ""
echo "========================================="
echo "✅ 설치 완료!"
echo "========================================="
echo ""
echo "앱 실행 방법:"
echo "1. source venv/bin/activate"
echo "2. python app.py"
echo "3. 브라우저에서 http://localhost:5000 접속"
echo ""
