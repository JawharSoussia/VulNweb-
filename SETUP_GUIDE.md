# VulNweb Setup Guide - UNSW-NB15 & VirusTotal Integration

This guide walks you through setting up VulNweb with UNSW-NB15 network threat detection and VirusTotal API integration.

## Prerequisites

- Python 3.10 or higher
- Docker & Docker-Compose (optional, for containerized setup)
- Git
- For automatic dataset download: Kaggle API credentials
- For threat intelligence: VirusTotal API key

## Step 1: Get VirusTotal API Key

1. Go to https://www.virustotal.com/
2. Sign up for a free account
3. Navigate to your API section
4. Copy your API key

## Step 2: Get Kaggle API Credentials (Optional)

For automatic download of UNSW-NB15 dataset:

1. Log into your Kaggle account at https://www.kaggle.com/
2. Go to Settings → Account → API → "Create New API Token"
3. This downloads `kaggle.json`
4. Save it to `~/.kaggle/kaggle.json`
5. Set permissions: `chmod 600 ~/.kaggle/kaggle.json`

## Step 3: Clone and Setup

```bash
# Clone repository
git clone <repo-url>
cd projet\ 2

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Step 4: Configure Environment Variables

Create a `.env` file from the template:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```bash
# VirusTotal API Configuration
VIRUSTOTAL_API_KEY=your_api_key_here

# Optional: Slack notifications
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Optional: Database (if not using Docker)
DATABASE_URL=postgresql://user:password@localhost:5432/vulnweb
```

## Step 5: Start Services

### Option A: Using Docker Compose (Recommended)

```bash
# Start all services
docker-compose up -d

# Verify services are running
docker-compose ps

# View logs
docker-compose logs -f backend
docker-compose logs -f db
```

### Option B: Local Development

```bash
# Start PostgreSQL (ensure it's installed and running)
# On Windows: Start PostgreSQL service from Services
# On macOS: brew services start postgresql
# On Linux: sudo systemctl start postgresql

# Run migrations (if needed)
alembic upgrade head

# Start the API server
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

## Step 6: Download UNSW-NB15 Dataset

### Option A: Automatic Download via API

```bash
# Make API call to trigger download
curl -X GET http://localhost:8000/threats/download-dataset

# This requires Kaggle API credentials configured
```

### Option B: Manual Download

1. Visit https://www.kaggle.com/datasets/mrwellsdavid/unsw-nb15
2. Download the CSV files
3. Place them in `data/unsw/` directory

### Option C: Using Kaggle CLI

```bash
# Download dataset
kaggle datasets download -d mrwellsdavid/unsw-nb15 -p ./data/unsw

# Unzip
cd data/unsw
unzip unsw-nb15.zip
```

## Step 7: Verify Installation

```bash
# Check API health
curl http://localhost:8000/health

# Get dataset info
curl http://localhost:8000/threats/dataset/info

# Test VirusTotal integration (if API key configured)
curl -X POST http://localhost:8000/threats/virustotal/scan-url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.google.com"}'
```

## API Usage Examples

### 1. Scan URL with VirusTotal

```bash
curl -X POST http://localhost:8000/threats/virustotal/scan-url \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com"
  }'
```

Response:
```json
{
  "scan_target": "https://example.com",
  "scan_type": "url",
  "malicious_detections": 0,
  "total_vendors": 70,
  "detection_ratio": "0/70",
  "threat_level": "safe",
  "additional_data": {
    "categories": {...}
  }
}
```

### 2. Scan File Hash

```bash
curl -X POST http://localhost:8000/threats/virustotal/scan-file \
  -H "Content-Type: application/json" \
  -d '{
    "file_hash": "e4d909c290d0fb1ca068ffaddf22cbd0"
  }'
```

### 3. Analyze Network Flow (UNSW-NB15)

```bash
curl -X POST http://localhost:8000/threats/network/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "source_ip": "192.168.1.100",
    "destination_ip": "10.0.0.50",
    "source_port": 52345,
    "destination_port": 80,
    "protocol": "TCP",
    "flow_duration": 45.5,
    "total_fwd_packets": 25,
    "total_bwd_packets": 23
  }'
```

