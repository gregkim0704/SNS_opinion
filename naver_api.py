"""
Naver API Integration Module
네이버 검색 API를 활용한 실시간 데이터 수집
"""

import requests
import os
from datetime import datetime

class NaverAPIClient:
    """네이버 검색 API 클라이언트"""

    def __init__(self, client_id=None, client_secret=None):
        """
        네이버 API 클라이언트 초기화

        Args:
            client_id: 네이버 API Client ID
            client_secret: 네이버 API Client Secret
        """
        self.client_id = client_id or os.getenv('NAVER_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('NAVER_CLIENT_SECRET')
        self.base_url = "https://openapi.naver.com/v1/search"

    def _make_request(self, endpoint, query, display=10, start=1, sort='sim'):
        """
        네이버 API 요청 실행

        Args:
            endpoint: API 엔드포인트 (blog, news, cafearticle, shop)
            query: 검색어
            display: 한 번에 표시할 검색 결과 개수 (최대 100)
            start: 검색 시작 위치 (최대 1000)
            sort: 정렬 옵션 (sim: 유사도순, date: 날짜순)

        Returns:
            dict: API 응답 데이터
        """
        if not self.client_id or not self.client_secret:
            raise ValueError("네이버 API 인증 정보가 설정되지 않았습니다.")

        headers = {
            "X-Naver-Client-Id": self.client_id,
            "X-Naver-Client-Secret": self.client_secret
        }

        params = {
            "query": query,
            "display": display,
            "start": start,
            "sort": sort
        }

        url = f"{self.base_url}/{endpoint}"

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API 요청 오류: {e}")
            return None

    def search_blogs(self, query, display=10, sort='date'):
        """
        네이버 블로그 검색

        Args:
            query: 검색어
            display: 결과 개수
            sort: 정렬 (sim: 정확도순, date: 날짜순)

        Returns:
            list: 블로그 포스트 리스트
        """
        result = self._make_request('blog', query, display, sort=sort)
        if not result or 'items' not in result:
            return []

        posts = []
        for item in result['items']:
            posts.append({
                'title': self._remove_html_tags(item.get('title', '')),
                'description': self._remove_html_tags(item.get('description', '')),
                'text': self._remove_html_tags(item.get('description', '')),
                'link': item.get('link', ''),
                'bloggername': item.get('bloggername', ''),
                'postdate': item.get('postdate', ''),
                'platform': 'Naver Blog',
                'date': self._format_date(item.get('postdate', ''))
            })

        return posts

    def search_news(self, query, display=10, sort='date'):
        """
        네이버 뉴스 검색

        Args:
            query: 검색어
            display: 결과 개수
            sort: 정렬 (sim: 정확도순, date: 날짜순)

        Returns:
            list: 뉴스 기사 리스트
        """
        result = self._make_request('news', query, display, sort=sort)
        if not result or 'items' not in result:
            return []

        articles = []
        for item in result['items']:
            articles.append({
                'title': self._remove_html_tags(item.get('title', '')),
                'description': self._remove_html_tags(item.get('description', '')),
                'text': self._remove_html_tags(item.get('description', '')),
                'link': item.get('originallink', item.get('link', '')),
                'pubDate': item.get('pubDate', ''),
                'platform': 'Naver News',
                'date': self._format_date(item.get('pubDate', ''))
            })

        return articles

    def search_cafearticle(self, query, display=10, sort='date'):
        """
        네이버 카페 글 검색

        Args:
            query: 검색어
            display: 결과 개수
            sort: 정렬 (sim: 정확도순, date: 날짜순)

        Returns:
            list: 카페 글 리스트
        """
        result = self._make_request('cafearticle', query, display, sort=sort)
        if not result or 'items' not in result:
            return []

        articles = []
        for item in result['items']:
            articles.append({
                'title': self._remove_html_tags(item.get('title', '')),
                'description': self._remove_html_tags(item.get('description', '')),
                'text': self._remove_html_tags(item.get('description', '')),
                'link': item.get('link', ''),
                'cafename': item.get('cafename', ''),
                'cafeurl': item.get('cafeurl', ''),
                'platform': 'Naver Cafe',
                'date': datetime.now().strftime('%Y-%m-%d')
            })

        return articles

    def search_shopping(self, query, display=10, sort='sim'):
        """
        네이버 쇼핑 검색 (상품 리뷰 수집용)

        Args:
            query: 검색어
            display: 결과 개수
            sort: 정렬 (sim: 정확도순, date: 날짜순, asc: 가격순, dsc: 가격역순)

        Returns:
            list: 상품 정보 리스트
        """
        result = self._make_request('shop', query, display, sort=sort)
        if not result or 'items' not in result:
            return []

        products = []
        for item in result['items']:
            products.append({
                'title': self._remove_html_tags(item.get('title', '')),
                'description': self._remove_html_tags(item.get('title', '')),
                'text': self._remove_html_tags(item.get('title', '')),
                'link': item.get('link', ''),
                'image': item.get('image', ''),
                'lprice': item.get('lprice', ''),
                'hprice': item.get('hprice', ''),
                'mallName': item.get('mallName', ''),
                'brand': item.get('brand', ''),
                'platform': 'Naver Shopping',
                'date': datetime.now().strftime('%Y-%m-%d')
            })

        return products

    def search_all(self, query, display=5):
        """
        모든 카테고리에서 통합 검색

        Args:
            query: 검색어
            display: 각 카테고리별 결과 개수

        Returns:
            dict: 카테고리별 결과
        """
        results = {
            'blogs': self.search_blogs(query, display),
            'news': self.search_news(query, display),
            'cafe': self.search_cafearticle(query, display),
            'shopping': self.search_shopping(query, display)
        }

        return results

    def _remove_html_tags(self, text):
        """HTML 태그 제거"""
        import re
        clean = re.compile('<.*?>')
        return re.sub(clean, '', text)

    def _format_date(self, date_str):
        """날짜 포맷 변환"""
        try:
            # YYYYMMDD 형식
            if len(date_str) == 8:
                return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
            # RFC 822 형식 (뉴스)
            elif ',' in date_str:
                from email.utils import parsedate_to_datetime
                dt = parsedate_to_datetime(date_str)
                return dt.strftime('%Y-%m-%d')
            else:
                return datetime.now().strftime('%Y-%m-%d')
        except:
            return datetime.now().strftime('%Y-%m-%d')


# 사용 예시
if __name__ == "__main__":
    # API 클라이언트 생성
    client = NaverAPIClient()

    # 블로그 검색
    blogs = client.search_blogs("맛집", display=5)
    print(f"블로그 검색 결과: {len(blogs)}개")

    # 뉴스 검색
    news = client.search_news("IT 트렌드", display=5)
    print(f"뉴스 검색 결과: {len(news)}개")

    # 통합 검색
    all_results = client.search_all("아이폰 15", display=3)
    print(f"통합 검색 완료")
