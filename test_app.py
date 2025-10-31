"""
Simple test script for SNS Opinion Analysis App
"""

import sys

def test_imports():
    """Test if all required packages can be imported"""
    print("Testing imports...")

    try:
        import flask
        print("✅ Flask imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Flask: {e}")
        return False

    try:
        from flask_cors import CORS
        print("✅ Flask-CORS imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Flask-CORS: {e}")
        return False

    try:
        import pandas
        print("✅ Pandas imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Pandas: {e}")
        return False

    try:
        import numpy
        print("✅ NumPy imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import NumPy: {e}")
        return False

    try:
        from textblob import TextBlob
        print("✅ TextBlob imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import TextBlob: {e}")
        return False

    return True

def test_sentiment_analysis():
    """Test sentiment analysis functionality"""
    print("\nTesting sentiment analysis...")

    try:
        from textblob import TextBlob

        # Test positive sentiment
        positive_text = "I love this product! It's amazing!"
        blob = TextBlob(positive_text)
        assert blob.sentiment.polarity > 0, "Positive sentiment test failed"
        print(f"✅ Positive sentiment: {blob.sentiment.polarity:.2f}")

        # Test negative sentiment
        negative_text = "This is terrible. I hate it."
        blob = TextBlob(negative_text)
        assert blob.sentiment.polarity < 0, "Negative sentiment test failed"
        print(f"✅ Negative sentiment: {blob.sentiment.polarity:.2f}")

        # Test neutral sentiment
        neutral_text = "This is a product."
        blob = TextBlob(neutral_text)
        print(f"✅ Neutral sentiment: {blob.sentiment.polarity:.2f}")

        return True
    except Exception as e:
        print(f"❌ Sentiment analysis test failed: {e}")
        return False

def test_app_structure():
    """Test if the app structure is correct"""
    print("\nTesting app structure...")

    import os

    required_files = [
        'app.py',
        'requirements.txt',
        'README.md',
        'templates/index.html',
        'static/css/style.css',
        'static/js/app.js'
    ]

    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} not found")
            all_exist = False

    return all_exist

def main():
    """Run all tests"""
    print("=" * 50)
    print("SNS Opinion Analysis App - Test Suite")
    print("=" * 50)

    tests = [
        ("Import Test", test_imports),
        ("Sentiment Analysis Test", test_sentiment_analysis),
        ("App Structure Test", test_app_structure)
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))

    print("\n" + "=" * 50)
    print("Test Results Summary")
    print("=" * 50)

    all_passed = True
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False

    print("=" * 50)

    if all_passed:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the output above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
