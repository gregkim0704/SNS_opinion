# SNS 의견 동향 분석 앱

소셜 미디어(SNS) 상의 리뷰와 의견을 수집하고 동향을 분석하는 웹 애플리케이션입니다.

## 주요 기능

- 📊 **감정 분석**: 긍정/부정/중립 의견 자동 분류
- 📈 **트렌드 분석**: 시간별 의견 동향 시각화
- 🔑 **키워드 추출**: 주요 키워드 및 워드클라우드
- 📉 **통계 대시보드**: 실시간 분석 결과 제공

## 기술 스택

- **Backend**: Python Flask
- **Frontend**: HTML, CSS, JavaScript (Chart.js)
- **분석**: TextBlob (감정 분석), scikit-learn (텍스트 처리)

## 설치 방법

### Windows 사용자

**간단한 방법 (추천):**
1. 프로젝트 폴더로 이동
2. `setup.bat` 더블클릭 (또는 명령 프롬프트에서 실행)
3. `run.bat` 더블클릭으로 앱 시작

**명령 프롬프트 사용:**
```cmd
# 1. 프로젝트 폴더로 이동 (예시)
cd C:\Users\YourName\SNS_opinion

# 2. 설치
setup.bat

# 3. 실행
run.bat
```

**수동 설치:**
```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -c "import textblob; textblob.download_corpora()"
python app.py
```

📖 **자세한 가이드**: [WINDOWS_GUIDE.md](WINDOWS_GUIDE.md) 참고

### Linux/Mac 사용자

**스크립트 사용:**
```bash
# 설치
bash setup.sh

# 실행
bash run.sh
```

**수동 설치:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -c "import textblob; textblob.download_corpora()"
python app.py
```

## 사용 방법

1. 브라우저에서 `http://localhost:5000` 접속
2. SNS 텍스트 데이터 입력 또는 샘플 데이터 로드
3. 분석 결과 확인 (감정 분석, 트렌드, 키워드)

## API 엔드포인트

- `GET /`: 메인 페이지
- `POST /api/analyze`: 텍스트 분석
- `GET /api/trends`: 트렌드 데이터
- `GET /api/keywords`: 키워드 추출
- `GET /api/sample-data`: 샘플 데이터 로드

## 라이선스

MIT License
