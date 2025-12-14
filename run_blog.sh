#!/bin/bash
# AI 블로그 자동화 앱 실행 스크립트

echo "========================================"
echo "  AI 블로그 자동화 앱 시작"
echo "========================================"

# 가상환경 활성화
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "가상환경 활성화됨"
else
    echo "가상환경이 없습니다. setup.sh를 먼저 실행하세요."
    exit 1
fi

# 환경변수 로드
if [ -f ".env" ]; then
    echo ".env 파일 로드됨"
else
    echo "경고: .env 파일이 없습니다. .env.example을 참고하여 생성하세요."
fi

echo ""
echo "앱 시작 중..."
echo "브라우저에서 http://localhost:5001 접속하세요."
echo ""

python blog_app.py
