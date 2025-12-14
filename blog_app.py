"""
AI 블로그 자동화 앱 - 메인 Flask 애플리케이션
구글 블로그 + 쓰레드 + AI 자동 글 생성 시스템
"""
import os
import json
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_cors import CORS
from datetime import datetime
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 로컬 모듈 임포트
from ai_generator import AIBlogGenerator
from youtube_extractor import YouTubeExtractor
from blogger_api import BloggerClient, BlogPostQueue
from threads_api import ThreadsClient, ThreadsPostScheduler
from scheduler import AutoPublisher

app = Flask(__name__)
CORS(app)

# 모듈 초기화
ai_generator = AIBlogGenerator()
youtube_extractor = YouTubeExtractor()
blogger_client = BloggerClient()
threads_client = ThreadsClient()
blog_queue = BlogPostQueue()
auto_publisher = AutoPublisher()

# 생성된 글 임시 저장
generated_posts = []


@app.route('/')
def index():
    """메인 대시보드"""
    return render_template('blog_dashboard.html')


@app.route('/api/status')
def get_status():
    """시스템 상태 확인"""
    return jsonify({
        'openai': ai_generator.is_configured(),
        'youtube': youtube_extractor.is_configured(),
        'blogger': blogger_client.is_configured(),
        'blogger_authenticated': blogger_client.is_authenticated(),
        'threads': threads_client.is_configured(),
        'scheduler': auto_publisher.get_status()
    })


# ===== AI 글 생성 API =====

