"""
AI 블로그 글 생성 모듈
OpenAI API를 사용하여 키워드 기반 블로그 콘텐츠를 자동 생성합니다.
"""
import os
import json
from typing import Optional, Dict, List
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class AIBlogGenerator:
    """AI 블로그 글 생성기"""

    def __init__(self):
        self.client = None
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            self.client = OpenAI(api_key=api_key)
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')

    def is_configured(self) -> bool:
        """API 설정 여부 확인"""
        return self.client is not None

    def generate_blog_post(
        self,
        keyword: str,
        style: str = "informative",
        tone: str = "friendly",
        length: str = "medium",
        include_seo: bool = True
    ) -> Dict:
        """
        키워드를 기반으로 블로그 글 생성

        Args:
            keyword: 주요 키워드
            style: 글 스타일 (informative, storytelling, tutorial, review, listicle)
            tone: 어조 (friendly, professional, casual, humorous)
            length: 글 길이 (short: ~500자, medium: ~1000자, long: ~2000자)
            include_seo: SEO 최적화 포함 여부

        Returns:
            생성된 블로그 글 데이터
        """
        if not self.client:
            raise ValueError("OpenAI API 키가 설정되지 않았습니다.")

        length_guide = {
            "short": "약 500자 분량으로",
            "medium": "약 1000자 분량으로",
            "long": "약 2000자 분량으로"
        }

        style_guide = {
            "informative": "정보 전달 위주의 교육적인 글",
            "storytelling": "스토리텔링 형식의 몰입감 있는 글",
            "tutorial": "단계별 튜토리얼/가이드 형식의 글",
            "review": "리뷰/평가 형식의 글",
            "listicle": "리스트 형식(~가지 방법, ~가지 팁 등)의 글"
        }

        tone_guide = {
            "friendly": "친근하고 따뜻한 어조",
            "professional": "전문적이고 신뢰감 있는 어조",
            "casual": "편안하고 일상적인 어조",
            "humorous": "유머러스하고 재미있는 어조"
        }

        seo_instruction = """
SEO 최적화를 위해 다음을 포함해주세요:
- 키워드가 제목과 본문에 자연스럽게 포함
- H2, H3 등 적절한 소제목 구조
- 검색 의도에 맞는 답변 제공
- 메타 설명용 요약문(160자 이내)
""" if include_seo else ""

        prompt = f"""
당신은 전문 블로그 작가입니다. 다음 조건에 맞는 블로그 글을 작성해주세요.

[키워드]: {keyword}
[스타일]: {style_guide.get(style, style_guide['informative'])}
[어조]: {tone_guide.get(tone, tone_guide['friendly'])}
[분량]: {length_guide.get(length, length_guide['medium'])}

{seo_instruction}

다음 JSON 형식으로 응답해주세요:
{{
    "title": "블로그 제목 (눈길을 끄는 제목)",
    "meta_description": "메타 설명 (160자 이내, SEO용)",
    "content": "본문 (HTML 형식, <h2>, <h3>, <p>, <ul>, <li> 등 사용)",
    "tags": ["태그1", "태그2", "태그3"],
    "summary": "요약문 (2-3문장)",
    "thread_hook": "쓰레드용 훅 (흥미를 끄는 1-2문장, 이모지 포함)"
}}

중요:
1. 실제로 유용하고 가치 있는 정보를 제공하세요
2. 독자의 관심을 끌 수 있는 제목을 작성하세요
3. 자연스러운 한국어로 작성하세요
4. 쓰레드용 훅은 블로그 링크와 함께 올릴 짧은 티저입니다
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "당신은 SEO에 최적화된 블로그 콘텐츠를 작성하는 전문 작가입니다. 항상 JSON 형식으로 응답합니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)
            result['keyword'] = keyword
            result['style'] = style
            result['tone'] = tone
            result['length'] = length

            return result

        except Exception as e:
            raise Exception(f"블로그 글 생성 실패: {str(e)}")

    def rewrite_youtube_script(
        self,
        script: str,
        target_keyword: Optional[str] = None,
        style: str = "informative"
    ) -> Dict:
        """
        유튜브 대본을 블로그 글로 재가공

        Args:
            script: 유튜브 대본/자막 텍스트
            target_keyword: 타겟 키워드 (없으면 자동 추출)
            style: 글 스타일

        Returns:
            재가공된 블로그 글 데이터
        """
        if not self.client:
            raise ValueError("OpenAI API 키가 설정되지 않았습니다.")

        prompt = f"""
