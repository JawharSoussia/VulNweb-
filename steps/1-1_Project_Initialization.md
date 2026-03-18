# Task 1.1: Project Initialization

**Phase:** Setup & Data Preparation
**Deadline:** Day 2
**Status:** ⏳ Pending
**Dependencies:** None

---

## 📋 Objective
Set up the complete project structure, version control, virtual environment, and Docker scaffolding.

---

## 🎯 What to Do

### Step 1: Create Project Directory Structure

```bash
# Navigate to your project directory
cd /path/to/projet\ 2

# Create main directory structure
mkdir -p backend/{app,tests,models}
mkdir -p frontend/{extension,public,src}
mkdir -p ml_model/{training,inference,data}
mkdir -p data/{raw,processed,train,test}
mkdir -p deployment/{docker,kubernetes,scripts}
mkdir -p docs
mkdir -p tests

# Create root configuration files
touch .gitignore
touch README.md
touch requirements.txt
touch docker-compose.yml
touch Dockerfile
```

**Final Structure:**
```
projet 2/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── models.py
│   │   └── schemas.py
│   ├── tests/
│   │   ├── __init__.py
│   │   └── test_api.py
│   └── requirements.txt
├── frontend/
│   ├── extension/
│   │   ├── manifest.json
│   │   ├── popup.html
│   │   ├── popup.js
│   │   ├── content.js
│   │   └── styles.css
│   └── public/
├── ml_model/
│   ├── training/
│   │   ├── train.py
│   │   └── evaluate.py
│   ├── inference/
│   │   └── predictor.py
│   └── data/
├── data/
│   ├── raw/
│   ├── processed/
│   ├── train/
│   └── test/
├── deployment/
│   ├── docker/
│   ├── kubernetes/
│   └── scripts/
├── docs/
├── tests/
├── .gitignore
├── README.md
├── requirements.txt
├── docker-compose.yml
└── Dockerfile
```

---

### Step 2: Initialize Git Repository

```bash
# Initialize git
git init

# Create .gitignore file
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
ENV/
env/
.venv

# IDE
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Data & Models
data/raw/*
data/processed/*
ml_model/training/models/*.pkl
ml_model/training/models/*.joblib

# Environment variables
.env
.env.local

# Test coverage
.coverage
htmlcov/

# Database
*.db
*.sqlite
*.sqlite3

# Logs
logs/
*.log

# Node (for Chrome extension)
node_modules/
package-lock.json
dist/

# Docker
.dockerignore

# Temporary files
*.tmp
*.temp
EOF

# First commit
git add .
git commit -m "Initial project structure setup"
```

---

### Step 3: Set Up Python Virtual Environment

**Option A: Using venv (Recommended for simplicity)**

```bash
# Create virtual environment
python -m venv venv

# Activate (on Windows)
venv\Scripts\activate

# Activate (on macOS/Linux)
source venv/bin/activate

# Verify activation (you should see (venv) in terminal)
python --version  # Should be 3.10+
```

**Option B: Using Poetry (Better for dependency management)**

```bash
# Install Poetry (if not already installed)
pip install poetry

# Create Poetry project
poetry init --no-interaction

# Add dependencies (we'll expand this later)
poetry add python="^3.10"
poetry add fastapi uvicorn pandas numpy scikit-learn xgboost
poetry add pydantic sqlalchemy psycopg2-binary
poetry add shap lime requests

# Activate Poetry environment
poetry shell
```

---

### Step 4: Create Initial requirements.txt

```bash
# Create requirements.txt
cat > requirements.txt << 'EOF'
# Web Framework
fastapi==0.104.1
uvicorn==0.24.0

# Data Science
pandas==2.1.3
numpy==1.26.2
scikit-learn==1.3.2
xgboost==2.0.2
imbalanced-learn==0.11.0

# ML Explainability
shap==0.43.0
lime==0.2.0

# Data Validation
pydantic==2.5.0
pydantic-settings==2.1.0

# Database
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
alembic==1.13.0

# API/HTTP
requests==2.31.0
httpx==0.25.1

# Testing
pytest==7.4.3
pytest-cov==4.1.0
pytest-asyncio==0.21.1

# Code Quality
black==23.12.0
flake8==6.1.0
isort==5.13.2
mypy==1.7.1

# Monitoring & Logging
python-json-logger==2.0.7

# Utilities
python-dotenv==1.0.0
pyyaml==6.0.1
EOF

# Install all dependencies
pip install -r requirements.txt
```

---

### Step 5: Create Docker Setup

**Create Dockerfile (for backend):**

```bash
cat > Dockerfile << 'EOF'
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY backend/app /app/app
COPY ml_model /app/ml_model

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF
```

**Create docker-compose.yml:**

