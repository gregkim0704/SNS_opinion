# SNS 의견 동향 분석 앱 - 주요 기능

## 📊 대시보드 개요

이 애플리케이션은 소셜 미디어에서 수집된 리뷰와 의견을 실시간으로 분석하고 시각화합니다.

## 🎯 주요 기능

### 1. 실시간 감정 분석
- **TextBlob** 라이브러리를 사용한 자연어 처리
- 각 리뷰를 **긍정(Positive)**, **중립(Neutral)**, **부정(Negative)**으로 분류
- 극성(Polarity)과 주관성(Subjectivity) 점수 계산
- 분석 결과를 즉시 표시

### 2. 다중 플랫폼 지원
지원하는 SNS 플랫폼:
- Twitter
- Facebook
- Instagram
- YouTube
- TikTok

### 3. 통계 대시보드
실시간으로 업데이트되는 통계:
- 총 리뷰 수
- 긍정/중립/부정 의견 개수
- 플랫폼별 분포
- 평균 극성 및 주관성 점수

### 4. 데이터 시각화

#### 감정 분포 차트
- 도넛 차트로 감정 비율 표시
- 색상 코딩으로 직관적 이해

#### 플랫폼별 분포 차트
- 막대 그래프로 각 플랫폼의 리뷰 수 비교

#### 시간별 트렌드 차트
- 선 그래프로 날짜별 감정 변화 추이 분석
- 여러 감정을 동시에 비교

### 5. 키워드 추출
- 자동으로 주요 키워드 추출
- 빈도수 기반 정렬
- 불용어(Stopwords) 제거
- 시각적 태그 클라우드

### 6. 샘플 데이터
- 테스트용 샘플 데이터 제공
- 15개의 다양한 리뷰 샘플
- 각 감정 유형별 균형 잡힌 데이터

## 🔧 기술 스택

### Backend
- **Flask**: 웹 프레임워크
- **Flask-CORS**: CORS 지원
- **TextBlob**: 자연어 처리 및 감정 분석
- **Pandas**: 데이터 처리 및 분석
- **NumPy**: 수치 연산
- **scikit-learn**: 머신러닝 유틸리티

### Frontend
- **HTML5/CSS3**: 반응형 UI
- **JavaScript (ES6+)**: 인터랙티브 기능
- **Chart.js**: 데이터 시각화
- **Fetch API**: RESTful API 통신

## 📡 API 엔드포인트

### GET /
메인 페이지 렌더링

### POST /api/analyze
**Request Body:**
```json
{
  "text": "리뷰 내용",
  "platform": "Twitter"
}
```

**Response:**
```json
{
  "text": "리뷰 내용",
  "platform": "Twitter",
  "sentiment": "positive",
  "polarity": 0.75,
  "subjectivity": 0.6,
  "date": "2024-01-15"
}
```

### GET /api/statistics
전체 통계 데이터 조회

### GET /api/trends
시간별 트렌드 데이터 조회

### GET /api/keywords
주요 키워드 목록 조회

### POST /api/sample-data
샘플 데이터 로드

### POST /api/clear-data
모든 데이터 삭제

## 🎨 UI/UX 특징

- **반응형 디자인**: 모바일, 태블릿, 데스크톱 지원
- **그라디언트 컬러**: 현대적이고 세련된 디자인
- **부드러운 애니메이션**: 사용자 경험 향상
- **직관적 인터페이스**: 쉬운 조작과 명확한 정보 전달
- **실시간 업데이트**: 즉각적인 피드백

## 🚀 확장 가능성

향후 추가 가능한 기능:
- 실제 SNS API 연동 (Twitter API, Facebook Graph API 등)
- 데이터베이스 연동 (MongoDB, PostgreSQL)
- 사용자 인증 시스템
- 고급 NLP 모델 (BERT, GPT 등)
- 다국어 지원
- 비교 분석 기능
- PDF/Excel 리포트 생성
- 실시간 알림 시스템
- 머신러닝 기반 예측 모델