다음 유튜브 대본/자막을 블로그 글로 재가공해주세요.

[원본 대본]:
{script[:4000]}  # 토큰 제한을 위해 앞부분만

[타겟 키워드]: {target_keyword if target_keyword else "대본에서 핵심 키워드를 추출해주세요"}

다음을 수행해주세요:
1. 구어체를 문어체로 자연스럽게 변환
2. 반복되는 내용 정리
3. 논리적 흐름에 맞게 재구성
4. SEO 최적화된 제목과 소제목 추가
5. 블로그에 적합한 형식으로 변환

다음 JSON 형식으로 응답해주세요:
{{
    "title": "블로그 제목",
    "meta_description": "메타 설명 (160자 이내)",
    "content": "본문 (HTML 형식)",
    "tags": ["태그1", "태그2", "태그3"],
    "summary": "요약문",
    "thread_hook": "쓰레드용 훅 (흥미를 끄는 1-2문장, 이모지 포함)",
    "extracted_keyword": "추출된 핵심 키워드"
}}
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "당신은 유튜브 콘텐츠를 블로그 글로 전문적으로 재가공하는 작가입니다. 항상 JSON 형식으로 응답합니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)
            result['source'] = 'youtube_rewrite'
            result['original_length'] = len(script)

            return result

        except Exception as e:
            raise Exception(f"대본 재가공 실패: {str(e)}")

    def generate_thread_content(
        self,
        blog_url: str,
        blog_title: str,
        blog_summary: str,
        style: str = "viral"
    ) -> Dict:
        """
        블로그 글을 기반으로 쓰레드 게시물 생성

        Args:
            blog_url: 블로그 URL
            blog_title: 블로그 제목
            blog_summary: 블로그 요약
            style: 스타일 (viral, informative, question, teaser)

        Returns:
            쓰레드 게시물 데이터
        """
        if not self.client:
            raise ValueError("OpenAI API 키가 설정되지 않았습니다.")

        style_guide = {
            "viral": "바이럴될 수 있는 충격적/흥미로운 훅",
            "informative": "정보를 미리 맛보기로 제공하는 스타일",
            "question": "질문으로 시작해서 호기심 유발",
            "teaser": "티저처럼 핵심만 살짝 공개"
        }

        prompt = f"""
다음 블로그 글을 홍보할 쓰레드(Threads) 게시물을 작성해주세요.

[블로그 제목]: {blog_title}
[블로그 요약]: {blog_summary}
[블로그 URL]: {blog_url}
[스타일]: {style_guide.get(style, style_guide['viral'])}

쓰레드 특성:
- 최대 500자
- 이모지 적극 활용
- 짧고 임팩트 있게
- 클릭 유도 (블로그 링크로 유입)

다음 JSON 형식으로 응답해주세요:
{{
    "main_post": "메인 게시물 내용 (500자 이내)",
    "alternative_hooks": ["대안 훅1", "대안 훅2", "대안 훅3"],
    "hashtags": ["#해시태그1", "#해시태그2"]
}}
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "당신은 바이럴 소셜 미디어 콘텐츠 전문가입니다. 조회수 10만 이상 터지는 게시물을 작성합니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)
            result['blog_url'] = blog_url

            return result

        except Exception as e:
            raise Exception(f"쓰레드 콘텐츠 생성 실패: {str(e)}")

    def generate_batch_posts(
        self,
        keywords: List[str],
        style: str = "informative",
        tone: str = "friendly"
    ) -> List[Dict]:
        """
        여러 키워드에 대해 배치로 블로그 글 생성

        Args:
            keywords: 키워드 리스트
            style: 글 스타일
            tone: 어조

        Returns:
            생성된 블로그 글 리스트
        """
        results = []
        for keyword in keywords:
            try:
                post = self.generate_blog_post(keyword, style=style, tone=tone)
                results.append({"status": "success", "data": post})
            except Exception as e:
                results.append({"status": "error", "keyword": keyword, "error": str(e)})

        return results


# 테스트용
if __name__ == "__main__":
    generator = AIBlogGenerator()

    if generator.is_configured():
        print("AI Generator is configured!")
        # 테스트 생성
        result = generator.generate_blog_post(
            keyword="부업으로 월 100만원 버는 방법",
            style="listicle",
            tone="friendly"
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("Please set OPENAI_API_KEY in .env file")
