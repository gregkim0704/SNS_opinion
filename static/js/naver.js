// ===== Naver API Functions =====
// Add these functions to your app.js file

// Check Naver API status on page load
async function checkNaverApiStatus() {
    try {
        const response = await fetch('/api/naver-status');
        const status = await response.json();

        const statusDiv = document.getElementById('naverApiStatus');
        if (status.enabled) {
            statusDiv.innerHTML = '<div class="api-status enabled">✅ 네이버 API 연동 활성화 - 실시간 데이터 수집 가능</div>';
        } else {
            statusDiv.innerHTML = '<div class="api-status disabled">⚠️ 네이버 API 미설정 - .env 파일에 API 키를 설정하세요 (WINDOWS_GUIDE.md 참고)</div>';
        }
    } catch (error) {
        console.error('API 상태 확인 실패:', error);
    }
}

async function searchNaver() {
    const query = document.getElementById('naverSearchQuery').value.trim();
    const category = document.getElementById('naverCategory').value;
    const display = parseInt(document.getElementById('naverDisplay').value) || 10;

    if (!query) {
        alert('검색어를 입력해주세요.');
        return;
    }

    const resultsDiv = document.getElementById('naverSearchResults');
    resultsDiv.innerHTML = '<div class="loading">🔍 검색 중...</div>';

    try {
        const response = await fetch('/api/naver-search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query, category, display })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || '검색 실패');
        }

        const data = await response.json();
        displaySearchResults(data.results);

    } catch (error) {
        resultsDiv.innerHTML = `<div class="error-message">❌ ${error.message}</div>`;
    }
}

async function collectNaverData() {
    const query = document.getElementById('naverSearchQuery').value.trim();
    const category = document.getElementById('naverCategory').value;
    const display = parseInt(document.getElementById('naverDisplay').value) || 10;

    if (!query) {
        alert('검색어를 입력해주세요.');
        return;
    }

    const resultsDiv = document.getElementById('naverSearchResults');
    resultsDiv.innerHTML = '<div class="loading">📥 데이터 수집 및 분석 중...</div>';

    try {
        const response = await fetch('/api/naver-collect', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query, category, display })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || '수집 실패');
        }

        const data = await response.json();
        resultsDiv.innerHTML = `
            <div class="success-message">
                ✅ ${data.message}<br>
                검색어: ${data.query}<br>
                수집 데이터: ${data.count}개<br>
                전체 리뷰: ${data.total_reviews}개
            </div>
        `;

        // 대시보드 자동 새로고침
        await refreshDashboard();

    } catch (error) {
        resultsDiv.innerHTML = `<div class="error-message">❌ ${error.message}</div>`;
    }
}

function displaySearchResults(results) {
    const resultsDiv = document.getElementById('naverSearchResults');

    if (!results || results.length === 0) {
        resultsDiv.innerHTML = '<div class="error-message">검색 결과가 없습니다.</div>';
        return;
    }

    let html = `<h3 style="color: #2e7d32; margin-bottom: 15px;">검색 결과 (${results.length}개)</h3>`;

    results.forEach(item => {
        const sentimentClass = item.sentiment || 'neutral';
        const sentimentText = {
            'positive': '긍정',
            'neutral': '중립',
            'negative': '부정'
        }[sentimentClass] || '중립';

        html += `
            <div class="search-result-item">
                <div class="title">${item.title || '제목 없음'}</div>
                <div class="description">${item.description || item.text || ''}</div>
                <div class="meta">
                    <div>
                        <span class="platform-badge">${item.platform}</span>
                        <span class="sentiment-badge ${sentimentClass}">${sentimentText}</span>
                    </div>
                    <div style="color: #999; font-size: 0.85em;">
                        ${item.date || ''}
                    </div>
                </div>
            </div>
        `;
    });

    resultsDiv.innerHTML = html;
}

// Initialize on page load
window.addEventListener('DOMContentLoaded', function() {
    checkNaverApiStatus();

    // Enter key support for Naver search
    const searchInput = document.getElementById('naverSearchQuery');
    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                searchNaver();
            }
        });
    }
});