```bash
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  # PostgreSQL Database
  db:
    image: postgres:15-alpine
    container_name: vulnweb_db
    environment:
      POSTGRES_USER: vulnweb
      POSTGRES_PASSWORD: password123
      POSTGRES_DB: vulnweb_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U vulnweb"]
      interval: 10s
      timeout: 5s
      retries: 5

  # FastAPI Backend
  backend:
    build: .
    container_name: vulnweb_backend
    depends_on:
      db:
        condition: service_healthy
    environment:
      DATABASE_URL: postgresql://vulnweb:password123@db:5432/vulnweb_db
      LOG_LEVEL: info
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app/backend
      - ./ml_model:/app/ml_model
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

volumes:
  postgres_data:
EOF
```

---

### Step 6: Create Placeholder Files

**backend/app/__init__.py:**
```bash
cat > backend/app/__init__.py << 'EOF'
"""VulNweb Backend API"""
__version__ = "0.1.0"
EOF
```

**backend/app/main.py:**
```bash
cat > backend/app/main.py << 'EOF'
"""Main FastAPI Application"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="VulNweb Threat Detection API",
    description="Real-time cyber threat surveillance system",
    version="0.1.0"
)

# CORS Configuration for Chrome Extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Will restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "version": "0.1.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
EOF
```

**backend/app/models.py:**
```bash
cat > backend/app/models.py << 'EOF'
"""Database Models"""
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Prediction(Base):
    """Prediction Log Model"""
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String, index=True)
    url = Column(String)
    threat_score = Column(Float)
    explanation = Column(String)
    confidence = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

class Feedback(Base):
    """User Feedback Model"""
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    prediction_id = Column(Integer)
    user_feedback = Column(String)  # "correct" or "incorrect"
    created_at = Column(DateTime, default=datetime.utcnow)
EOF
```

**backend/app/schemas.py:**
```bash
cat > backend/app/schemas.py << 'EOF'
"""Pydantic Schemas (Data Contracts)"""
from pydantic import BaseModel
from typing import List

class PredictionRequest(BaseModel):
    """Input schema for prediction request"""
    url: str
    ip_address: str
    file_hash: str = None
    logs: str = None

class ExplanationItem(BaseModel):
    """Single explanation reason"""
    reason: str
    importance: float

class PredictionResponse(BaseModel):
    """Output schema for prediction response"""
    threat_score: float  # 0-100
    confidence: float    # 0-1
    explanation: List[ExplanationItem]
    threat_level: str    # "safe", "suspicious", "critical"

class FeedbackRequest(BaseModel):
    """User feedback schema"""
    prediction_id: int
    is_correct: bool
    comments: str = None
EOF
```

---

### Step 7: Create README.md Template

```bash
cat > README.md << 'EOF'
# VulNweb - Real-Time Cyber Threat Surveillance System

![Status](https://img.shields.io/badge/status-in%20development-yellow)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Overview
VulNweb is an intelligent Chrome extension powered by machine learning that provides real-time threat detection and analysis for browsing security.

## Features
- 🎯 Real-time threat detection using XGBoost ML model
- 🔴 Color-coded threat indicators (Green/Orange/Red)
- 📊 Explainable AI with top 3 decision reasons
- 🔔 Instant Slack alerts on critical threats
- 📈 Dashboard with threat analytics
- ⚡ Sub-500ms API response times

## Architecture
```
Chrome Extension → FastAPI Backend → ML Model → PostgreSQL
                        ↓
                   Threat Intelligence APIs
                        ↓
                   Slack Alerts
```

## Tech Stack
- **Backend:** FastAPI, PostgreSQL, SQLAlchemy
- **ML:** XGBoost, SHAP, Scikit-learn
- **Frontend:** JavaScript, Chrome API
- **DevOps:** Docker, Docker-Compose, GitHub Actions
- **Monitoring:** Grafana, Prometheus

## Quick Start

### Prerequisites
- Python 3.10+
- Docker & Docker-Compose
- Chrome Browser

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

## Project Structure
See `PROJECT_PLAN.md` for detailed breakdown.

## Contributing
[To be updated during development]

## License
MIT

## Contact
[Project details]
EOF
```

---

### Step 8: Verify Setup

```bash
# Check Python version
python --version  # Should be 3.10+

# Verify virtual environment
pip list | head

# Test fastapi import
python -c "import fastapi; print(fastapi.__version__)"

# Test Docker (if installed)
docker --version
docker-compose --version
```

---

## ✅ Checklist

- [ ] Directory structure created
- [ ] Git initialized with .gitignore
- [ ] Virtual environment activated
- [ ] requirements.txt created
- [ ] Docker & docker-compose.yml configured
- [ ] Placeholder Python files created
- [ ] README.md created
- [ ] First commit made (`git add . && git commit -m "Initial setup"`)
- [ ] All imports verified (fastapi, pandas, sklearn, etc.)

---

## 🔗 Next Steps

✅ **Task 1.1 Complete** → Move to **Task 1.2: Data Collection & EDA**

---

## 📝 Common Issues

| Issue | Solution |
|-------|----------|
| Python version too old | Install Python 3.10+: `python.org` |
| Virtual env not activating | Try: `python -m venv --upgrade-deps venv` |
| Docker not found | Install from `docker.com` |
| Permission error on .sh files | Run: `chmod +x script.sh` |

---

**Created:** 2026-03-17
**Last Updated:** 2026-03-17
