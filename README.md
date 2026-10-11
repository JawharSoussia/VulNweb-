# VulNweb - Real-Time Cyber Threat Surveillance System

![Status](https://img.shields.io/badge/status-in%20development-yellow)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Overview
VulNweb is an intelligent Chrome extension powered by machine learning that provides real-time threat detection and analysis for browsing security. It integrates network threat detection with VirusTotal URL/file analysis.
## PROJECT PURPOSE

VulNweb is an intelligent security system designed to provide **real-time URL threat detection and analysis** for web browsing. The system uses machine learning with explainable AI to classify URLs as safe, suspicious, or malicious:

- **Malicious URLs** - Detection of phishing, malware distribution, credential harvesting sites
- **Suspicious URLs** - Identification of suspicious patterns and potentially harmful URLs
- **Safe URLs** - Classification of legitimate, trusted URLs
- **Explainable Predictions** - SHAP values show top 3 decision reasons for each classification

**Key Objectives:**
- Deliver <500ms response time for URL threat analysis
- Achieve 95%+ accuracy in URL threat classification
- Provide explainable AI predictions (SHAP values showing decision reasons)
- Detect malicious URLs, phishing, and suspicious patterns
- Enable real-time browser protection via Chrome extension

## Features
- Real-time threat detection using XGBoost ML model 
- VirusTotal API integration for URL and file hash analysis
- Color-coded threat indicators (Green/Orange/Red)
- Explainable AI with top 3 decision reasons
- Instant Slack alerts on critical threats
- Dashboard with threat analytics
- Sub-500ms API response times
- Batch analysis of URLs, file hashes, and network flows

## Architecture
```
Chrome Extension → FastAPI Backend → ML Model → PostgreSQL
                        ↓
                   Threat Intelligence APIs
                        ├─ VirusTotal (URL/File)
                        ├─ Model 
                        └─ Slack Alerts
```



## TECHNOLOGY STACK

### Backend
- **Framework:** FastAPI 0.104.1
- **Server:** Uvicorn 0.24.0
- **Language:** Python 3.10+
- **Database:** PostgreSQL with SQLAlchemy ORM (optional, for production)
- **ORM:** Alembic for migrations

### Machine Learning
- **Primary Model:** XGBoost 2.0.2
- **Model Selection:** Scikit-learn 1.3.2
- **Data Processing:** Pandas 2.1.3, NumPy 1.26.2
- **Explainability:** SHAP 0.43.0, LIME 0.2.0.1
- **Data Imbalance:** Imbalanced-learn 0.11.0 (if needed)

### Frontend
- **Browser:** Chrome/Chromium-based
- **Technology:** Vanilla JavaScript
- **Chrome APIs:**
  - `webRequest` - Request interception
  - `storage` - Local settings persistence
  - `alarms` - Background task scheduling
  - `contextMenus` - Right-click menu integration

### Threat Intelligence
- **VirusTotal API:** vt-py 0.22.0
- **Dataset Source:** Kaggle

### DevOps & Deployment
- **Containerization:** Docker, Docker-Compose
- **Configuration:** Python-dotenv 1.0.0
- **Testing:** pytest 7.4.3, pytest-asyncio 0.21.1
- **Code Quality:** Black 23.12.0, Flake8 6.1.0, isort 5.13.2, mypy 1.7.1

### Utilities
- **HTTP Requests:** requests 2.31.0, httpx 0.25.1
- **Validation:** Pydantic 2.5.0
- **Configuration:** YAML, JSON
- **Logging:** Python-json-logger 2.0.7

---

## 6. TEAM & PERSONNEL

### Project Lead & Developer
**Name:** Soussai Jawhar
**Role:** Full Stack Developer / ML Engineer
**Responsibilities:**
- Architecture design and planning
- Data engineering and feature extraction
- ML model development and optimization
- FastAPI backend implementation
- Chrome extension development
- API integration and testing
- Documentation and deployment
- Performance optimization

**Contact:** soussiajawhar2@gmail.com


## Quick Start

### Prerequisites
- Python 3.10+
- Docker & Docker-Compose
- Chrome Browser
- Kaggle API credentials (optional, for automatic dataset download)

### Local Development

```bash
# Clone and navigate
git clone <repo-url>
cd projet\ VulNweb

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt


# Start services
docker-compose up

# Run API
uvicorn backend.app.main:app --reload
```

### Install Chrome Extension

1. Open `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select `frontend/extension/` folder

## API Endpoints
### Run backend server
```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
 
### Health Check
```bash
GET /health
```


### Network Threat Detection
```bash
# Analyze network flow
POST /threats/network/analyze
{
  "source_ip": "192.168.1.100",
  "destination_ip": "10.0.0.50",
  "source_port": 52345,
  "destination_port": 80,
  "protocol": "TCP",
  "flow_duration": 45.5,
  "total_fwd_packets": 25,
  "total_bwd_packets": 23
}
```

### Batch Analysis
```bash
# Analyze multiple threats
POST /threats/batch-analyze
{
  "urls": ["https://example1.com", "https://example2.com"],
  "file_hashes": ["e4d909c290d0fb1ca068ffaddf22cbd0"],
  "network_flows": [
    {
      "source_ip": "192.168.1.100",
      "destination_ip": "10.0.0.50",
      ...
    }
  ]
}
```

### Dataset Information
```bash
GET /threats/dataset/info
```

## Project Structure


```
.
├── backend/
│   └── app/
│       ├── main.py                 # FastAPI app and endpoints
│       ├── models.py               # Database models
│       ├── schemas.py              # Pydantic schemas
│       ├── virustotal_client.py    # VirusTotal API integration
│       └── dataset_loader.py       # dataset handling
├── frontend/
│   └── extension/                  # Chrome extension files
├── docker-compose.yml              # Multi-container setup
├── Dockerfile                      # Container configuration
└── requirements.txt                # Python dependencies
```

## Environment Variables
```bash    # VirusTotal API key (optional)
DATABASE_URL=postgresql://...         # PostgreSQL connection
SLACK_WEBHOOK_URL=https://...         # Slack alerts (optional)
```

## Contact
soussiajawhar2@gmail.com
