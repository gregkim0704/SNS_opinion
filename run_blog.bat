@echo off
chcp 65001 > nul
echo ========================================
echo   AI 블로그 자동화 앱 시작
echo ========================================

REM 가상환경 활성화
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    echo 가상환경 활성화됨
) else (
    echo 가상환경이 없습니다. setup.bat을 먼저 실행하세요.
    pause
    exit /b 1
)

REM 환경변수 확인
if exist .env (
    echo .env 파일 확인됨
) else (
    echo 경고: .env 파일이 없습니다. .env.example을 참고하여 생성하세요.
)

echo.
echo 앱 시작 중...
echo 브라우저에서 http://localhost:5001 접속하세요.
echo.

python blog_app.py

pause
