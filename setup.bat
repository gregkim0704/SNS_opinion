@echo off
chcp 65001 >nul
echo =========================================
echo SNS 의견 동향 분석 앱 설치 스크립트
echo =========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python이 설치되어 있지 않습니다.
    echo Python 3.8 이상을 설치해주세요.
    echo 다운로드: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python 발견
python --version
echo.

REM Create virtual environment
echo 📦 가상환경 생성 중...
python -m venv venv

if errorlevel 1 (
    echo ❌ 가상환경 생성 실패
    pause
    exit /b 1
)

echo ✅ 가상환경 생성 완료
echo.

REM Activate virtual environment
echo 🔧 가상환경 활성화 중...
call venv\Scripts\activate.bat

REM Upgrade pip
echo 📦 pip 업그레이드 중...
python -m pip install --upgrade pip >nul 2>&1

REM Install requirements
echo 📦 의존성 패키지 설치 중...
pip install -r requirements.txt

if errorlevel 1 (
    echo ❌ 패키지 설치 실패
    pause
    exit /b 1
)

echo ✅ 패키지 설치 완료
echo.

REM Download TextBlob corpora
echo 📥 TextBlob 데이터 다운로드 중...
python -c "import textblob; textblob.download_corpora()" >nul 2>&1

if errorlevel 1 (
    echo ⚠️  TextBlob 데이터 다운로드 실패 (나중에 수동으로 다운로드하세요)
) else (
    echo ✅ TextBlob 데이터 다운로드 완료
)

echo.
echo =========================================
echo ✅ 설치 완료!
echo =========================================
echo.
echo 앱 실행 방법:
echo 1. run.bat 더블클릭
echo    또는
echo 2. 명령 프롬프트에서: run.bat
echo.
echo 브라우저에서 http://localhost:5000 접속
echo.
pause
