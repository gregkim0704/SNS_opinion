"""
Meta Threads API 연동 모듈
쓰레드(Threads)에 자동으로 게시물을 발행합니다.
"""
import os
import json
import requests
from typing import Dict, List, Optional
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()


class ThreadsClient:
    """Meta Threads API 클라이언트"""

    BASE_URL = "https://graph.threads.net/v1.0"

    def __init__(self):
        self.access_token = os.getenv('THREADS_ACCESS_TOKEN')
        self.user_id = os.getenv('THREADS_USER_ID')

    def is_configured(self) -> bool:
        """API 설정 여부 확인"""
        return bool(self.access_token and self.user_id)

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Dict = None,
        data: Dict = None
    ) -> Dict:
        """API 요청 수행"""
        url = f"{self.BASE_URL}/{endpoint}"

        if params is None:
            params = {}
        params['access_token'] = self.access_token

        try:
            if method == 'GET':
                response = requests.get(url, params=params)
            elif method == 'POST':
                response = requests.post(url, params=params, json=data)
            else:
                raise ValueError(f"지원하지 않는 HTTP 메서드: {method}")

            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as e:
            error_data = e.response.json() if e.response.content else {}
            raise Exception(f"API 오류: {error_data.get('error', {}).get('message', str(e))}")
        except Exception as e:
            raise Exception(f"요청 실패: {str(e)}")

    def get_profile(self) -> Dict:
        """
        사용자 프로필 정보 가져오기

        Returns:
            프로필 정보
        """
        if not self.is_configured():
            raise ValueError("Threads API가 설정되지 않았습니다.")

        response = self._make_request(
            'GET',
            f"{self.user_id}",
            params={'fields': 'id,username,threads_profile_picture_url,threads_biography'}
        )

        return {
            'id': response.get('id'),
            'username': response.get('username'),
            'profile_picture': response.get('threads_profile_picture_url'),
            'bio': response.get('threads_biography')
        }

    def create_text_post(self, text: str) -> Dict:
        """
        텍스트 게시물 생성

        Args:
            text: 게시물 내용 (최대 500자)

        Returns:
            생성된 게시물 정보
        """
        if not self.is_configured():
            raise ValueError("Threads API가 설정되지 않았습니다.")

        if len(text) > 500:
            text = text[:497] + "..."

        # 1단계: 미디어 컨테이너 생성
        container_response = self._make_request(
            'POST',
            f"{self.user_id}/threads",
            params={
                'media_type': 'TEXT',
                'text': text
            }
        )

        container_id = container_response.get('id')
        if not container_id:
            raise Exception("미디어 컨테이너 생성 실패")

        # 2단계: 게시물 발행
        publish_response = self._make_request(
            'POST',
            f"{self.user_id}/threads_publish",
            params={'creation_id': container_id}
        )

        post_id = publish_response.get('id')

        return {
            'id': post_id,
            'container_id': container_id,
            'text': text,
            'created_at': datetime.now().isoformat()
        }

    def create_link_post(self, text: str, link_url: str) -> Dict:
        """
        링크 포함 게시물 생성

        Args:
            text: 게시물 내용
            link_url: 포함할 링크 URL

        Returns:
            생성된 게시물 정보
        """
        # Threads에서 링크는 텍스트에 포함
        full_text = f"{text}\n\n{link_url}"
        return self.create_text_post(full_text)

    def create_image_post(self, text: str, image_url: str) -> Dict:
        """
        이미지 포함 게시물 생성

        Args:
            text: 게시물 내용
            image_url: 이미지 URL (공개 접근 가능해야 함)

        Returns:
            생성된 게시물 정보
        """
        if not self.is_configured():
            raise ValueError("Threads API가 설정되지 않았습니다.")

        # 1단계: 미디어 컨테이너 생성
        container_response = self._make_request(
            'POST',
            f"{self.user_id}/threads",
            params={
                'media_type': 'IMAGE',
                'image_url': image_url,
                'text': text[:500] if len(text) > 500 else text
            }
        )

        container_id = container_response.get('id')
        if not container_id:
            raise Exception("미디어 컨테이너 생성 실패")

        # 2단계: 게시물 발행
        publish_response = self._make_request(
            'POST',
            f"{self.user_id}/threads_publish",
            params={'creation_id': container_id}
        )

        return {
            'id': publish_response.get('id'),
            'container_id': container_id,
            'text': text,
            'image_url': image_url,
            'created_at': datetime.now().isoformat()
        }

    def get_post_insights(self, post_id: str) -> Dict:
        """
        게시물 인사이트/통계 가져오기

        Args:
            post_id: 게시물 ID

        Returns:
            인사이트 데이터
        """
        if not self.is_configured():
            raise ValueError("Threads API가 설정되지 않았습니다.")

        response = self._make_request(
            'GET',
            f"{post_id}/insights",
            params={'metric': 'views,likes,replies,reposts,quotes'}
        )

        metrics = {}
        for item in response.get('data', []):
            metrics[item['name']] = item['values'][0]['value']

        return {
            'post_id': post_id,
            'views': metrics.get('views', 0),
            'likes': metrics.get('likes', 0),
            'replies': metrics.get('replies', 0),
            'reposts': metrics.get('reposts', 0),
            'quotes': metrics.get('quotes', 0)
        }

    def get_user_threads(self, limit: int = 10) -> List[Dict]:
        """
        사용자의 게시물 목록 가져오기

        Args:
            limit: 가져올 게시물 수

        Returns:
            게시물 리스트
        """
        if not self.is_configured():
            raise ValueError("Threads API가 설정되지 않았습니다.")

        response = self._make_request(
            'GET',
            f"{self.user_id}/threads",
            params={
                'fields': 'id,text,timestamp,media_type,permalink',
                'limit': limit
            }
        )

        return [{
            'id': item.get('id'),
            'text': item.get('text'),
            'timestamp': item.get('timestamp'),
            'media_type': item.get('media_type'),
            'permalink': item.get('permalink')
        } for item in response.get('data', [])]


