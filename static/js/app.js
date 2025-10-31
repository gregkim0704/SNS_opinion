// Chart instances
let sentimentChart = null;
let platformChart = null;
let trendChart = null;

// Initialize the dashboard when the page loads
document.addEventListener('DOMContentLoaded', function() {
    initializeCharts();
    console.log('SNS 의견 동향 분석 앱이 시작되었습니다.');
});

// Initialize all charts
function initializeCharts() {
    // Sentiment Distribution Chart
    const sentimentCtx = document.getElementById('sentimentChart').getContext('2d');
    sentimentChart = new Chart(sentimentCtx, {
        type: 'doughnut',
        data: {
            labels: ['긍정', '중립', '부정'],
            datasets: [{
                data: [0, 0, 0],
                backgroundColor: [
                    'rgba(40, 167, 69, 0.8)',
                    'rgba(23, 162, 184, 0.8)',
                    'rgba(220, 53, 69, 0.8)'
                ],
                borderColor: [
                    'rgba(40, 167, 69, 1)',
                    'rgba(23, 162, 184, 1)',
                    'rgba(220, 53, 69, 1)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        font: {
                            size: 14
                        },
                        padding: 15
                    }
                }
            }
        }
    });

    // Platform Distribution Chart
    const platformCtx = document.getElementById('platformChart').getContext('2d');
    platformChart = new Chart(platformCtx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: '리뷰 수',
                data: [],
                backgroundColor: 'rgba(102, 126, 234, 0.8)',
                borderColor: 'rgba(102, 126, 234, 1)',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });

    // Trend Chart
    const trendCtx = document.getElementById('trendChart').getContext('2d');
    trendChart = new Chart(trendCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: '긍정',
                    data: [],
                    borderColor: 'rgba(40, 167, 69, 1)',
                    backgroundColor: 'rgba(40, 167, 69, 0.1)',
                    tension: 0.4,
                    fill: true
                },
                {
                    label: '중립',
                    data: [],
                    borderColor: 'rgba(23, 162, 184, 1)',
                    backgroundColor: 'rgba(23, 162, 184, 0.1)',
                    tension: 0.4,
                    fill: true
                },
                {
                    label: '부정',
                    data: [],
                    borderColor: 'rgba(220, 53, 69, 1)',
                    backgroundColor: 'rgba(220, 53, 69, 0.1)',
                    tension: 0.4,
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        font: {
                            size: 14
                        },
                        padding: 15
                    }
                }
            }
        }
    });
}

// Analyze a review
async function analyzeReview() {
    const text = document.getElementById('reviewText').value.trim();
    const platform = document.getElementById('platform').value;

    if (!text) {
        alert('리뷰 내용을 입력해주세요.');
        return;
    }

    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text, platform })
        });

        if (!response.ok) {
            throw new Error('분석에 실패했습니다.');
        }

        const result = await response.json();
        displayAnalysisResult(result);

        // Clear the input
        document.getElementById('reviewText').value = '';

        // Refresh the dashboard
        await refreshDashboard();
    } catch (error) {
        console.error('Error:', error);
        alert('분석 중 오류가 발생했습니다.');
    }
}

// Display analysis result
function displayAnalysisResult(result) {
    const resultBox = document.getElementById('analysisResult');
    const sentimentClass = `sentiment-${result.sentiment}`;
    const sentimentText = {
        'positive': '긍정적',
        'neutral': '중립적',
        'negative': '부정적'
    }[result.sentiment];

    resultBox.innerHTML = `
        <h3>분석 결과</h3>
        <p><strong>플랫폼:</strong> ${result.platform}</p>
        <p><strong>감정:</strong> <span class="${sentimentClass}">${sentimentText}</span></p>
        <p><strong>극성 점수:</strong> ${result.polarity.toFixed(3)}</p>
        <p><strong>주관성 점수:</strong> ${result.subjectivity.toFixed(3)}</p>
    `;
    resultBox.classList.add('show');
}

// Load sample data
async function loadSampleData() {
    try {
        const response = await fetch('/api/sample-data', {
            method: 'POST'
        });

        if (!response.ok) {
            throw new Error('샘플 데이터 로드에 실패했습니다.');
        }

        const result = await response.json();
        alert(`샘플 데이터 ${result.count}개가 로드되었습니다.`);

        await refreshDashboard();
    } catch (error) {
        console.error('Error:', error);
        alert('샘플 데이터 로드 중 오류가 발생했습니다.');
    }
}

