/**
 * VoicePulse AI - Dashboard Controller
 * Main application logic and chart rendering
 */

// ==================== STATE MANAGEMENT ====================
let currentAudioFile = null;
let currentAnalysisData = null;
let charts = {};

// ==================== DOM ELEMENTS ====================
const elements = {
    // Upload section
    audioFileInput: document.getElementById('audio-file'),
    fileInfo: document.getElementById('file-info'),
    recordBtn: document.getElementById('record-btn'),
    recordText: document.getElementById('record-text'),
    recordingTimer: document.getElementById('recording-timer'),
    analyzeBtn: document.getElementById('analyze-btn'),

    // Progress
    progressContainer: document.getElementById('progress-container'),
    progressFill: document.getElementById('progress-fill'),
    progressText: document.getElementById('progress-text'),

    // Sections
    uploadSection: document.getElementById('upload-section'),
    dashboardSection: document.getElementById('dashboard-section'),

    // Summary cards
    primaryEmotion: document.getElementById('primary-emotion'),
    avgConfidence: document.getElementById('avg-confidence'),
    overallSentiment: document.getElementById('overall-sentiment'),
    totalTransitions: document.getElementById('total-transitions'),

    // Tables
    transitionsTbody: document.getElementById('transitions-tbody'),

    // Audio player
    audioPlayer: document.getElementById('audio-player'),
    audioMarkers: document.getElementById('audio-markers'),

    // Actions
    downloadReportBtn: document.getElementById('download-report-btn'),
    newAnalysisBtn: document.getElementById('new-analysis-btn')
};

// ==================== EMOTION COLORS ====================
const EMOTION_COLORS = {
    happy: '#ffd93d',
    sad: '#6bcfff',
    angry: '#ff6b6b',
    neutral: '#a8dadc',
    fear: '#b19cd9',
    disgust: '#98d8c8',
    surprise: '#ffaaa5'
};

// ==================== INITIALIZATION ====================
document.addEventListener('DOMContentLoaded', () => {
    initializeEventListeners();
    checkBackendHealth();
});

function initializeEventListeners() {
    // File upload
    elements.audioFileInput.addEventListener('change', handleFileSelect);

    // Recording
    elements.recordBtn.addEventListener('click', handleRecordToggle);

    // Analyze
    elements.analyzeBtn.addEventListener('click', handleAnalyze);

    // Actions
    elements.downloadReportBtn.addEventListener('click', handleDownloadReport);
    elements.newAnalysisBtn.addEventListener('click', handleNewAnalysis);
}

// ==================== BACKEND HEALTH CHECK ====================
async function checkBackendHealth() {
    try {
        await api.healthCheck();
        console.log('✅ Backend is healthy');
    } catch (error) {
        console.error('❌ Backend health check failed:', error);
        
        const isLocal = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
        let message = 'Backend server is not responding.';

        if (isLocal) {
            message += ' Please start the backend server (START_BACKEND.bat).';
        } else {
            message += ' Set your backend URL by adding ?api=https://your-backend-domain to the page URL.';
        }

        showNotification(message, 'error');
    }
}

// ==================== FILE HANDLING ====================
function handleFileSelect(event) {
    const file = event.target.files[0];

    if (!file) return;

    // Validate file type
    const validTypes = ['audio/wav', 'audio/mpeg', 'audio/mp3', 'audio/mp4', 'audio/x-m4a', 'audio/ogg', 'audio/webm'];
    if (!validTypes.includes(file.type) && !file.name.match(/\.(wav|mp3|m4a|ogg|webm)$/i)) {
        showNotification('Invalid file type. Please upload WAV, MP3, or M4A files.', 'error');
        return;
    }

    // Validate file size (50MB)
    if (file.size > 50 * 1024 * 1024) {
        showNotification('File too large. Maximum size is 50MB.', 'error');
        return;
    }

    currentAudioFile = file;
    elements.fileInfo.textContent = `Selected: ${file.name} (${formatFileSize(file.size)})`;
    elements.analyzeBtn.disabled = false;

    console.log('File selected:', file.name);
}

// ==================== RECORDING ====================
let recordingTimerInterval = null;

