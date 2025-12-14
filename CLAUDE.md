# CLAUDE.md - AI Assistant Guide for SNS Opinion Trend Analysis

This file provides guidance for AI assistants working with this codebase.

## Project Overview

**SNS 의견 동향 분석 앱** (SNS Opinion Trend Analysis App) is a Python Flask web application that collects and analyzes social media reviews and opinions. It provides sentiment analysis, trend visualization, and keyword extraction capabilities.

### Key Features
- Sentiment analysis (positive/neutral/negative classification)
- Time-based trend visualization with Chart.js
- Keyword extraction and word cloud
- Naver API integration for real-time data collection (blogs, news, cafes, shopping)
- Multi-platform support (Twitter, Facebook, Instagram, YouTube, TikTok, Naver)

## Codebase Structure

```
SNS_opinion/
├── app.py                 # Main Flask application and API endpoints
├── naver_api.py           # Naver Search API client module
├── test_app.py            # Test suite for the application
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variables template
├── .gitignore             # Git ignore patterns
├── templates/
│   └── index.html         # Main dashboard HTML template (Jinja2)
├── static/
│   ├── css/
│   │   └── style.css      # Application styles
│   └── js/
│       ├── app.js         # Main frontend JavaScript (Chart.js integration)
│       └── naver.js       # Naver API frontend functions
├── setup.sh / setup.bat   # Installation scripts (Linux/Mac and Windows)
├── run.sh / run.bat       # Run scripts (Linux/Mac and Windows)
├── README.md              # Project documentation (Korean)
├── FEATURES.md            # Detailed feature documentation
├── NAVER_API_GUIDE.md     # Naver API setup guide
└── WINDOWS_GUIDE.md       # Windows installation guide
```

## Tech Stack

### Backend
- **Python 3.10+** (supports up to 3.13)
- **Flask 3.0+** - Web framework
- **Flask-CORS 4.0+** - CORS support
- **TextBlob 0.17+** - NLP and sentiment analysis
- **Pandas 2.2+** - Data processing
- **NumPy 1.26+** - Numerical operations
- **requests 2.31+** - HTTP client for Naver API
- **python-dotenv 1.0+** - Environment variable management

### Frontend
- **HTML5/CSS3** - Responsive UI
- **Vanilla JavaScript (ES6+)** - No frameworks
- **Chart.js 4.4** - Data visualization (CDN-loaded)
- **Jinja2** - Template engine (Flask default)

## Development Workflows

### Setup (First Time)

**Linux/Mac:**
```bash
bash setup.sh
# or manually:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -c "import textblob; textblob.download_corpora()"
```

**Windows:**
```cmd
setup.bat
# or manually:
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -c "import textblob; textblob.download_corpora()"
```

### Running the Application

**Linux/Mac:**
```bash
bash run.sh
# or: source venv/bin/activate && python app.py
```

**Windows:**
```cmd
run.bat
# or: venv\Scripts\activate && python app.py
```

The app runs at `http://localhost:5000` with debug mode enabled.

### Running Tests

```bash
python test_app.py
```

Tests include:
- Import validation for all dependencies
- Sentiment analysis functionality tests
- Application structure verification

### Naver API Configuration (Optional)

1. Get API credentials from [Naver Developer Center](https://developers.naver.com)
2. Copy `.env.example` to `.env`
3. Set `NAVER_CLIENT_ID` and `NAVER_CLIENT_SECRET`
4. Restart the application

## API Endpoints

### Core APIs

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main dashboard page |
| `/api/analyze` | POST | Analyze text sentiment. Body: `{"text": "...", "platform": "Twitter"}` |
| `/api/statistics` | GET | Get overall statistics |
| `/api/trends` | GET | Get time-series trend data |
| `/api/keywords` | GET | Get extracted keywords |
| `/api/sample-data` | POST | Load sample data for testing |
| `/api/clear-data` | POST | Clear all stored data |

### Naver API Integration

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/naver-search` | POST | Search Naver. Body: `{"query": "...", "category": "all/blog/news/cafe/shopping", "display": 10}` |
| `/api/naver-collect` | POST | Search and add to analysis data |
| `/api/naver-status` | GET | Check API configuration status |

## Key Conventions

### Code Style
- **Language**: Code is in English, UI/comments often in Korean
- **Docstrings**: Korean docstrings with descriptive function names
- **Variables**: Snake_case for Python, camelCase for JavaScript
- **Flask routes**: RESTful API design with JSON responses

### Sentiment Analysis Logic
Located in `app.py:analyze_sentiment()`:
- Polarity > 0.1 → **positive**
- Polarity < -0.1 → **negative**
- Otherwise → **neutral**

### Data Storage
- In-memory storage using `reviews_data` list (no database)
- Each review entry contains: `text`, `platform`, `date`, `sentiment`, `polarity`, `subjectivity`

### Frontend Architecture
- Single-page application pattern
- Chart instances stored as global variables: `sentimentChart`, `platformChart`, `trendChart`
- All API calls use `fetch()` with async/await
- Dashboard auto-refreshes after data changes

### Error Handling
- API returns `404` when no data available
- API returns `400` for validation errors (missing text, missing API keys)
- API returns `500` for internal errors with message details

## Common Tasks for AI Assistants

### Adding a New API Endpoint
1. Add route in `app.py` with appropriate decorator
2. Follow existing patterns for JSON responses
3. Handle errors consistently with existing endpoints

### Modifying Sentiment Analysis
- Core logic is in `app.py:analyze_sentiment()`
- Uses TextBlob library for NLP
- Threshold values (0.1, -0.1) can be adjusted

### Adding a New Chart
1. Add `<canvas>` element in `templates/index.html`
2. Initialize Chart.js instance in `static/js/app.js:initializeCharts()`
3. Add update function following `updateStatistics()` pattern

### Extending Naver API
- `naver_api.py` contains the `NaverAPIClient` class
- Add new search methods following existing patterns (e.g., `search_blogs()`)
- Update `app.py` to expose new endpoints

### Adding a New Platform
1. Add option to `<select id="platform">` in `templates/index.html`
2. No backend changes needed - platform is just a string label

## Important Notes

- **No Database**: Data is stored in-memory and lost on restart
- **TextBlob Corpora**: Must be downloaded after installation (`textblob.download_corpora()`)
- **CORS Enabled**: Flask-CORS is configured for all origins
- **Debug Mode**: App runs in debug mode by default (`debug=True`)
- **Host Binding**: Binds to `0.0.0.0:5000` (accessible from network)

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `NAVER_CLIENT_ID` | No | Naver API Client ID |
| `NAVER_CLIENT_SECRET` | No | Naver API Client Secret |
| `FLASK_ENV` | No | Flask environment (development/production) |
| `FLASK_DEBUG` | No | Enable debug mode |

## Quick Reference

```bash
# Start development server
python app.py

# Run tests
python test_app.py

# Test sentiment analysis manually
python -c "from textblob import TextBlob; print(TextBlob('I love this!').sentiment)"

# Test Naver API client
python naver_api.py  # Requires API keys in .env
```
