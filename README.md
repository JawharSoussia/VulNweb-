# VulNweb - Real-Time Cyber Threat Surveillance System

![Status](https://img.shields.io/badge/status-in%20development-yellow)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Overview
VulNweb is an intelligent Chrome extension powered by machine learning that provides real-time threat detection and analysis for browsing security. It integrates UNSW-NB15 network threat detection with VirusTotal URL/file analysis.

## Features
- Real-time threat detection using XGBoost ML model trained on UNSW-NB15
- Network traffic analysis with attack classification (DoS, Exploits, Backdoors, etc.)
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
                        ├─ UNSW-NB15 (Network)
                        └─ Slack Alerts
```

## Tech Stack
- **Backend:** FastAPI, PostgreSQL, SQLAlchemy
- **ML:** XGBoost, SHAP, Scikit-learn
- **Dataset:** UNSW-NB15 (2.5M network flow records)
- **Threat Intelligence:** VirusTotal API
- **Frontend:** JavaScript, Chrome API
- **DevOps:** Docker, Docker-Compose, GitHub Actions
- **Monitoring:** Grafana, Prometheus

## Datasets & APIs

### UNSW-NB15 Dataset
- **Source:** [Kaggle UNSW-NB15](https://www.kaggle.com/datasets/mrwellsdavid/unsw-nb15)
- **Samples:** 2,540,047 network flows
- **Features:** 47 network and traffic features
- **Attack Categories:** DoS, Exploits, Backdoors, Analysis, Fuzzers, Reconnaissance, Shellcode, Generic, Worms
- **Training:** Automatically downloaded and cached

### VirusTotal API
- **Capabilities:** URL scanning, file hash lookup, malware detection
- **Detections:** Multi-vendor analysis (70+ antivirus engines)
- **Rate Limits:** Follow free tier limits
- **Setup:** Set `VIRUSTOTAL_API_KEY` environment variable

## Quick Start

### Prerequisites
- Python 3.10+
- Docker & Docker-Compose
- Chrome Browser
- Kaggle API credentials (optional, for automatic dataset download)
- VirusTotal API key (optional, for threat intelligence)

### Local Development

```bash
# Clone and navigate
git clone <repo-url>
cd projet\ 2

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cat > .env << EOF
VIRUSTOTAL_API_KEY=your_virustotal_api_key_here
EOF

# Start services
docker-compose up

# Run API
uvicorn backend.app.main:app --reload
```

### Configure Kaggle API (Optional)
For automatic dataset download:
```bash
# Download credentials from Kaggle account settings
mkdir -p ~/.kaggle
cp kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json
```

### Install Chrome Extension

1. Open `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select `frontend/extension/` folder

## API Endpoints

### Health Check
```bash
GET /health
```

### VirusTotal Integration
```bash
# Scan URL
POST /threats/virustotal/scan-url
{
  "url": "https://example.com"
}

# Scan File Hash
POST /threats/virustotal/scan-file
{
  "file_hash": "e4d909c290d0fb1ca068ffaddf22cbd0"
}
```

### Network Threat Detection (UNSW-NB15)
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
See `PROJECT_PLAN.md` for detailed breakdown.

```
.
├── backend/
│   └── app/
│       ├── main.py                 # FastAPI app and endpoints
│       ├── models.py               # Database models
│       ├── schemas.py              # Pydantic schemas
│       ├── virustotal_client.py    # VirusTotal API integration
│       └── dataset_loader.py       # UNSW-NB15 dataset handling
├── frontend/
│   └── extension/                  # Chrome extension files
├── docker-compose.yml              # Multi-container setup
├── Dockerfile                      # Container configuration
└── requirements.txt                # Python dependencies
```

## Environment Variables
```bash
VIRUSTOTAL_API_KEY=your_api_key       # VirusTotal API key (optional)
DATABASE_URL=postgresql://...         # PostgreSQL connection
SLACK_WEBHOOK_URL=https://...         # Slack alerts (optional)
```

## Contact
soussiajawhar2@gmail.com