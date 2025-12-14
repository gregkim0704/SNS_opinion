"""
유튜브 대본/자막 추출 모듈
유튜브 영상에서 자막을 추출하여 블로그 콘텐츠로 재가공합니다.
"""
import os
import re
from typing import Dict, List, Optional
from urllib.parse import urlparse, parse_qs

try:
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
    YOUTUBE_API_AVAILABLE = True
except ImportError:
    YOUTUBE_API_AVAILABLE = False

try:
    from googleapiclient.discovery import build
    YOUTUBE_DATA_API_AVAILABLE = True
except ImportError:
    YOUTUBE_DATA_API_AVAILABLE = False

from dotenv import load_dotenv

load_dotenv()


class YouTubeExtractor:
    """유튜브 대본/자막 추출기"""

    def __init__(self):
        self.youtube_api_key = os.getenv('YOUTUBE_API_KEY')
        self.youtube_client = None

        if self.youtube_api_key and YOUTUBE_DATA_API_AVAILABLE:
            try:
                self.youtube_client = build('youtube', 'v3', developerKey=self.youtube_api_key)
            except Exception:
                pass

    def is_configured(self) -> bool:
        """API 설정 여부 확인"""
        return YOUTUBE_API_AVAILABLE

    def extract_video_id(self, url: str) -> Optional[str]:
        """
        유튜브 URL에서 비디오 ID 추출

        지원 형식:
        - https://www.youtube.com/watch?v=VIDEO_ID
        - https://youtu.be/VIDEO_ID
        - https://www.youtube.com/embed/VIDEO_ID
        """
        if not url:
            return None

        # 이미 video_id인 경우
        if len(url) == 11 and re.match(r'^[a-zA-Z0-9_-]+$', url):
            return url

        parsed = urlparse(url)

        # youtube.com/watch?v=VIDEO_ID
        if 'youtube.com' in parsed.netloc:
            if parsed.path == '/watch':
                query = parse_qs(parsed.query)
                return query.get('v', [None])[0]
            elif parsed.path.startswith('/embed/'):
                return parsed.path.split('/')[2]
            elif parsed.path.startswith('/v/'):
                return parsed.path.split('/')[2]

        # youtu.be/VIDEO_ID
        if 'youtu.be' in parsed.netloc:
            return parsed.path[1:].split('?')[0]

        return None

    def get_transcript(
        self,
        video_url: str,
        languages: List[str] = ['ko', 'en']
    ) -> Dict:
        """
        유튜브 영상의 자막/대본 추출

        Args:
            video_url: 유튜브 URL 또는 비디오 ID
            languages: 선호 언어 순서

        Returns:
            추출된 대본 데이터
        """
        if not YOUTUBE_API_AVAILABLE:
            raise ImportError("youtube_transcript_api가 설치되지 않았습니다. pip install youtube-transcript-api")

        video_id = self.extract_video_id(video_url)
        if not video_id:
            raise ValueError(f"유효하지 않은 유튜브 URL입니다: {video_url}")

        try:
            # 자막 목록 가져오기
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

            # 선호 언어로 자막 찾기
            transcript = None
            used_language = None

            # 수동 자막 우선 시도
            for lang in languages:
                try:
                    transcript = transcript_list.find_manually_created_transcript([lang])
                    used_language = lang
                    break
                except NoTranscriptFound:
                    continue

            # 자동 생성 자막 시도
            if not transcript:
                for lang in languages:
                    try:
                        transcript = transcript_list.find_generated_transcript([lang])
                        used_language = lang
                        break
                    except NoTranscriptFound:
                        continue

            # 아무 자막이나 가져오기
            if not transcript:
                for t in transcript_list:
                    transcript = t
                    used_language = t.language_code
                    break

            if not transcript:
                raise NoTranscriptFound(video_id, languages, None)

            # 자막 데이터 추출
            transcript_data = transcript.fetch()

            # 전체 텍스트로 결합
            full_text = ' '.join([entry['text'] for entry in transcript_data])

            # 타임스탬프 포함 데이터
            timestamped = []
            for entry in transcript_data:
                timestamped.append({
                    'start': entry['start'],
                    'duration': entry['duration'],
                    'text': entry['text']
                })

            return {
                'video_id': video_id,
                'language': used_language,
                'is_generated': transcript.is_generated,
                'full_text': full_text,
                'timestamped': timestamped,
                'word_count': len(full_text.split()),
                'duration_seconds': timestamped[-1]['start'] + timestamped[-1]['duration'] if timestamped else 0
            }

        except TranscriptsDisabled:
            raise Exception(f"이 영상({video_id})은 자막이 비활성화되어 있습니다.")
        except NoTranscriptFound:
            raise Exception(f"이 영상({video_id})에서 사용 가능한 자막을 찾을 수 없습니다.")
        except Exception as e:
            raise Exception(f"자막 추출 실패: {str(e)}")

    def get_video_info(self, video_url: str) -> Optional[Dict]:
        """
        유튜브 영상 정보 가져오기 (YouTube Data API 필요)

        Args:
            video_url: 유튜브 URL 또는 비디오 ID

        Returns:
            영상 정보 (제목, 설명, 조회수 등)
        """
        if not self.youtube_client:
            return None

        video_id = self.extract_video_id(video_url)
        if not video_id:
            return None

        try:
            response = self.youtube_client.videos().list(
                part='snippet,statistics,contentDetails',
                id=video_id
            ).execute()

            if not response.get('items'):
                return None

            item = response['items'][0]
            snippet = item['snippet']
            statistics = item.get('statistics', {})

            return {
                'video_id': video_id,
                'title': snippet.get('title', ''),
                'description': snippet.get('description', ''),
                'channel_title': snippet.get('channelTitle', ''),
                'published_at': snippet.get('publishedAt', ''),
                'tags': snippet.get('tags', []),
                'view_count': int(statistics.get('viewCount', 0)),
                'like_count': int(statistics.get('likeCount', 0)),
                'comment_count': int(statistics.get('commentCount', 0))
            }

        except Exception as e:
            return None

    def search_trending_videos(
        self,
        query: str,
        max_results: int = 10,
        order: str = 'viewCount'
    ) -> List[Dict]:
        """
        인기 유튜브 영상 검색

        Args:
            query: 검색 키워드
            max_results: 최대 결과 수
            order: 정렬 기준 (viewCount, date, rating, relevance)

        Returns:
            검색된 영상 리스트
        """
        if not self.youtube_client:
            raise ValueError("YouTube Data API 키가 설정되지 않았습니다.")

        try:
            response = self.youtube_client.search().list(
                part='snippet',
                q=query,
                type='video',
                order=order,
                maxResults=max_results,
                regionCode='KR',
                relevanceLanguage='ko'
            ).execute()

            videos = []
            for item in response.get('items', []):
                video_id = item['id']['videoId']
                snippet = item['snippet']

                videos.append({
                    'video_id': video_id,
                    'url': f"https://www.youtube.com/watch?v={video_id}",
                    'title': snippet.get('title', ''),
                    'description': snippet.get('description', ''),
                    'channel_title': snippet.get('channelTitle', ''),
                    'published_at': snippet.get('publishedAt', '')
                })

            return videos

        except Exception as e:
            raise Exception(f"영상 검색 실패: {str(e)}")

    def extract_and_prepare(
        self,
        video_url: str,
        languages: List[str] = ['ko', 'en']
    ) -> Dict:
        """
        유튜브 영상에서 대본을 추출하고 블로그용으로 준비

        Args:
            video_url: 유튜브 URL
            languages: 선호 언어

        Returns:
            블로그 재가공용 데이터
        """
        # 대본 추출
        transcript = self.get_transcript(video_url, languages)

        # 영상 정보 가져오기 (가능한 경우)
        video_info = self.get_video_info(video_url)

        result = {
            'video_id': transcript['video_id'],
            'video_url': f"https://www.youtube.com/watch?v={transcript['video_id']}",
            'transcript': transcript['full_text'],
            'language': transcript['language'],
            'word_count': transcript['word_count'],
            'is_auto_generated': transcript['is_generated']
        }

        if video_info:
            result['title'] = video_info['title']
            result['channel'] = video_info['channel_title']
            result['view_count'] = video_info['view_count']
            result['original_tags'] = video_info['tags']
        else:
            result['title'] = None
            result['channel'] = None
            result['view_count'] = None
            result['original_tags'] = []

        return result


# 테스트용
if __name__ == "__main__":
    extractor = YouTubeExtractor()

    if extractor.is_configured():
        print("YouTube Extractor is configured!")
        # 테스트 (실제 영상 ID 필요)
        # result = extractor.get_transcript("dQw4w9WgXcQ")  # Never Gonna Give You Up
        # print(result)
    else:
        print("Please install youtube-transcript-api: pip install youtube-transcript-api")