Response:
```json
{
  "threat_score": 23.5,
  "threat_level": "safe",
  "confidence": 0.92,
  "attack_category": null,
  "explanation": [
    {
      "reason": "Unusual packet ratio detected",
      "importance": 0.35
    },
    {
      "reason": "High byte transfer rate",
      "importance": 0.28
    },
    {
      "reason": "Port combination suspicious",
      "importance": 0.22
    }
  ]
}
```

### 4. Batch Analysis

```bash
curl -X POST http://localhost:8000/threats/batch-analyze \
  -H "Content-Type: application/json" \
  -d '{
    "urls": [
      "https://example1.com",
      "https://example2.com"
    ],
    "file_hashes": [
      "e4d909c290d0fb1ca068ffaddf22cbd0"
    ],
    "network_flows": [
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
    ]
  }'
```

## UNSW-NB15 Dataset Features

The dataset includes 47 network features:

### Flow Features
- `srcip`: Source IP address
- `dstip`: Destination IP address
- `sport`: Source port
- `dstp`: Destination port
- `proto`: Protocol type (TCP, UDP, ICMP)

### Duration Features
- `dur`: Connection duration
- `stime`: Start time
- `ltime`: Last time

### Flow Volume Features
- `sbytes`: Source to destination bytes
- `dbytes`: Destination to source bytes
- `spkts`: Source to destination packets
- `dpkts`: Destination to source packets

### Packet Features
- `sttl`: Source TTL
- `dttl`: Destination TTL
- `sloss`: Source loss
- `dloss`: Destination loss

### And more... (47 total)

### Attack Categories
- DoS (Denial of Service)
- Exploits
- Backdoors
- Analysis
- Fuzzers
- Reconnaissance
- Shellcode
- Generic
- Worms

## Troubleshooting

### VirusTotal API Not Working

```
Error: VirusTotal service not available
```

Solution:
1. Check if `VIRUSTOTAL_API_KEY` is set in `.env`
2. Verify API key is valid at https://www.virustotal.com/
3. Check API rate limits (free tier has limits)

### Dataset Not Found

```
Error: Dataset file not found
```

Solution:
1. Download dataset from Kaggle manually
2. Place CSV files in `data/unsw/` directory
3. Verify files exist: `ls data/unsw/`

### Database Connection Error

```
Error: Could not connect to database
```

Solution:
1. Ensure PostgreSQL is running
2. Verify `DATABASE_URL` in `.env` is correct
3. Check database user/password credentials
4. For Docker: `docker-compose logs db`

### Port Already in Use

```
Error: Address already in use
```

Solution:
1. Stop existing service: `lsof -i :8000` (Linux/Mac)
2. Or change port: Modify docker-compose.yml or uvicorn command

## Development

### Run Tests

```bash
pytest tests/ -v --cov=backend
```

### Code Quality

```bash
# Format code
black backend/

# Check linting
flake8 backend/

# Type checking
mypy backend/
```

### View API Documentation

Once the server is running:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Performance Tips

1. **Caching**: Implement Redis for frequently scanned URLs
2. **Batch Processing**: Use `/threats/batch-analyze` for multiple items
3. **Dataset Optimization**: Filter UNSW-NB15 by attack type for faster training
4. **Connection Pooling**: Adjust PostgreSQL pool size in production

## Next Steps

1. Train XGBoost model on UNSW-NB15 data
2. Integrate SHAP for explainability
3. Set up Slack notifications for critical threats
4. Deploy Chrome extension
5. Configure Grafana monitoring dashboard

## Support

For issues or questions:
- Check `/health` endpoint for service status
- Review logs: `docker-compose logs -f`
- Visit Kaggle dataset page: https://www.kaggle.com/datasets/mrwellsdavid/unsw-nb15
- VirusTotal documentation: https://developers.virustotal.com/

## Resources

- UNSW-NB15 Paper: https://www.unsw.adfa.edu.au/unsw-canberra/academic/schools/school-of-cyber-and-security/cybersecurity-research/datasets/unsw-nb15-dataset
- VirusTotal API: https://developers.virustotal.com/reference
- FastAPI Documentation: https://fastapi.tiangolo.com/
- XGBoost Documentation: https://xgboost.readthedocs.io/
