"""
구글 Blogger API 연동 모듈
구글 블로그에 자동으로 글을 발행합니다.
"""
import os
import json
import pickle
from typing import Dict, List, Optional
from datetime import datetime

try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    GOOGLE_API_AVAILABLE = True
except ImportError:
    GOOGLE_API_AVAILABLE = False

from dotenv import load_dotenv

load_dotenv()


class BloggerClient:
    """구글 Blogger API 클라이언트"""

    SCOPES = ['https://www.googleapis.com/auth/blogger']

    def __init__(self):
        self.credentials = None
        self.service = None
        self.blog_id = os.getenv('BLOGGER_BLOG_ID')
        self.credentials_file = os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json')
        self.token_file = 'blogger_token.pickle'

    def is_available(self) -> bool:
        """Google API 라이브러리 설치 여부"""
        return GOOGLE_API_AVAILABLE

    def is_configured(self) -> bool:
        """API 설정 여부 확인"""
        return GOOGLE_API_AVAILABLE and os.path.exists(self.credentials_file)

    def is_authenticated(self) -> bool:
        """인증 여부 확인"""
        return self.service is not None

    def authenticate(self) -> bool:
        """
        구글 OAuth2 인증 수행

        Returns:
            인증 성공 여부
        """
        if not GOOGLE_API_AVAILABLE:
            raise ImportError("Google API 라이브러리가 설치되지 않았습니다. pip install google-api-python-client google-auth-oauthlib")

        if not os.path.exists(self.credentials_file):
            raise FileNotFoundError(f"인증 파일을 찾을 수 없습니다: {self.credentials_file}")

        # 저장된 토큰 확인
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                self.credentials = pickle.load(token)

        # 토큰 갱신 또는 새로 인증
        if not self.credentials or not self.credentials.valid:
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                self.credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, self.SCOPES
                )
                self.credentials = flow.run_local_server(port=0)

            # 토큰 저장
            with open(self.token_file, 'wb') as token:
                pickle.dump(self.credentials, token)

        # 서비스 생성
        self.service = build('blogger', 'v3', credentials=self.credentials)
        return True

    def get_blogs(self) -> List[Dict]:
        """
        사용자의 블로그 목록 가져오기

        Returns:
            블로그 목록
        """
        if not self.service:
            raise Exception("먼저 authenticate()를 호출해주세요.")

        try:
            response = self.service.blogs().listByUser(userId='self').execute()
            blogs = response.get('items', [])

            return [{
                'id': blog['id'],
                'name': blog['name'],
                'url': blog['url'],
                'posts_count': blog.get('posts', {}).get('totalItems', 0)
            } for blog in blogs]

        except Exception as e:
            raise Exception(f"블로그 목록 조회 실패: {str(e)}")

    def set_blog(self, blog_id: str):
        """사용할 블로그 ID 설정"""
        self.blog_id = blog_id

    def create_post(
        self,
        title: str,
        content: str,
        labels: List[str] = None,
        is_draft: bool = False,
        scheduled_time: Optional[datetime] = None
    ) -> Dict:
        """
        블로그 글 발행

        Args:
            title: 글 제목
            content: 글 본문 (HTML)
            labels: 라벨/태그 리스트
            is_draft: 초안으로 저장 여부
            scheduled_time: 예약 발행 시간 (None이면 즉시 발행)

        Returns:
            생성된 글 정보
        """
        if not self.service:
            raise Exception("먼저 authenticate()를 호출해주세요.")

        if not self.blog_id:
            raise ValueError("blog_id가 설정되지 않았습니다. set_blog()를 호출하거나 BLOGGER_BLOG_ID 환경변수를 설정해주세요.")

        post_body = {
            'kind': 'blogger#post',
            'blog': {'id': self.blog_id},
            'title': title,
            'content': content
        }

        if labels:
            post_body['labels'] = labels

        try:
            if is_draft:
                # 초안으로 저장
                response = self.service.posts().insert(
                    blogId=self.blog_id,
                    body=post_body,
                    isDraft=True
                ).execute()
            elif scheduled_time:
                # 예약 발행
                post_body['published'] = scheduled_time.isoformat()
                response = self.service.posts().insert(
                    blogId=self.blog_id,
                    body=post_body
                ).execute()
            else:
                # 즉시 발행
                response = self.service.posts().insert(
                    blogId=self.blog_id,
                    body=post_body
                ).execute()

            return {
                'id': response['id'],
                'url': response.get('url', ''),
                'title': response['title'],
                'published': response.get('published', ''),
                'status': 'draft' if is_draft else 'published'
            }

        except Exception as e:
            raise Exception(f"글 발행 실패: {str(e)}")

    def update_post(
        self,
        post_id: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
        labels: Optional[List[str]] = None
    ) -> Dict:
        """
        기존 글 수정

        Args:
            post_id: 수정할 글 ID
            title: 새 제목 (None이면 유지)
            content: 새 본문 (None이면 유지)
            labels: 새 라벨 (None이면 유지)

        Returns:
            수정된 글 정보
        """
        if not self.service:
            raise Exception("먼저 authenticate()를 호출해주세요.")

        if not self.blog_id:
            raise ValueError("blog_id가 설정되지 않았습니다.")

        # 기존 글 가져오기
        existing = self.service.posts().get(
            blogId=self.blog_id,
            postId=post_id
        ).execute()

        # 업데이트할 필드만 변경
        if title:
            existing['title'] = title
        if content:
            existing['content'] = content
        if labels is not None:
            existing['labels'] = labels

        try:
            response = self.service.posts().update(
                blogId=self.blog_id,
                postId=post_id,
                body=existing
            ).execute()

            return {
                'id': response['id'],
                'url': response.get('url', ''),
                'title': response['title'],
                'updated': response.get('updated', '')
            }

        except Exception as e:
            raise Exception(f"글 수정 실패: {str(e)}")

    def delete_post(self, post_id: str) -> bool:
        """
        글 삭제

        Args:
            post_id: 삭제할 글 ID

        Returns:
            삭제 성공 여부
        """
        if not self.service:
            raise Exception("먼저 authenticate()를 호출해주세요.")

        if not self.blog_id:
            raise ValueError("blog_id가 설정되지 않았습니다.")

        try:
            self.service.posts().delete(
                blogId=self.blog_id,
                postId=post_id
            ).execute()
            return True

        except Exception as e:
            raise Exception(f"글 삭제 실패: {str(e)}")

    def get_posts(self, max_results: int = 10, status: str = 'live') -> List[Dict]:
        """
        블로그 글 목록 가져오기

        Args:
            max_results: 최대 결과 수
            status: 상태 (live, draft, scheduled)

        Returns:
            글 목록
        """
        if not self.service:
            raise Exception("먼저 authenticate()를 호출해주세요.")

        if not self.blog_id:
            raise ValueError("blog_id가 설정되지 않았습니다.")

        try:
            response = self.service.posts().list(
                blogId=self.blog_id,
                maxResults=max_results,
                status=status
            ).execute()

            posts = response.get('items', [])

            return [{
                'id': post['id'],
                'title': post['title'],
                'url': post.get('url', ''),
                'published': post.get('published', ''),
                'labels': post.get('labels', [])
            } for post in posts]

        except Exception as e:
            raise Exception(f"글 목록 조회 실패: {str(e)}")

    def get_post_stats(self, post_id: str) -> Optional[Dict]:
        """
        글 통계 가져오기 (조회수 등)

        Args:
            post_id: 글 ID

        Returns:
            글 통계
        """
        if not self.service:
            raise Exception("먼저 authenticate()를 호출해주세요.")

        if not self.blog_id:
            raise ValueError("blog_id가 설정되지 않았습니다.")

        try:
            response = self.service.posts().get(
                blogId=self.blog_id,
                postId=post_id,
                view='READER'
            ).execute()

            return {
                'id': response['id'],
                'title': response['title'],
                'url': response.get('url', ''),
                'published': response.get('published', ''),
                'replies_count': response.get('replies', {}).get('totalItems', 0)
            }

        except Exception as e:
            return None


