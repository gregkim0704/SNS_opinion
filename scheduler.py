"""
자동 발행 스케줄러 모듈
APScheduler를 사용하여 블로그와 쓰레드에 자동으로 콘텐츠를 발행합니다.
"""
import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable

try:
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.interval import IntervalTrigger
    from apscheduler.triggers.cron import CronTrigger
    SCHEDULER_AVAILABLE = True
except ImportError:
    SCHEDULER_AVAILABLE = False

from dotenv import load_dotenv

# 로컬 모듈 임포트
from ai_generator import AIBlogGenerator
from blogger_api import BloggerClient, BlogPostQueue
from threads_api import ThreadsClient, ThreadsPostScheduler

load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AutoPublisher:
    """자동 발행 관리자"""

    def __init__(self):
        self.ai_generator = AIBlogGenerator()
        self.blogger = BloggerClient()
        self.threads = ThreadsClient()
        self.blog_queue = BlogPostQueue()
        self.threads_scheduler = ThreadsPostScheduler()
        self.scheduler = None
        self.config = self._load_config()
        self.stats = self._load_stats()

    def _load_config(self) -> Dict:
        """설정 로드"""
        config_file = 'publisher_config.json'
        default_config = {
            'enabled': False,
            'blog_interval_hours': 3,
            'threads_interval_minutes': 60,
            'auto_generate': True,
            'keywords': [],
            'styles': ['informative', 'listicle', 'tutorial'],
            'tones': ['friendly', 'professional'],
            'max_daily_posts': 8,
            'working_hours': {'start': 9, 'end': 22},
            'post_to_threads': True,
            'thread_style': 'viral'
        }

        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
                default_config.update(loaded)

        return default_config

    def save_config(self):
        """설정 저장"""
        with open('publisher_config.json', 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)

    def _load_stats(self) -> Dict:
        """통계 로드"""
        stats_file = 'publisher_stats.json'
        default_stats = {
            'total_blog_posts': 0,
            'total_threads_posts': 0,
            'posts_today': 0,
            'last_post_date': None,
            'last_blog_post': None,
            'last_threads_post': None,
            'daily_history': []
        }

        if os.path.exists(stats_file):
            with open(stats_file, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
                default_stats.update(loaded)

        return default_stats

    def _save_stats(self):
        """통계 저장"""
        with open('publisher_stats.json', 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, ensure_ascii=False, indent=2)

    def _reset_daily_stats(self):
        """일일 통계 리셋 (자정에 호출)"""
        today = datetime.now().strftime('%Y-%m-%d')
        if self.stats['last_post_date'] != today:
            # 이전 날짜 기록
            if self.stats['last_post_date']:
                self.stats['daily_history'].append({
                    'date': self.stats['last_post_date'],
                    'posts': self.stats['posts_today']
                })
                # 최근 30일만 유지
                self.stats['daily_history'] = self.stats['daily_history'][-30:]

            self.stats['posts_today'] = 0
            self.stats['last_post_date'] = today
            self._save_stats()

    def can_post(self) -> bool:
        """현재 발행 가능 여부 확인"""
        self._reset_daily_stats()

        # 최대 일일 발행 수 체크
        if self.stats['posts_today'] >= self.config['max_daily_posts']:
            logger.info(f"일일 최대 발행 수({self.config['max_daily_posts']}) 도달")
            return False

        # 근무 시간 체크
        current_hour = datetime.now().hour
        start_hour = self.config['working_hours']['start']
        end_hour = self.config['working_hours']['end']

        if not (start_hour <= current_hour < end_hour):
            logger.info(f"근무 시간 외: {current_hour}시 (설정: {start_hour}-{end_hour}시)")
            return False

        return True

    def generate_and_queue_post(
        self,
        keyword: Optional[str] = None,
        style: Optional[str] = None,
        tone: Optional[str] = None
    ) -> Dict:
        """
        AI로 글 생성 후 큐에 추가

        Args:
            keyword: 키워드 (없으면 설정에서 랜덤 선택)
            style: 스타일 (없으면 설정에서 랜덤 선택)
            tone: 어조 (없으면 설정에서 랜덤 선택)

        Returns:
            생성된 글 정보
        """
        import random

        if not self.ai_generator.is_configured():
            raise Exception("OpenAI API가 설정되지 않았습니다.")

        # 기본값 설정
        if not keyword and self.config['keywords']:
            keyword = random.choice(self.config['keywords'])
        elif not keyword:
            raise ValueError("키워드가 필요합니다.")

        if not style:
            style = random.choice(self.config['styles'])
        if not tone:
            tone = random.choice(self.config['tones'])

        # AI로 글 생성
        logger.info(f"글 생성 시작: 키워드={keyword}, 스타일={style}, 어조={tone}")
        post_data = self.ai_generator.generate_blog_post(
            keyword=keyword,
            style=style,
            tone=tone,
            include_seo=True
        )

        # 큐에 추가
        queue_id = self.blog_queue.add(post_data)
        logger.info(f"큐에 추가됨: ID={queue_id}")

        return {
            'queue_id': queue_id,
            'title': post_data['title'],
            'keyword': keyword
        }

    def publish_blog_post(self) -> Optional[Dict]:
        """
        큐에서 다음 글을 가져와 블로그에 발행

        Returns:
            발행 결과 또는 None
        """
        if not self.can_post():
            return None

        # 큐에서 다음 글 가져오기
        next_post = self.blog_queue.get_next()
        if not next_post:
            logger.info("발행할 글이 없습니다.")
            return None

        post_data = next_post['data']
        queue_id = next_post['id']

        try:
            # Blogger 인증 확인
            if not self.blogger.is_authenticated():
                if self.blogger.is_configured():
                    self.blogger.authenticate()
                else:
                    raise Exception("Blogger API가 설정되지 않았습니다.")

            # 블로그에 발행
            result = self.blogger.create_post(
                title=post_data['title'],
                content=post_data['content'],
                labels=post_data.get('tags', [])
            )

            # 성공 처리
            self.blog_queue.mark_published(queue_id, result['url'])
            self.stats['total_blog_posts'] += 1
            self.stats['posts_today'] += 1
            self.stats['last_blog_post'] = {
                'title': post_data['title'],
                'url': result['url'],
                'time': datetime.now().isoformat()
            }
            self._save_stats()

            logger.info(f"블로그 발행 성공: {result['url']}")

            # 쓰레드에도 발행
            if self.config['post_to_threads'] and self.threads.is_configured():
                self._post_to_threads(
                    blog_url=result['url'],
                    blog_title=post_data['title'],
                    thread_hook=post_data.get('thread_hook', post_data.get('summary', ''))
                )

            return result

        except Exception as e:
            self.blog_queue.mark_failed(queue_id, str(e))
            logger.error(f"블로그 발행 실패: {str(e)}")
            return None

    def _post_to_threads(
        self,
        blog_url: str,
        blog_title: str,
        thread_hook: str
    ):
        """블로그 글을 쓰레드에 홍보"""
        try:
            # 쓰레드용 텍스트 생성
            if thread_hook:
                text = f"{thread_hook}\n\n{blog_url}"
            else:
                text = f"새 글이 올라왔어요!\n\n📖 {blog_title}\n\n{blog_url}"

            result = self.threads.create_text_post(text)

            self.stats['total_threads_posts'] += 1
            self.stats['last_threads_post'] = {
                'text': text[:100],
                'time': datetime.now().isoformat()
            }
            self._save_stats()

            logger.info(f"쓰레드 발행 성공: {result['id']}")

        except Exception as e:
            logger.error(f"쓰레드 발행 실패: {str(e)}")

    def start_scheduler(self):
        """스케줄러 시작"""
        if not SCHEDULER_AVAILABLE:
            raise ImportError("APScheduler가 설치되지 않았습니다. pip install apscheduler")

        if self.scheduler and self.scheduler.running:
            logger.warning("스케줄러가 이미 실행 중입니다.")
            return

        self.scheduler = BackgroundScheduler()

        # 블로그 발행 작업 추가 (기본 3시간마다)
        blog_interval = self.config.get('blog_interval_hours', 3)
        self.scheduler.add_job(
            self._scheduled_blog_publish,
            IntervalTrigger(hours=blog_interval),
            id='blog_publish',
            name='블로그 자동 발행',
            replace_existing=True
        )

        # 자동 생성 작업 (큐가 비면 글 생성)
        if self.config.get('auto_generate', True):
            self.scheduler.add_job(
                self._scheduled_generate,
                IntervalTrigger(hours=1),
                id='auto_generate',
                name='자동 글 생성',
                replace_existing=True
            )

        # 일일 통계 리셋 (자정)
        self.scheduler.add_job(
            self._reset_daily_stats,
            CronTrigger(hour=0, minute=0),
            id='daily_reset',
            name='일일 통계 리셋',
            replace_existing=True
        )

        self.scheduler.start()
        self.config['enabled'] = True
        self.save_config()
        logger.info("스케줄러가 시작되었습니다.")

    def stop_scheduler(self):
        """스케줄러 중지"""
        if self.scheduler and self.scheduler.running:
            self.scheduler.shutdown()
            self.scheduler = None
            self.config['enabled'] = False
            self.save_config()
            logger.info("스케줄러가 중지되었습니다.")

    def _scheduled_blog_publish(self):
        """스케줄된 블로그 발행"""
        logger.info("스케줄된 블로그 발행 실행")
        self.publish_blog_post()

    def _scheduled_generate(self):
        """스케줄된 글 생성 (큐가 비면)"""
        if self.blog_queue.get_pending_count() < 3:
            if self.config['keywords']:
                logger.info("큐가 부족하여 자동 생성 실행")
                try:
                    self.generate_and_queue_post()
                except Exception as e:
                    logger.error(f"자동 생성 실패: {str(e)}")

    def get_status(self) -> Dict:
        """현재 상태 반환"""
        self._reset_daily_stats()

        return {
            'scheduler_running': self.scheduler.running if self.scheduler else False,
            'enabled': self.config['enabled'],
            'queue_pending': self.blog_queue.get_pending_count(),
            'queue_published': self.blog_queue.get_published_count(),
            'posts_today': self.stats['posts_today'],
            'max_daily_posts': self.config['max_daily_posts'],
            'total_blog_posts': self.stats['total_blog_posts'],
            'total_threads_posts': self.stats['total_threads_posts'],
            'last_blog_post': self.stats['last_blog_post'],
            'last_threads_post': self.stats['last_threads_post'],
            'next_run': self._get_next_run_time(),
            'api_status': {
                'openai': self.ai_generator.is_configured(),
                'blogger': self.blogger.is_configured(),
                'threads': self.threads.is_configured()
            }
        }

    def _get_next_run_time(self) -> Optional[str]:
        """다음 실행 시간 반환"""
        if not self.scheduler or not self.scheduler.running:
            return None

        job = self.scheduler.get_job('blog_publish')
        if job and job.next_run_time:
            return job.next_run_time.isoformat()
        return None


# 간단한 CLI
if __name__ == "__main__":
    import sys

    publisher = AutoPublisher()

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == 'status':
            status = publisher.get_status()
            print(json.dumps(status, ensure_ascii=False, indent=2))

        elif command == 'start':
            publisher.start_scheduler()
            print("스케줄러가 시작되었습니다.")
            # 메인 스레드 유지
            try:
                while True:
                    import time
                    time.sleep(60)
            except KeyboardInterrupt:
                publisher.stop_scheduler()
                print("\n스케줄러가 중지되었습니다.")

        elif command == 'generate':
            if len(sys.argv) > 2:
                keyword = sys.argv[2]
            else:
                keyword = input("키워드를 입력하세요: ")
            result = publisher.generate_and_queue_post(keyword=keyword)
            print(f"생성 완료: {result['title']}")

        elif command == 'publish':
            result = publisher.publish_blog_post()
            if result:
                print(f"발행 완료: {result['url']}")
            else:
                print("발행할 글이 없거나 조건에 맞지 않습니다.")

        else:
            print(f"알 수 없는 명령: {command}")
            print("사용법: python scheduler.py [status|start|generate|publish]")

    else:
        print("사용법: python scheduler.py [status|start|generate|publish]")
        print("\n현재 상태:")
        status = publisher.get_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))