async function handleRecordToggle() {
    if (!recorder.isSupported()) {
        showNotification('Audio recording is not supported in your browser.', 'error');
        return;
    }

    if (!recorder.isRecording) {
        // Start recording
        try {
            await recorder.startRecording();

            // Update UI
            elements.recordBtn.classList.add('btn-recording');
            elements.recordText.textContent = 'Stop Recording';
            elements.recordingTimer.style.display = 'block';

            // Start timer
            recordingTimerInterval = setInterval(() => {
                elements.recordingTimer.textContent = recorder.getFormattedDuration();
            }, 1000);

        } catch (error) {
            showNotification(error.message, 'error');
        }
    } else {
        // Stop recording
        try {
            const audioBlob = await recorder.stopRecording();

            // Convert to file
            currentAudioFile = recorder.blobToFile(audioBlob, 'recording.webm');

            // Update UI
            elements.recordBtn.classList.remove('btn-recording');
            elements.recordText.textContent = 'Record Voice';
            elements.recordingTimer.style.display = 'none';
            elements.fileInfo.textContent = `Recorded: ${recorder.getFormattedDuration()} (${formatFileSize(audioBlob.size)})`;
            elements.analyzeBtn.disabled = false;

            // Clear timer
            clearInterval(recordingTimerInterval);

            console.log('Recording complete');

        } catch (error) {
            showNotification('Failed to stop recording', 'error');
        }
    }
}

// ==================== ANALYSIS ====================
async function handleAnalyze() {
    if (!currentAudioFile) {
        showNotification('Please select or record an audio file first.', 'error');
        return;
    }

    // Show progress
    elements.progressContainer.style.display = 'block';
    elements.analyzeBtn.disabled = true;
    elements.progressText.textContent = 'Uploading audio...';

    try {
        // Analyze audio
        const result = await api.analyzeAudio(currentAudioFile, (progress) => {
            elements.progressFill.style.width = `${progress}%`;

            if (progress === 100) {
                elements.progressText.textContent = 'Processing with AI model...';
            }
        });

        if (!result.success) {
            throw new Error(result.error || 'Analysis failed');
        }

        // Store result
        currentAnalysisData = result;

        // Update progress
        elements.progressText.textContent = 'Rendering dashboard...';

        // Render dashboard
        await renderDashboard(result);

        // Hide upload, show dashboard
        elements.uploadSection.style.display = 'none';
        elements.dashboardSection.style.display = 'block';

        // Scroll to dashboard
        elements.dashboardSection.scrollIntoView({ behavior: 'smooth' });

        console.log('Analysis complete:', result);

    } catch (error) {
        console.error('Analysis error:', error);
        showNotification(`Analysis failed: ${error.message}`, 'error');
    } finally {
        elements.progressContainer.style.display = 'none';
        elements.progressFill.style.width = '0%';
        elements.analyzeBtn.disabled = false;
    }
}

// ==================== DASHBOARD RENDERING ====================
async function renderDashboard(data) {
    // Update summary cards
    updateSummaryCards(data);

    // Render charts
    renderTimelineChart(data.timeline);
    renderConfidenceChart(data.confidence_curve);
    renderDistributionChart(data.distribution);
    renderSentimentGauge(data.sentiment_analysis);
    renderHeatmapChart(data.heatmap_data);

    // Render transitions table
    renderTransitionsTable(data.transitions);

    // Setup audio player
    setupAudioPlayer(data);
}

function updateSummaryCards(data) {
    const journey = data.journey_analysis;
    const sentiment = data.sentiment_analysis;

    elements.primaryEmotion.textContent = journey.primary_emotion.toUpperCase();

    // Calculate average confidence
    const avgConf = data.confidence_curve.reduce((sum, item) => sum + item.confidence, 0) / data.confidence_curve.length;
    elements.avgConfidence.textContent = `${(avgConf * 100).toFixed(1)}%`;

    elements.overallSentiment.textContent = sentiment.category.toUpperCase();
    elements.totalTransitions.textContent = journey.total_transitions;
}

