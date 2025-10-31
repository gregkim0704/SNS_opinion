# SNS 의견 동향 분석 앱

소셜 미디어(SNS) 상의 리뷰와 의견을 수집하고 동향을 분석하는 웹 애플리케이션입니다.

## 주요 기능

- 📊 **감정 분석**: 긍정/부정/중립 의견 자동 분류
- 📈 **트렌드 분석**: 시간별 의견 동향 시각화
- 🔑 **키워드 추출**: 주요 키워드 및 워드클라우드
- 📉 **통계 대시보드**: 실시간 분석 결과 제공
- 🔍 **네이버 API 연동**: 실시간 데이터 수집 (블로그, 뉴스, 카페, 쇼핑)

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

### 기본 사용

1. 브라우저에서 `http://localhost:5000` 접속
2. **샘플 데이터 로드** 버튼으로 테스트 데이터 확인
3. 직접 리뷰 입력하거나 네이버 API로 실시간 데이터 수집

### 🔍 네이버 API 실시간 데이터 수집 (선택사항)

실제 네이버에서 블로그, 뉴스, 카페, 쇼핑 데이터를 실시간으로 수집하여 분석할 수 있습니다.

**설정 방법:**

1. [네이버 개발자 센터](https://developers.naver.com)에서 API 키 발급
2. `.env.example` 파일을 `.env`로 복사
3. `.env` 파일에 API 키 입력:
   ```env
   NAVER_CLIENT_ID=your_client_id
   NAVER_CLIENT_SECRET=your_client_secret
   ```
4. 앱 재시작

**사용 예시:**
- 검색어: "아이폰 15", "강남 맛집", "테슬라"
- 카테고리 선택: 블로그, 뉴스, 카페, 쇼핑
- "수집 & 분석" 클릭 → 실시간 데이터 자동 분석

📖 **자세한 설정 가이드**: [NAVER_API_GUIDE.md](NAVER_API_GUIDE.md) 참고

## API 엔드포인트

### 기본 API
- `GET /`: 메인 페이지
- `POST /api/analyze`: 텍스트 감정 분석
- `GET /api/trends`: 시간별 트렌드 데이터
- `GET /api/keywords`: 주요 키워드 추출
- `GET /api/statistics`: 전체 통계 조회
- `POST /api/sample-data`: 샘플 데이터 로드
- `POST /api/clear-data`: 데이터 초기화

### 네이버 API (선택사항)
- `POST /api/naver-search`: 네이버에서 데이터 검색
- `POST /api/naver-collect`: 네이버 데이터 수집 및 분석 추가
- `GET /api/naver-status`: 네이버 API 연동 상태 확인

## 라이선스

MIT License
