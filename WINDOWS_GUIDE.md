# Windows 사용자를 위한 설치 가이드

## 📋 사전 요구사항

### Python 설치
1. Python 3.8 이상이 필요합니다
2. [Python 공식 사이트](https://www.python.org/downloads/)에서 다운로드
3. 설치 시 **"Add Python to PATH"** 옵션을 반드시 체크하세요

### Python 설치 확인
명령 프롬프트(CMD)를 열고 다음 명령어로 확인:
```cmd
python --version
```

## 🚀 빠른 시작 (Windows)

### 방법 1: 배치 파일 사용 (추천)

1. **프로젝트 다운로드 위치로 이동**
   ```cmd
   cd C:\경로\SNS_opinion
   ```

2. **설치 실행**
   - `setup.bat` 파일을 더블클릭
   - 또는 명령 프롬프트에서:
   ```cmd
   setup.bat
   ```

3. **앱 실행**
   - `run.bat` 파일을 더블클릭
   - 또는 명령 프롬프트에서:
   ```cmd
   run.bat
   ```

4. **브라우저 열기**
   - 자동으로 열리지 않으면 수동으로 접속: http://localhost:5000

### 방법 2: 수동 설치

```cmd
# 1. 프로젝트 폴더로 이동
cd C:\경로\SNS_opinion

# 2. 가상환경 생성
python -m venv venv

# 3. 가상환경 활성화
venv\Scripts\activate

# 4. 의존성 설치
pip install -r requirements.txt

# 5. TextBlob 데이터 다운로드
python -c "import textblob; textblob.download_corpora()"

# 6. 앱 실행
python app.py
```

## 📂 현재 위치 확인

명령 프롬프트에서 현재 위치를 확인하려면:
```cmd
cd
```

프로젝트 폴더의 파일 목록을 보려면:
```cmd
dir
```

다음 파일들이 보여야 합니다:
- app.py
- requirements.txt
- setup.bat
- run.bat
- templates 폴더
- static 폴더

## ⚠️ 일반적인 문제 해결

### "python을 찾을 수 없습니다" 오류
- Python이 PATH에 추가되지 않았습니다
- Python을 재설치하면서 "Add Python to PATH" 체크
- 또는 시스템 환경 변수에 Python 경로 수동 추가

### "requirements.txt를 찾을 수 없습니다" 오류
- 현재 디렉토리가 프로젝트 폴더가 아닙니다
- `cd` 명령어로 올바른 폴더로 이동하세요
- 예: `cd C:\Users\water\SNS_opinion`

### 가상환경 활성화 오류
- PowerShell에서 실행 정책 오류가 발생하면:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```
- 또는 명령 프롬프트(CMD)를 사용하세요

### 포트 5000이 이미 사용 중
- 다른 앱이 포트 5000을 사용 중입니다
- app.py의 마지막 줄을 수정:
  ```python
  app.run(debug=True, host='0.0.0.0', port=5001)
  ```

## 🎯 단계별 첫 실행 가이드

### Step 1: 명령 프롬프트 열기
- Windows 키 + R
- "cmd" 입력 후 Enter

### Step 2: 프로젝트 위치 확인
레포지토리를 클론했거나 다운로드한 위치를 찾습니다.
예를 들어:
- `C:\Users\water\SNS_opinion`
- `D:\Projects\SNS_opinion`

### Step 3: 해당 폴더로 이동
```cmd
cd C:\Users\water\SNS_opinion
```

### Step 4: 파일 확인
```cmd
dir
```
app.py, requirements.txt 등이 보이는지 확인

### Step 5: 설치 및 실행
```cmd
setup.bat
```
설치가 완료되면:
```cmd
run.bat
```

### Step 6: 브라우저에서 확인
http://localhost:5000 접속

## 💡 유용한 팁

### Git Bash를 사용하는 경우
Git Bash에서는 Linux 스크립트를 사용할 수 있습니다:
```bash
bash setup.sh
bash run.sh
```

### Visual Studio Code 사용자
1. VSCode에서 프로젝트 폴더 열기
2. 터미널 열기 (Ctrl + `)
3. 터미널에서 setup.bat 또는 run.bat 실행

### 자동 실행 배치 파일 만들기
프로젝트 폴더에 `start.bat` 생성:
```batch
@echo off
start http://localhost:5000
call run.bat
```

## 🔍 디버깅

문제가 발생하면 다음을 확인하세요:

1. **Python 버전**
   ```cmd
   python --version
   ```
   3.8 이상이어야 합니다

2. **현재 디렉토리**
   ```cmd
   cd
   ```

3. **파일 존재 여부**
   ```cmd
   dir requirements.txt
   ```

4. **가상환경 상태**
   명령 프롬프트에 `(venv)`가 표시되면 활성화된 상태입니다

## 📞 추가 도움

문제가 계속되면 다음 정보와 함께 문의하세요:
- Windows 버전
- Python 버전
- 오류 메시지 전체 내용
- 실행한 명령어