// ==================== CHART: TIMELINE ====================
function renderTimelineChart(timeline) {
    const ctx = document.getElementById('timeline-chart').getContext('2d');

    // Destroy existing chart
    if (charts.timeline) charts.timeline.destroy();

    const labels = timeline.map(t => t.start_formatted);
    const emotions = timeline.map(t => t.emotion);
    const confidences = timeline.map(t => t.confidence);

    // Create dataset with colors based on emotion
    const backgroundColors = emotions.map(e => EMOTION_COLORS[e] || '#888');

    charts.timeline = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Emotion Confidence',
                data: confidences,
                backgroundColor: backgroundColors,
                borderColor: backgroundColors,
                borderWidth: 2,
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        title: (items) => `Time: ${items[0].label}`,
                        label: (item) => {
                            const emotion = emotions[item.dataIndex];
                            const confidence = (item.raw * 100).toFixed(1);
                            return `${emotion}: ${confidence}%`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 1,
                    ticks: {
                        callback: (value) => `${(value * 100).toFixed(0)}%`,
                        color: '#b8c1ec'
                    },
                    grid: { color: 'rgba(255, 255, 255, 0.1)' }
                },
                x: {
                    ticks: { color: '#b8c1ec' },
                    grid: { display: false }
                }
            }
        }
    });
}

// ==================== CHART: CONFIDENCE ====================
function renderConfidenceChart(confidenceCurve) {
    const ctx = document.getElementById('confidence-chart').getContext('2d');

    if (charts.confidence) charts.confidence.destroy();

    const labels = confidenceCurve.map(c => c.time);
    const data = confidenceCurve.map(c => c.confidence);

    charts.confidence = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Confidence',
                data: data,
                borderColor: '#4facfe',
                backgroundColor: 'rgba(79, 172, 254, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointRadius: 4,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: (item) => `Confidence: ${(item.raw * 100).toFixed(1)}%`
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 1,
                    ticks: {
                        callback: (value) => `${(value * 100).toFixed(0)}%`,
                        color: '#b8c1ec'
                    },
                    grid: { color: 'rgba(255, 255, 255, 0.1)' }
                },
                x: {
                    ticks: { color: '#b8c1ec' },
                    grid: { display: false }
                }
            }
        }
    });
}

// ==================== CHART: DISTRIBUTION ====================
function renderDistributionChart(distribution) {
    const ctx = document.getElementById('distribution-chart').getContext('2d');

    if (charts.distribution) charts.distribution.destroy();

    const emotions = Object.keys(distribution);
    const percentages = Object.values(distribution);
    const colors = emotions.map(e => EMOTION_COLORS[e] || '#888');

    charts.distribution = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: emotions.map(e => e.charAt(0).toUpperCase() + e.slice(1)),
            datasets: [{
                data: percentages,
                backgroundColor: colors,
                borderWidth: 2,
                borderColor: '#0a0e27'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { color: '#b8c1ec', padding: 15 }
                },
                tooltip: {
                    callbacks: {
                        label: (item) => `${item.label}: ${item.raw.toFixed(1)}%`
                    }
                }
            }
        }
    });
}

// ==================== CHART: SENTIMENT GAUGE ====================
function renderSentimentGauge(sentimentAnalysis) {
    const ctx = document.getElementById('sentiment-chart').getContext('2d');

    if (charts.sentiment) charts.sentiment.destroy();

    const score = sentimentAnalysis.score;
    const category = sentimentAnalysis.category;

    // Convert score (-1 to 1) to percentage (0 to 100)
    const percentage = ((score + 1) / 2) * 100;

    charts.sentiment = new Chart(ctx, {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [percentage, 100 - percentage],
                backgroundColor: [
                    score > 0 ? '#4facfe' : score < 0 ? '#ff6b6b' : '#a8dadc',
                    'rgba(255, 255, 255, 0.1)'
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            cutout: '75%',
            plugins: {
                legend: { display: false },
                tooltip: { enabled: false }
            }
        },
        plugins: [{
            id: 'centerText',
            afterDraw: (chart) => {
                const ctx = chart.ctx;
                const centerX = chart.chartArea.left + (chart.chartArea.right - chart.chartArea.left) / 2;
                const centerY = chart.chartArea.top + (chart.chartArea.bottom - chart.chartArea.top) / 2;

                ctx.save();
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';

                // Score
                ctx.font = 'bold 32px Inter';
                ctx.fillStyle = '#ffffff';
                ctx.fillText(score.toFixed(2), centerX, centerY - 15);

                // Category
                ctx.font = '14px Inter';
                ctx.fillStyle = '#b8c1ec';
                ctx.fillText(category.toUpperCase(), centerX, centerY + 20);

                ctx.restore();
            }
        }]
    });
}