class BlogPostQueue:
    """블로그 글 발행 큐 관리"""

    def __init__(self, queue_file: str = 'blog_queue.json'):
        self.queue_file = queue_file
        self.queue = self._load_queue()

    def _load_queue(self) -> List[Dict]:
        """큐 파일 로드"""
        if os.path.exists(self.queue_file):
            with open(self.queue_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def _save_queue(self):
        """큐 파일 저장"""
        with open(self.queue_file, 'w', encoding='utf-8') as f:
            json.dump(self.queue, f, ensure_ascii=False, indent=2)

    def add(self, post_data: Dict, priority: int = 0):
        """
        발행 큐에 글 추가

        Args:
            post_data: 글 데이터 (title, content, labels 등)
            priority: 우선순위 (높을수록 먼저 발행)
        """
        entry = {
            'id': len(self.queue) + 1,
            'data': post_data,
            'priority': priority,
            'status': 'pending',
            'created_at': datetime.now().isoformat(),
            'published_at': None
        }
        self.queue.append(entry)
        self._save_queue()
        return entry['id']

    def get_next(self) -> Optional[Dict]:
        """다음 발행할 글 가져오기"""
        pending = [q for q in self.queue if q['status'] == 'pending']
        if not pending:
            return None

        # 우선순위 순으로 정렬
        pending.sort(key=lambda x: (-x['priority'], x['created_at']))
        return pending[0]

    def mark_published(self, queue_id: int, post_url: str):
        """발행 완료 표시"""
        for item in self.queue:
            if item['id'] == queue_id:
                item['status'] = 'published'
                item['published_at'] = datetime.now().isoformat()
                item['post_url'] = post_url
                break
        self._save_queue()

    def mark_failed(self, queue_id: int, error: str):
        """발행 실패 표시"""
        for item in self.queue:
            if item['id'] == queue_id:
                item['status'] = 'failed'
                item['error'] = error
                break
        self._save_queue()

    def get_pending_count(self) -> int:
        """대기 중인 글 수"""
        return len([q for q in self.queue if q['status'] == 'pending'])

    def get_published_count(self) -> int:
        """발행 완료된 글 수"""
        return len([q for q in self.queue if q['status'] == 'published'])

    def clear_published(self):
        """발행 완료된 항목 정리"""
        self.queue = [q for q in self.queue if q['status'] != 'published']
        self._save_queue()


# 테스트용
if __name__ == "__main__":
    client = BloggerClient()

    if client.is_available():
        print("Blogger API is available!")
        if client.is_configured():
            print("Credentials file found.")
            # 인증 테스트
            # client.authenticate()
            # blogs = client.get_blogs()
            # print(blogs)
        else:
            print("Please provide credentials.json file.")
    else:
        print("Please install: pip install google-api-python-client google-auth-oauthlib")
