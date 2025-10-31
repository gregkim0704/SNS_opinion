@echo off
chcp 65001 >nul
echo =========================================
echo SNS 의견 동향 분석 앱 실행
echo =========================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo ❌ 가상환경이 없습니다.
    echo 먼저 setup.bat을 실행해주세요.
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment
echo 🔧 가상환경 활성화 중...
call venv\Scripts\activate.bat

REM Check if Flask is installed
python -c "import flask" 2>nul
if errorlevel 1 (
    echo ❌ Flask가 설치되어 있지 않습니다.
    echo 먼저 setup.bat을 실행해주세요.
    echo.
    pause
    exit /b 1
)

echo ✅ 의존성 확인 완료
echo.
echo 🚀 서버 시작 중...
echo 📱 브라우저에서 http://localhost:5000 을 열어주세요
echo.
echo 종료하려면 Ctrl+C를 누르세요
echo =========================================
echo.

REM Run the application
python app.py