// ==================== CHART: HEATMAP ====================
function renderHeatmapChart(heatmapData) {
    const ctx = document.getElementById('heatmap-chart').getContext('2d');

    if (charts.heatmap) charts.heatmap.destroy();

    const emotions = ['happy', 'sad', 'angry', 'neutral', 'fear', 'disgust', 'surprise'];
    const labels = heatmapData.map(h => h.time);

    const datasets = emotions.map(emotion => ({
        label: emotion.charAt(0).toUpperCase() + emotion.slice(1),
        data: heatmapData.map(h => h[emotion] || 0),
        borderColor: EMOTION_COLORS[emotion],
        backgroundColor: EMOTION_COLORS[emotion] + '40',
        borderWidth: 2,
        fill: true,
        tension: 0.4
    }));

    charts.heatmap = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { color: '#b8c1ec', padding: 10 }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 1,
                    ticks: {
                        callback: (value) => `${(value * 100).toFixed(0)}%`,
                        color: '#b8c1ec'
                    },
                    grid: { color: 'rgba(255, 255, 255, 0.1)' }
                },
                x: {
                    ticks: { color: '#b8c1ec' },
                    grid: { display: false }
                }
            }
        }
    });
}

// ==================== TRANSITIONS TABLE ====================
function renderTransitionsTable(transitions) {
    elements.transitionsTbody.innerHTML = '';

    if (transitions.length === 0) {
        elements.transitionsTbody.innerHTML = '<tr><td colspan="5" style="text-align: center;">No transitions detected</td></tr>';
        return;
    }

    transitions.forEach(t => {
        const row = document.createElement('tr');

        row.innerHTML = `
            <td>${t.time}</td>
            <td><span class="emotion-badge badge-${t.from_emotion}">${t.from_emotion}</span></td>
            <td><span class="emotion-badge badge-${t.to_emotion}">${t.to_emotion}</span></td>
            <td>${t.confidence_change > 0 ? '+' : ''}${(t.confidence_change * 100).toFixed(1)}%</td>
            <td>${t.is_significant ? '✓' : '−'}</td>
        `;

        elements.transitionsTbody.appendChild(row);
    });
}

// ==================== AUDIO PLAYER ====================
function setupAudioPlayer(data) {
    // Set audio source
    const audioURL = URL.createObjectURL(currentAudioFile);
    elements.audioPlayer.src = audioURL;

    // Create markers for transitions
    elements.audioMarkers.innerHTML = '';

    data.transitions.forEach((t, index) => {
        const marker = document.createElement('div');
        marker.className = 'marker';
        marker.textContent = `${t.time} - ${t.to_emotion}`;
        marker.onclick = () => {
            elements.audioPlayer.currentTime = t.time_seconds;
            elements.audioPlayer.play();
        };
        elements.audioMarkers.appendChild(marker);
    });
}

// ==================== ACTIONS ====================
function handleDownloadReport() {
    if (!currentAnalysisData) return;

    const dataStr = JSON.stringify(currentAnalysisData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);

    const link = document.createElement('a');
    link.href = url;
    link.download = `voicepulse_report_${currentAnalysisData.analysis_id}.json`;
    link.click();

    URL.revokeObjectURL(url);
}

function handleNewAnalysis() {
    // Reset state
    currentAudioFile = null;
    currentAnalysisData = null;

    // Reset UI
    elements.audioFileInput.value = '';
    elements.fileInfo.textContent = 'Supports: WAV, MP3, M4A (max 50MB)';
    elements.analyzeBtn.disabled = true;

    // Show upload section
    elements.uploadSection.style.display = 'block';
    elements.dashboardSection.style.display = 'none';

    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ==================== UTILITIES ====================
function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

function showNotification(message, type = 'info') {
    // Simple alert for now - can be enhanced with toast notifications
    alert(message);
}
