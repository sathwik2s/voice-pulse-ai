# VoicePulse AI 🎙️

**Real-Time Speech Emotion Intelligence Dashboard**

A production-ready AI web application that performs speech emotion intelligence by analyzing voice input and detecting emotion + sentiment transitions over time, then visualizes them in an interactive dashboard.

![VoicePulse AI](https://img.shields.io/badge/AI-Emotion%20Recognition-blue)
![Python](https://img.shields.io/badge/Python-3.8+-green)
![Flask](https://img.shields.io/badge/Flask-3.0-red)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 🎯 Features

### Core Capabilities
- **Real-time Emotion Detection** - Analyzes voice recordings with 7 emotion classes
- **Temporal Analysis** - Detects emotion changes over time with 2-second overlapping windows
- **Sentiment Mapping** - Maps emotions to positive/neutral/negative sentiment
- **Transition Detection** - Identifies exact timestamps of emotion shifts
- **Interactive Dashboard** - Beautiful visualizations with Chart.js
- **Audio Playback** - Play audio with emotion markers
- **Report Export** - Download complete JSON analysis reports

### Emotion Classes
- Happy 😊
- Sad 😢
- Angry 😠
- Neutral 😐
- Fear 😨
- Disgust 🤢
- Surprise 😲

---

## 🏗️ Architecture

```
VoicePulseAI/
│
├── backend/                          # AI + Flask Server
│   ├── app.py                        # Flask app & API routes
│   ├── emotion_pipeline.py           # Main AI workflow controller
│   ├── audio_utils.py                # Audio preprocessing & chunking
│   ├── emotion_model.py              # Emotion model loading + inference
│   ├── transition_logic.py           # Detect emotion changes
│   ├── sentiment_map.py              # Emotion → sentiment mapping
│   ├── uploads/                      # Stored input audio
│   ├── reports/                      # Output JSON analysis
│   └── requirements.txt
│
├── frontend/                         # UI Layer
│   ├── index.html                    # Main UI page
│   ├── style.css                     # Premium styling
│   ├── dashboard.js                  # Charts + dashboard logic
│   ├── recorder.js                   # Mic recording logic
│   └── api.js                        # Backend API connector
│
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip
- Modern web browser (Chrome, Firefox, Edge, Safari)

### Installation

1. **Clone or navigate to the project directory**
```bash
cd "c:\Users\sathw\Videos\emotion analyzer"
```

2. **Install Python dependencies**
```bash
cd backend
pip install -r requirements.txt
```

3. **Start the backend server**
```bash
python app.py
```

The backend will start on `http://localhost:5000`

4. **Open the frontend**

Simply open `frontend/index.html` in your web browser, or use a local server:

```bash
cd frontend
python -m http.server 8000
```

Then navigate to `http://localhost:8000`

---

## 📊 API Endpoints

### Health Check
```
GET /health
```
Returns server status

### Analyze Audio
```
POST /analyze
Content-Type: multipart/form-data
Body: audio file

Response:
{
  "success": true,
  "analysis_id": "uuid",
  "timeline": [...],
  "transitions": [...],
  "distribution": {...},
  "confidence_curve": [...],
  "heatmap_data": [...],
  "sentiment_analysis": {...},
  "journey_analysis": {...}
}
```

### Get Report
```
GET /report/<analysis_id>
```
Retrieve saved analysis

### Download Report
```
GET /download/<analysis_id>
```
Download JSON report

---

## 🎨 Dashboard Components

### 1. Emotion Timeline Chart
- X-axis: Time
- Y-axis: Confidence
- Color-coded by emotion
- Hover shows timestamp + confidence

### 2. Confidence Trend
- Line graph of model confidence over time

### 3. Emotion Distribution
- Pie chart showing % duration of each emotion

### 4. Sentiment Gauge
- Visual gauge of overall sentiment polarity

### 5. Emotion Heatmap
- Multi-line chart showing all emotion intensities

### 6. Transition Events Table
- Detailed table of emotion shifts with timestamps

### 7. Audio Player with Markers
- Play audio with clickable emotion markers

---

## 🧠 AI Model

**Model:** `superb/wav2vec2-base-superb-er`

- Pre-trained Wav2Vec2 model from HuggingFace
- Fine-tuned for emotion recognition
- 7-class emotion classification
- Confidence scores for each prediction

### Processing Pipeline

1. **Audio Loading** - Convert to mono, 16kHz, PCM
2. **Segmentation** - 2-second overlapping windows (1s overlap)
3. **Emotion Recognition** - Wav2Vec2 inference per segment
4. **Transition Detection** - Identify emotion changes
5. **Sentiment Mapping** - Map to positive/neutral/negative
6. **Visualization** - Generate dashboard data

---

## 🎯 Use Cases

- **Call Center Analytics** - Analyze customer service calls
- **Mental Health** - Track emotional patterns in therapy
- **Content Creation** - Analyze podcast/video emotions
- **Research** - Study emotional responses in interviews
- **Training** - Improve public speaking emotional delivery

---

## 🔧 Configuration

### Backend Configuration (`backend/app.py`)
```python
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max file size
UPLOAD_FOLDER = 'uploads'
REPORTS_FOLDER = 'reports'
```

### Audio Processing (`backend/audio_utils.py`)
```python
TARGET_SR = 16000      # 16kHz sampling rate
WINDOW_SIZE = 2.0      # 2-second windows
OVERLAP = 1.0          # 1-second overlap
```

### Frontend API (`frontend/api.js`)
```javascript
const API_BASE_URL = 'http://localhost:5000';
```

---

## 📦 Deployment

### Local Development
Already covered in Quick Start

### Production Deployment (Render)

1. **Create `render.yaml`**
```yaml
services:
  - type: web
    name: voicepulse-ai
    env: python
    buildCommand: cd backend && pip install -r requirements.txt
    startCommand: cd backend && gunicorn app:app
    envVars:
      - key: PYTHON_VERSION
        value: 3.9.0
```

2. **Deploy to Render**
- Connect your GitHub repository
- Render will auto-deploy from `render.yaml`

3. **Update Frontend API URL**
- Change `API_BASE_URL` in `frontend/api.js` to your Render URL

### Environment Variables
```
FLASK_ENV=production
FLASK_DEBUG=0
```

---

## 🧪 Testing

### Test Audio Files
Use sample audio files in various formats:
- WAV (recommended)
- MP3
- M4A
- OGG
- WebM

### Browser Testing
- Chrome ✅
- Firefox ✅
- Edge ✅
- Safari ✅

---

## 🎨 Design Features

- **Glassmorphism** - Modern glass card effects
- **Gradient Backgrounds** - Vibrant color schemes
- **Smooth Animations** - Micro-interactions throughout
- **Dark Mode** - Premium dark theme
- **Responsive Design** - Works on all screen sizes
- **Premium Typography** - Inter font family

---

## 🔒 Security

- File type validation
- File size limits (50MB)
- Audio duration limits (10 minutes)
- CORS enabled for frontend
- Input sanitization
- Error handling

---

## 📈 Performance

- **Model Caching** - Singleton pattern for model instance
- **Async Processing** - Non-blocking audio analysis
- **Lazy Loading** - Model loads on first request
- **Efficient Segmentation** - Optimized window processing

---

## 🐛 Troubleshooting

### Backend won't start
- Check Python version (3.8+)
- Install all dependencies: `pip install -r requirements.txt`
- Check port 5000 is available

### Frontend can't connect
- Verify backend is running on port 5000
- Check CORS settings
- Update `API_BASE_URL` if needed

### Model download fails
- Ensure internet connection
- HuggingFace models download on first use
- Check disk space (~500MB needed)

### Audio upload fails
- Check file format (WAV, MP3, M4A)
- Verify file size < 50MB
- Check audio duration < 10 minutes

---

## 📝 License

MIT License - feel free to use for any purpose

---

## 🙏 Acknowledgments

- **HuggingFace** - Wav2Vec2 emotion model
- **Chart.js** - Beautiful charts
- **Flask** - Backend framework
- **Librosa** - Audio processing

---

## 📧 Support

For issues or questions, please open an issue on GitHub.

---

**Built with ❤️ using AI-powered emotion recognition**
#   v o i c e - p u l s e - a i  
 