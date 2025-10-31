from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from textblob import TextBlob
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import Counter
import re
import json

app = Flask(__name__)
CORS(app)

# 샘플 데이터 저장소
reviews_data = []

def analyze_sentiment(text):
    """텍스트의 감정을 분석합니다."""
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity

    if polarity > 0.1:
        sentiment = 'positive'
    elif polarity < -0.1:
        sentiment = 'negative'
    else:
        sentiment = 'neutral'

    return {
        'sentiment': sentiment,
        'polarity': polarity,
        'subjectivity': blob.sentiment.subjectivity
    }

def extract_keywords(texts, top_n=10):
    """텍스트에서 주요 키워드를 추출합니다."""
    # 모든 텍스트 결합
    combined_text = ' '.join(texts)

    # 단어 추출 (영어 기준, 한글은 추가 처리 필요)
    words = re.findall(r'\b[a-zA-Z가-힣]{2,}\b', combined_text.lower())

    # 불용어 제거
    stopwords = {'the', 'is', 'at', 'which', 'on', 'and', 'a', 'an', 'as', 'are', 'was', 'were', 'been', 'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should', 'could', 'may', 'might', 'must', 'can', 'to', 'of', 'in', 'for', 'with', 'this', 'that', 'it', 'from', 'by'}
    words = [w for w in words if w not in stopwords and len(w) > 2]

    # 빈도수 계산
    word_freq = Counter(words)

    return word_freq.most_common(top_n)

def generate_sample_data():
    """분석용 샘플 데이터를 생성합니다."""
    sample_reviews = [
        {"text": "This product is amazing! I love it so much. Best purchase ever!", "platform": "Twitter", "date": "2024-01-15"},
        {"text": "Terrible experience. Would not recommend to anyone. Very disappointed.", "platform": "Facebook", "date": "2024-01-16"},
        {"text": "It's okay, nothing special but does the job.", "platform": "Instagram", "date": "2024-01-17"},
        {"text": "Great quality and fast delivery. Exceeded my expectations!", "platform": "Twitter", "date": "2024-01-18"},
        {"text": "Worst customer service ever. Product broke after 2 days.", "platform": "Facebook", "date": "2024-01-19"},
        {"text": "Pretty good for the price. Would buy again.", "platform": "Instagram", "date": "2024-01-20"},
        {"text": "Absolutely fantastic! Everyone should try this.", "platform": "Twitter", "date": "2024-01-21"},
        {"text": "Mediocre at best. Expected more for the price.", "platform": "Facebook", "date": "2024-01-22"},
        {"text": "Outstanding product! Highly recommended to everyone.", "platform": "Instagram", "date": "2024-01-23"},
        {"text": "Complete waste of money. Do not buy this.", "platform": "Twitter", "date": "2024-01-24"},
        {"text": "Good quality product with excellent features.", "platform": "Facebook", "date": "2024-01-25"},
        {"text": "Not bad, but could be better. Average experience.", "platform": "Instagram", "date": "2024-01-26"},
        {"text": "Incredible value! Best in its category without doubt.", "platform": "Twitter", "date": "2024-01-27"},
        {"text": "Poor quality, broke immediately. Very unhappy.", "platform": "Facebook", "date": "2024-01-28"},
        {"text": "Decent product, meets basic expectations well.", "platform": "Instagram", "date": "2024-01-29"},
    ]

    # 각 리뷰에 감정 분석 추가
    for review in sample_reviews:
        sentiment_data = analyze_sentiment(review['text'])
        review.update(sentiment_data)

    return sample_reviews

@app.route('/')
def index():
    """메인 페이지를 렌더링합니다."""
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """텍스트를 분석합니다."""
    data = request.json
    text = data.get('text', '')
    platform = data.get('platform', 'Unknown')

    if not text:
        return jsonify({'error': 'No text provided'}), 400

    # 감정 분석
    sentiment_data = analyze_sentiment(text)

    # 데이터 저장
    review_entry = {
        'text': text,
        'platform': platform,
        'date': datetime.now().strftime('%Y-%m-%d'),
        **sentiment_data
    }
    reviews_data.append(review_entry)

    return jsonify(review_entry)

@app.route('/api/trends', methods=['GET'])
def get_trends():
    """시간별 트렌드 데이터를 반환합니다."""
    if not reviews_data:
        return jsonify({'error': 'No data available'}), 404

    df = pd.DataFrame(reviews_data)

    # 날짜별 감정 집계
    trend_data = df.groupby(['date', 'sentiment']).size().unstack(fill_value=0)

    result = {
        'dates': trend_data.index.tolist(),
        'positive': trend_data.get('positive', [0]*len(trend_data)).tolist(),
        'neutral': trend_data.get('neutral', [0]*len(trend_data)).tolist(),
        'negative': trend_data.get('negative', [0]*len(trend_data)).tolist()
    }

    return jsonify(result)

@app.route('/api/keywords', methods=['GET'])
def get_keywords():
    """주요 키워드를 추출합니다."""
    if not reviews_data:
        return jsonify({'error': 'No data available'}), 404

    texts = [review['text'] for review in reviews_data]
    keywords = extract_keywords(texts, top_n=15)

    return jsonify({
        'keywords': [{'word': word, 'count': count} for word, count in keywords]
    })

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """전체 통계를 반환합니다."""
    if not reviews_data:
        return jsonify({'error': 'No data available'}), 404

    df = pd.DataFrame(reviews_data)

    sentiment_counts = df['sentiment'].value_counts().to_dict()
    platform_counts = df['platform'].value_counts().to_dict()

    avg_polarity = df['polarity'].mean()
    avg_subjectivity = df['subjectivity'].mean()

    return jsonify({
        'total_reviews': len(reviews_data),
        'sentiment_distribution': sentiment_counts,
        'platform_distribution': platform_counts,
        'average_polarity': float(avg_polarity),
        'average_subjectivity': float(avg_subjectivity)
    })

@app.route('/api/sample-data', methods=['POST'])
def load_sample_data():
    """샘플 데이터를 로드합니다."""
    global reviews_data
    reviews_data = generate_sample_data()

    return jsonify({
        'message': 'Sample data loaded successfully',
        'count': len(reviews_data)
    })

@app.route('/api/clear-data', methods=['POST'])
def clear_data():
    """모든 데이터를 삭제합니다."""
    global reviews_data
    reviews_data = []

    return jsonify({'message': 'All data cleared'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