@app.route('/api/generate', methods=['POST'])
def generate_post():
    """키워드로 블로그 글 생성"""
    if not ai_generator.is_configured():
        return jsonify({'error': 'OpenAI API 키가 설정되지 않았습니다.'}), 400

    data = request.json
    keyword = data.get('keyword', '')
    style = data.get('style', 'informative')
    tone = data.get('tone', 'friendly')
    length = data.get('length', 'medium')

    if not keyword:
        return jsonify({'error': '키워드를 입력해주세요.'}), 400

    try:
        result = ai_generator.generate_blog_post(
            keyword=keyword,
            style=style,
            tone=tone,
            length=length,
            include_seo=True
        )

        # 생성된 글 저장
        result['id'] = len(generated_posts) + 1
        result['created_at'] = datetime.now().isoformat()
        generated_posts.append(result)

        return jsonify({
            'success': True,
            'post': result
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/generate/batch', methods=['POST'])
def generate_batch():
    """여러 키워드로 배치 생성"""
    if not ai_generator.is_configured():
        return jsonify({'error': 'OpenAI API 키가 설정되지 않았습니다.'}), 400

    data = request.json
    keywords = data.get('keywords', [])
    style = data.get('style', 'informative')
    tone = data.get('tone', 'friendly')

    if not keywords:
        return jsonify({'error': '키워드 리스트가 필요합니다.'}), 400

    try:
        results = ai_generator.generate_batch_posts(keywords, style=style, tone=tone)
        return jsonify({
            'success': True,
            'results': results
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/generated-posts')
def get_generated_posts():
    """생성된 글 목록"""
    return jsonify({
        'posts': generated_posts,
        'count': len(generated_posts)
    })


# ===== 유튜브 대본 추출 API =====

@app.route('/api/youtube/extract', methods=['POST'])
def extract_youtube():
    """유튜브 영상에서 대본 추출"""
    if not youtube_extractor.is_configured():
        return jsonify({'error': 'youtube-transcript-api가 설치되지 않았습니다.'}), 400

    data = request.json
    video_url = data.get('url', '')

    if not video_url:
        return jsonify({'error': '유튜브 URL을 입력해주세요.'}), 400

    try:
        result = youtube_extractor.extract_and_prepare(video_url)
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/youtube/rewrite', methods=['POST'])
def rewrite_youtube():
    """유튜브 대본을 블로그 글로 재가공"""
    if not ai_generator.is_configured():
        return jsonify({'error': 'OpenAI API 키가 설정되지 않았습니다.'}), 400

    data = request.json
    script = data.get('script', '')
    target_keyword = data.get('keyword', None)

    if not script:
        return jsonify({'error': '대본을 입력해주세요.'}), 400

    try:
        result = ai_generator.rewrite_youtube_script(script, target_keyword)

        # 생성된 글 저장
        result['id'] = len(generated_posts) + 1
        result['created_at'] = datetime.now().isoformat()
        generated_posts.append(result)

        return jsonify({
            'success': True,
            'post': result
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ===== 블로그 발행 API =====

@app.route('/api/queue/add', methods=['POST'])
def add_to_queue():
    """발행 큐에 글 추가"""
    data = request.json
    post_data = data.get('post', {})
    priority = data.get('priority', 0)

    if not post_data:
        return jsonify({'error': '글 데이터가 필요합니다.'}), 400

    queue_id = blog_queue.add(post_data, priority=priority)

    return jsonify({
        'success': True,
        'queue_id': queue_id,
        'pending_count': blog_queue.get_pending_count()
    })


@app.route('/api/queue')
def get_queue():
    """발행 큐 조회"""
    return jsonify({
        'queue': blog_queue.queue,
        'pending_count': blog_queue.get_pending_count(),
        'published_count': blog_queue.get_published_count()
    })


@app.route('/api/blogger/auth', methods=['POST'])
def blogger_auth():
    """Blogger OAuth 인증"""
    if not blogger_client.is_available():
        return jsonify({
            'error': 'Google API 라이브러리가 설치되지 않았습니다.',
            'install': 'pip install google-api-python-client google-auth-oauthlib'
        }), 400

    if not blogger_client.is_configured():
        return jsonify({
            'error': 'credentials.json 파일이 필요합니다.',
            'guide': 'Google Cloud Console에서 OAuth 2.0 클라이언트 ID를 생성하세요.'
        }), 400

    try:
        blogger_client.authenticate()
        blogs = blogger_client.get_blogs()

        return jsonify({
            'success': True,
            'authenticated': True,
            'blogs': blogs
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/blogger/set-blog', methods=['POST'])
def set_blog():
    """사용할 블로그 설정"""
    data = request.json
    blog_id = data.get('blog_id', '')

    if not blog_id:
        return jsonify({'error': 'blog_id가 필요합니다.'}), 400

    blogger_client.set_blog(blog_id)
    return jsonify({'success': True, 'blog_id': blog_id})


@app.route('/api/blogger/publish', methods=['POST'])
def publish_to_blogger():
    """블로그에 즉시 발행"""
    if not blogger_client.is_authenticated():
        return jsonify({'error': '먼저 Blogger 인증이 필요합니다.'}), 400

    data = request.json
    title = data.get('title', '')
    content = data.get('content', '')
    labels = data.get('labels', [])
    is_draft = data.get('is_draft', False)

    if not title or not content:
        return jsonify({'error': '제목과 내용이 필요합니다.'}), 400

    try:
        result = blogger_client.create_post(
            title=title,
            content=content,
            labels=labels,
            is_draft=is_draft
        )

        return jsonify({
            'success': True,
            'post': result
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/blogger/posts')
def get_blogger_posts():
    """블로그 글 목록"""
    if not blogger_client.is_authenticated():
        return jsonify({'error': '먼저 Blogger 인증이 필요합니다.'}), 400

    try:
        posts = blogger_client.get_posts(max_results=20)
        return jsonify({'posts': posts})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ===== 쓰레드 API =====

@app.route('/api/threads/post', methods=['POST'])
def post_to_threads():
    """쓰레드에 게시"""
    if not threads_client.is_configured():
        return jsonify({'error': 'Threads API가 설정되지 않았습니다.'}), 400

    data = request.json
    text = data.get('text', '')
    blog_url = data.get('blog_url', '')

    if not text:
        return jsonify({'error': '게시물 내용이 필요합니다.'}), 400

    try:
        if blog_url:
            result = threads_client.create_link_post(text, blog_url)
        else:
            result = threads_client.create_text_post(text)

        return jsonify({
            'success': True,
            'post': result
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/threads/generate-hook', methods=['POST'])
def generate_thread_hook():
    """블로그용 쓰레드 훅 생성"""
    if not ai_generator.is_configured():
        return jsonify({'error': 'OpenAI API 키가 설정되지 않았습니다.'}), 400

    data = request.json
    blog_url = data.get('blog_url', '')
    blog_title = data.get('blog_title', '')
    blog_summary = data.get('blog_summary', '')
    style = data.get('style', 'viral')

    try:
        result = ai_generator.generate_thread_content(
            blog_url=blog_url,
            blog_title=blog_title,
            blog_summary=blog_summary,
            style=style
        )

        return jsonify({
            'success': True,
            'content': result
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ===== 스케줄러 API =====

@app.route('/api/scheduler/status')
def scheduler_status():
    """스케줄러 상태"""
    return jsonify(auto_publisher.get_status())


@app.route('/api/scheduler/start', methods=['POST'])
def start_scheduler():
    """스케줄러 시작"""
    try:
        auto_publisher.start_scheduler()
        return jsonify({
            'success': True,
            'status': auto_publisher.get_status()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/scheduler/stop', methods=['POST'])
def stop_scheduler():
    """스케줄러 중지"""
    try:
        auto_publisher.stop_scheduler()
        return jsonify({
            'success': True,
            'status': auto_publisher.get_status()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/scheduler/config', methods=['GET', 'POST'])
def scheduler_config():
    """스케줄러 설정"""
    if request.method == 'GET':
        return jsonify(auto_publisher.config)

    data = request.json
    auto_publisher.config.update(data)
    auto_publisher.save_config()

    return jsonify({
        'success': True,
        'config': auto_publisher.config
    })


@app.route('/api/scheduler/publish-now', methods=['POST'])
def publish_now():
    """즉시 발행"""
    result = auto_publisher.publish_blog_post()
    if result:
        return jsonify({
            'success': True,
            'result': result
        })
    else:
        return jsonify({
            'success': False,
            'message': '발행할 글이 없거나 발행 조건에 맞지 않습니다.'
        })


@app.route('/api/scheduler/generate-now', methods=['POST'])
def generate_now():
    """즉시 글 생성 후 큐에 추가"""
    data = request.json
    keyword = data.get('keyword', '')

    if not keyword:
        return jsonify({'error': '키워드가 필요합니다.'}), 400

    try:
        result = auto_publisher.generate_and_queue_post(keyword=keyword)
        return jsonify({
            'success': True,
            'result': result
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ===== 설정 관리 =====

@app.route('/api/settings', methods=['GET', 'POST'])
def manage_settings():
    """앱 설정 관리"""
    settings_file = 'app_settings.json'

    if request.method == 'GET':
        if os.path.exists(settings_file):
            with open(settings_file, 'r', encoding='utf-8') as f:
                return jsonify(json.load(f))
        return jsonify({})

    data = request.json
    with open(settings_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return jsonify({'success': True})


if __name__ == '__main__':
    print("\n" + "=" * 50)
    print("  AI 블로그 자동화 앱")
    print("=" * 50)
    print(f"  OpenAI API: {'설정됨' if ai_generator.is_configured() else '미설정'}")
    print(f"  YouTube 추출: {'가능' if youtube_extractor.is_configured() else '미설치'}")
    print(f"  Blogger API: {'설정됨' if blogger_client.is_configured() else '미설정'}")
    print(f"  Threads API: {'설정됨' if threads_client.is_configured() else '미설정'}")
    print("=" * 50)
    print("  http://localhost:5001 에서 실행됩니다.")
    print("=" * 50 + "\n")

    app.run(debug=True, host='0.0.0.0', port=5001)