class ThreadsPostScheduler:
    """쓰레드 게시물 스케줄링 관리"""

    def __init__(self, schedule_file: str = 'threads_schedule.json'):
        self.schedule_file = schedule_file
        self.schedule = self._load_schedule()

    def _load_schedule(self) -> List[Dict]:
        """스케줄 파일 로드"""
        if os.path.exists(self.schedule_file):
            with open(self.schedule_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def _save_schedule(self):
        """스케줄 파일 저장"""
        with open(self.schedule_file, 'w', encoding='utf-8') as f:
            json.dump(self.schedule, f, ensure_ascii=False, indent=2)

    def add_post(
        self,
        text: str,
        blog_url: Optional[str] = None,
        scheduled_time: Optional[datetime] = None
    ):
        """
        게시물 스케줄에 추가

        Args:
            text: 게시물 내용
            blog_url: 블로그 링크 (있으면 포함)
            scheduled_time: 예약 시간 (없으면 다음 슬롯)
        """
        entry = {
            'id': len(self.schedule) + 1,
            'text': text,
            'blog_url': blog_url,
            'status': 'pending',
            'scheduled_time': scheduled_time.isoformat() if scheduled_time else None,
            'created_at': datetime.now().isoformat(),
            'posted_at': None,
            'post_id': None
        }
        self.schedule.append(entry)
        self._save_schedule()
        return entry['id']

    def get_pending(self) -> List[Dict]:
        """대기 중인 게시물 목록"""
        return [s for s in self.schedule if s['status'] == 'pending']

    def get_next_post(self) -> Optional[Dict]:
        """다음 발행할 게시물"""
        now = datetime.now()
        pending = self.get_pending()

        for post in pending:
            if post['scheduled_time']:
                scheduled = datetime.fromisoformat(post['scheduled_time'])
                if scheduled <= now:
                    return post
            else:
                return post

        return None

    def mark_posted(self, schedule_id: int, post_id: str):
        """발행 완료 표시"""
        for item in self.schedule:
            if item['id'] == schedule_id:
                item['status'] = 'posted'
                item['posted_at'] = datetime.now().isoformat()
                item['post_id'] = post_id
                break
        self._save_schedule()

    def mark_failed(self, schedule_id: int, error: str):
        """발행 실패 표시"""
        for item in self.schedule:
            if item['id'] == schedule_id:
                item['status'] = 'failed'
                item['error'] = error
                break
        self._save_schedule()


# 테스트용
if __name__ == "__main__":
    client = ThreadsClient()

    if client.is_configured():
        print("Threads API is configured!")
        # 테스트
        # profile = client.get_profile()
        # print(profile)
    else:
        print("Please set THREADS_ACCESS_TOKEN and THREADS_USER_ID in .env file")
        print("\n설정 방법:")
        print("1. Meta for Developers에서 앱 생성")
        print("2. Threads API 권한 추가")
        print("3. Access Token 발급")
        print("4. .env 파일에 설정")
