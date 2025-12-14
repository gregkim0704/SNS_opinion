# AI 블로그 자동화 앱 사용 가이드

구글 블로그 + 쓰레드 + AI 자동 글 생성을 통한 애드센스 수익화 시스템입니다.

## 핵심 기능

### 1. 3분 글 생성 시스템
- 키워드 하나만 입력하면 AI가 자동으로 SEO 최적화된 블로그 글 생성
- 다양한 스타일 선택: 정보형, 리스트형, 튜토리얼, 스토리텔링, 리뷰
- 쓰레드용 바이럴 훅 자동 생성

### 2. 3시간 자동 발행
- APScheduler를 활용한 자동 발행 시스템
- 설정한 간격으로 큐에 있는 글을 자동 발행
- 일일 최대 발행 수, 활동 시간 설정 가능

### 3. 쓰레드 트래픽 터널
- 블로그 글 발행 시 쓰레드에 자동 홍보 게시물 발행
- 바이럴될 수 있는 훅 자동 생성

### 4. 유튜브 대본 재가공
- 유튜브 영상 자막 자동 추출
- 구어체를 문어체로 자연스럽게 변환
- SEO 최적화된 블로그 글로 재탄생

## 설치 방법

### 1. 패키지 설치

```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env.example`을 `.env`로 복사하고 API 키를 입력합니다:

```bash
cp .env.example .env
```

#### 필수: OpenAI API
```env
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_MODEL=gpt-4o-mini  # 또는 gpt-4, gpt-3.5-turbo
```

API 키 발급: https://platform.openai.com/api-keys

#### 선택: Google Blogger API

1. [Google Cloud Console](https://console.cloud.google.com) 접속
2. 새 프로젝트 생성
3. Blogger API 활성화
4. OAuth 2.0 클라이언트 ID 생성 (데스크톱 앱)
5. `credentials.json` 다운로드 후 프로젝트 루트에 저장

```env
BLOGGER_BLOG_ID=블로그ID
GOOGLE_CREDENTIALS_FILE=credentials.json
```

#### 선택: YouTube Data API

1. [Google Cloud Console](https://console.cloud.google.com) 접속
2. YouTube Data API v3 활성화
3. API 키 생성

```env
YOUTUBE_API_KEY=AIzaxxxxxxxxxxxxxxxxxxxxxxxx
```

#### 선택: Meta Threads API

1. [Meta for Developers](https://developers.facebook.com) 접속
2. 앱 생성 및 Threads API 권한 추가
3. Access Token 발급

```env
THREADS_ACCESS_TOKEN=액세스토큰
THREADS_USER_ID=유저ID
```

## 실행 방법

### 웹 앱 실행

```bash
python blog_app.py
```

브라우저에서 `http://localhost:5001` 접속

### CLI로 스케줄러 실행 (백그라운드)

```bash
# 상태 확인
python scheduler.py status

# 글 생성
python scheduler.py generate "키워드"

# 즉시 발행
python scheduler.py publish

# 스케줄러 시작 (3시간마다 자동 발행)
python scheduler.py start
```

## 사용 방법

### 1. 글 생성하기

1. 웹 앱에서 "글 생성" 탭 선택
2. 키워드 입력 (예: "부업으로 월 100만원 버는 방법")
3. 스타일, 어조, 길이 선택
4. "글 생성하기" 클릭
5. 미리보기 확인 후 "큐에 추가" 또는 "즉시 발행"

### 2. 유튜브 대본 재가공

1. "유튜브 재가공" 탭 선택
2. 유튜브 URL 입력
3. "대본 추출하기" 클릭
4. 필요시 타겟 키워드 입력
5. "블로그 글로 재가공" 클릭

### 3. 자동화 설정

1. "자동화 설정" 탭 선택
2. 발행 간격, 일일 최대 발행 수 설정
3. 활동 시간 설정 (예: 09시 ~ 22시)
4. 자동 생성용 키워드 입력 (쉼표로 구분)
5. "스케줄러 시작" 클릭

## 주요 설정 옵션

| 설정 | 설명 | 기본값 |
|------|------|--------|
| `blog_interval_hours` | 블로그 발행 간격 (시간) | 3 |
| `max_daily_posts` | 일일 최대 발행 수 | 8 |
| `working_hours` | 활동 시간 | 09:00 ~ 22:00 |
| `auto_generate` | 큐 부족 시 자동 생성 | true |
| `post_to_threads` | 쓰레드 자동 발행 | true |
| `keywords` | 자동 생성용 키워드 | [] |

## API 엔드포인트

### 글 생성
- `POST /api/generate` - AI로 블로그 글 생성
- `POST /api/generate/batch` - 배치 생성

### 유튜브
- `POST /api/youtube/extract` - 대본 추출
- `POST /api/youtube/rewrite` - 블로그 글로 재가공

### 발행 큐
- `GET /api/queue` - 큐 조회
- `POST /api/queue/add` - 큐에 추가

### Blogger
- `POST /api/blogger/auth` - 인증
- `POST /api/blogger/publish` - 발행
- `GET /api/blogger/posts` - 글 목록

### Threads
- `POST /api/threads/post` - 게시
- `POST /api/threads/generate-hook` - 훅 생성

### 스케줄러
- `GET /api/scheduler/status` - 상태 확인
- `POST /api/scheduler/start` - 시작
- `POST /api/scheduler/stop` - 중지
- `POST /api/scheduler/publish-now` - 즉시 발행

## 수익화 전략

### 1. 키워드 선정
- 검색량이 높은 롱테일 키워드 선택
- 경쟁이 적은 틈새 키워드 공략
- 시즌/트렌드 키워드 활용

### 2. 콘텐츠 최적화
- SEO 최적화된 제목과 메타 설명
- 적절한 소제목(H2, H3) 구조
- 이미지, 리스트 활용

### 3. 쓰레드 활용
- 바이럴 가능한 훅으로 관심 유도
- 블로그 링크로 유입 유도
- 꾸준한 게시로 팔로워 확보

### 4. 애드센스 최적화
- 콘텐츠 품질 유지
- 광고 배치 최적화
- 사용자 경험 고려

## 주의사항

1. **API 사용량**: OpenAI API 사용량과 비용 모니터링
2. **저작권**: 유튜브 재가공 시 원저작자 권리 존중
3. **품질 관리**: 자동 생성 글도 검토 후 발행 권장
4. **스팸 방지**: 과도한 발행은 플랫폼 정책 위반 주의

## 문제 해결

### OpenAI API 오류
- API 키 확인
- 크레딧 잔액 확인
- 모델명 확인 (gpt-4o-mini, gpt-4 등)

### Blogger 인증 실패
- credentials.json 파일 위치 확인
- OAuth 권한 스코프 확인
- 처음 인증 시 브라우저 창 확인

### YouTube 자막 추출 실패
- 자막이 비활성화된 영상
- 해당 언어 자막 없음
- 영상 ID 형식 확인

### 스케줄러 동작 안함
- 근무 시간 설정 확인
- 일일 최대 발행 수 확인
- 큐에 대기 중인 글 확인

## 라이선스

MIT License