// Clear all data
async function clearData() {
    if (!confirm('모든 데이터를 삭제하시겠습니까?')) {
        return;
    }

    try {
        const response = await fetch('/api/clear-data', {
            method: 'POST'
        });

        if (!response.ok) {
            throw new Error('데이터 삭제에 실패했습니다.');
        }

        alert('모든 데이터가 삭제되었습니다.');
        await refreshDashboard();
    } catch (error) {
        console.error('Error:', error);
        alert('데이터 삭제 중 오류가 발생했습니다.');
    }
}

// Refresh the entire dashboard
async function refreshDashboard() {
    await updateStatistics();
    await updateTrends();
    await updateKeywords();
}

// Update statistics
async function updateStatistics() {
    try {
        const response = await fetch('/api/statistics');

        if (!response.ok) {
            // No data available
            resetStatistics();
            return;
        }

        const stats = await response.json();

        // Update stat cards
        document.getElementById('totalReviews').textContent = stats.total_reviews;
        document.getElementById('positiveCount').textContent = stats.sentiment_distribution.positive || 0;
        document.getElementById('neutralCount').textContent = stats.sentiment_distribution.neutral || 0;
        document.getElementById('negativeCount').textContent = stats.sentiment_distribution.negative || 0;

        // Update sentiment chart
        sentimentChart.data.datasets[0].data = [
            stats.sentiment_distribution.positive || 0,
            stats.sentiment_distribution.neutral || 0,
            stats.sentiment_distribution.negative || 0
        ];
        sentimentChart.update();

        // Update platform chart
        const platforms = Object.keys(stats.platform_distribution);
        const platformCounts = Object.values(stats.platform_distribution);

        platformChart.data.labels = platforms;
        platformChart.data.datasets[0].data = platformCounts;
        platformChart.update();

    } catch (error) {
        console.error('Error updating statistics:', error);
        resetStatistics();
    }
}

// Update trends
async function updateTrends() {
    try {
        const response = await fetch('/api/trends');

        if (!response.ok) {
            resetTrends();
            return;
        }

        const trends = await response.json();

        trendChart.data.labels = trends.dates;
        trendChart.data.datasets[0].data = trends.positive;
        trendChart.data.datasets[1].data = trends.neutral;
        trendChart.data.datasets[2].data = trends.negative;
        trendChart.update();

    } catch (error) {
        console.error('Error updating trends:', error);
        resetTrends();
    }
}

// Update keywords
async function updateKeywords() {
    try {
        const response = await fetch('/api/keywords');

        if (!response.ok) {
            document.getElementById('keywordsContainer').innerHTML = '<p>키워드 데이터가 없습니다.</p>';
            return;
        }

        const data = await response.json();
        const keywordsContainer = document.getElementById('keywordsContainer');

        if (data.keywords.length === 0) {
            keywordsContainer.innerHTML = '<p>키워드 데이터가 없습니다.</p>';
            return;
        }

        keywordsContainer.innerHTML = data.keywords.map(item => `
            <div class="keyword-tag">
                ${item.word}
                <span class="keyword-count">${item.count}</span>
            </div>
        `).join('');

    } catch (error) {
        console.error('Error updating keywords:', error);
        document.getElementById('keywordsContainer').innerHTML = '<p>키워드를 불러오는 중 오류가 발생했습니다.</p>';
    }
}

// Reset statistics display
function resetStatistics() {
    document.getElementById('totalReviews').textContent = '0';
    document.getElementById('positiveCount').textContent = '0';
    document.getElementById('neutralCount').textContent = '0';
    document.getElementById('negativeCount').textContent = '0';

    sentimentChart.data.datasets[0].data = [0, 0, 0];
    sentimentChart.update();

    platformChart.data.labels = [];
    platformChart.data.datasets[0].data = [];
    platformChart.update();
}

// Reset trends display
function resetTrends() {
    trendChart.data.labels = [];
    trendChart.data.datasets[0].data = [];
    trendChart.data.datasets[1].data = [];
    trendChart.data.datasets[2].data = [];
    trendChart.update();
}

// Handle Enter key in textarea
document.addEventListener('DOMContentLoaded', function() {
    const textarea = document.getElementById('reviewText');
    if (textarea) {
        textarea.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                analyzeReview();
            }
        });
    }
});
