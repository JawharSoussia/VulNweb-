# VulNweb Project - Complete Breakdown & Timeline

**Project:** Real-Time Cyber Threat Surveillance & Analysis System
**Objective:** Supervised ML model for real-time threat prediction with DevOps integration
**Started:** 2026-03-17

---

## 📋 Tech Stack Overview

### Core Technologies
- **Language:** Python 3.10+
- **Backend:** FastAPI (API Gateway & Inference)
- **ML Models:** XGBoost or Random Forest (binary classification)
- **Explainability:** SHAP or LIME (XAI)
- **Data Validation:** Pydantic (Data Contracts)
- **Database:** PostgreSQL (logs & scores)
- **Frontend:** JavaScript (Chrome Extension)
- **Deployment:** Docker & Docker-Compose
- **Monitoring:** Grafana (optional)
- **Cloud:** AWS/GCP/Azure (Free Tier)
- **Alerting:** Slack/Discord webhooks
- **Version Control:** Git + CI/CD

---

## 🎯 Project Phases & Timeline

### Phase 1: Project Setup & Data Preparation (Week 1-2)
**Duration:** ~2 weeks
**Dependencies:** None

#### Tasks:
- [ ] **1.1 - Project Initialization**
  - Create Git repository structure
  - Set up Python virtual environment (Poetry or venv)
  - Create Docker & Docker-Compose base files
  - Set up project directories: `/backend`, `/frontend`, `/ml_model`, `/data`, `/tests`
  - **Deadline:** Day 2
  - **Tech Stack:** Git, Python 3.10+, Poetry/venv, Docker

- [ ] **1.2 - Data Collection & EDA**
  - Identify threat intelligence data sources (IP addresses, malware signatures, intrusion logs)
  - Collect labeled dataset (~5,000-10,000 samples minimum)
  - Perform Exploratory Data Analysis (EDA)
  - Document class balance (handle imbalanced data)
  - Create `/data` directory with train/test splits
  - **Deadline:** Day 8
  - **Tech Stack:** Pandas, NumPy, Matplotlib, Seaborn, Scikit-learn

- [ ] **1.3 - Feature Engineering**
  - Extract features from logs/IPs:
    - Domain entropy, IP reputation, suspicious ports
    - Connection patterns, temporal features
    - Malware signature matches
  - Normalize and scale features
  - Handle missing values & outliers
  - **Deadline:** Day 12
  - **Tech Stack:** Pandas, NumPy, Scikit-learn, Feature-engine

- [ ] **1.4 - Data Quality Tests (Data Contracts)**
  - Define schema validation (Pydantic models)
  - Create unit tests for data structure
  - Implement freshness checks
  - Set up automated validation pipeline
  - **Deadline:** Day 14
  - **Tech Stack:** Pydantic, pytest

---

### Phase 2: ML Model Development (Week 2-4)
**Duration:** ~2.5 weeks
**Dependencies:** Phase 1 complete

#### Tasks:
- [ ] **2.1 - Model Selection & Training**
  - Train baseline models (Logistic Regression as baseline)
  - Train Random Forest and XGBoost
  - Implement cross-validation (5-fold)
  - **Deadline:** Day 18
  - **Tech Stack:** Scikit-learn, XGBoost, Pandas

- [ ] **2.2 - Class Imbalance Handling (SMOTE)**
  - Analyze class distribution
  - Apply SMOTE to training set
  - Evaluate impact on recall vs precision
  - Document approach in technical report
  - **Deadline:** Day 20
  - **Tech Stack:** Imbalanced-learn (SMOTE), Scikit-learn

- [ ] **2.3 - Model Evaluation & Metrics**
  - Calculate: Precision, Recall, F1-Score, ROC-AUC
  - Create confusion matrix
  - Document performance on test set
  - **Target:** Recall > 90%, F1-Score > 0.85
  - **Deadline:** Day 21
  - **Tech Stack:** Scikit-learn, Matplotlib

- [ ] **2.4 - Explainability (XAI)**
  - Integrate SHAP for feature importance
  - Extract top 3 decision reasons for each prediction
  - Create explanation interface (text format for API)
  - Test with sample predictions
  - **Deadline:** Day 24
  - **Tech Stack:** SHAP, Matplotlib

- [ ] **2.5 - Model Serialization & Packaging**
  - Save best model (.pkl or .joblib)
  - Version model with metadata (features, performance metrics)
  - Create model loading utility
  - Package for API consumption
  - **Deadline:** Day 25
  - **Tech Stack:** joblib/pickle, PyYAML

---

### Phase 3: Backend API Development (Week 3-5)
**Duration:** ~2 weeks
**Dependencies:** Phase 2.5 complete

#### Tasks:
- [ ] **3.1 - FastAPI Setup**
  - Initialize FastAPI app structure
  - Configure CORS for Chrome extension
  - Set up logging and error handling
  - Create health check endpoint (`GET /health`)
  - **Deadline:** Day 20
  - **Tech Stack:** FastAPI, Uvicorn, Python-logging

- [ ] **3.2 - Prediction Endpoint**
  - Create `POST /predict` endpoint
  - Input validation with Pydantic models:
    - `PredictionRequest`: url, ip, file_hash, logs
    - `PredictionResponse`: threat_score, explanation, confidence
  - Load & run ML model
  - Return threat_score (0-100) + top 3 explanation reasons
  - Add request logging
  - **Deadline:** Day 23
  - **Tech Stack:** FastAPI, Pydantic, ML model

- [ ] **3.3 - Feedback Loop Endpoint**
  - Create `POST /feedback` endpoint
  - Accept user corrections (false positive/negative)
  - Store feedback in database
  - Log for future model retraining
  - **Deadline:** Day 24
  - **Tech Stack:** FastAPI, PostgreSQL, SQLAlchemy

- [ ] **3.4 - Threat Intelligence Integration**
  - Integrate external threat API (VirusTotal, AbuseIPDB, etc.)
  - Enrich incoming data with known threat signatures
  - Cache API calls to reduce latency
  - Handle API rate limits
  - **Deadline:** Day 26
  - **Tech Stack:** FastAPI, Requests, Redis (optional)

- [ ] **3.5 - Database Setup**
  - Set up PostgreSQL connection
  - Create table schemas:
    - `predictions` (id, ip, url, threat_score, timestamp, explanation)
    - `feedback` (id, prediction_id, user_correction, timestamp)
  - Set up connection pooling
  - Create migrations
  - **Deadline:** Day 27
  - **Tech Stack:** PostgreSQL, SQLAlchemy, Alembic

- [ ] **3.6 - API Testing & Documentation**
  - Write unit tests for all endpoints
  - Generate Swagger/OpenAPI documentation
  - Test with sample payloads
  - Validate response times < 500ms
  - **Deadline:** Day 28
  - **Tech Stack:** pytest, FastAPI test client

---

### Phase 4: Frontend - Chrome Extension Development (Week 4-6)
**Duration:** ~2.5 weeks
**Dependencies:** Phase 3.2 complete (Prediction endpoint)

#### Tasks:
- [ ] **4.1 - Chrome Extension Setup**
  - Create project structure: manifest.json, popup.html, content.js
  - Define extension permissions (activeTab, scripting, webRequest)
  - Set up icon/UI assets (red/orange/green threat indicators)
  - **Deadline:** Day 26
  - **Tech Stack:** JavaScript, HTML, CSS, Chrome API

- [ ] **4.2 - Content Script & Data Extraction**
  - Detect current URL/domain
  - Extract page metadata (IP, headers if available)
  - Monitor downloads (filename, file hash attempts)
  - Capture network logs
  - **Deadline:** Day 29
  - **Tech Stack:** JavaScript, Chrome Content Scripts

- [ ] **4.3 - API Communication**
  - Implement POST requests to backend API
  - Handle auth tokens if needed
  - Add error handling & retry logic
  - Cache responses (avoid duplicate API calls)
  - **Deadline:** Day 31
  - **Tech Stack:** JavaScript, Fetch API

- [ ] **4.4 - UI/UX - Color-Coded Threat Indicator**
  - Display threat score as popup badge:
    - **Green (0-30%):** Safe
    - **Orange (30-70%):** Suspicious
    - **Red (70-100%):** Critical threat
  - Show threat score percentage
  - Display top 3 decision reasons
  - Add manual feedback button ("This is/isn't a threat")
  - **Deadline:** Day 33
  - **Tech Stack:** HTML, CSS, JavaScript

- [ ] **4.5 - Alert System**
  - Show browser notification on critical threat (>90%)
  - Suggest blocking/allowing action
  - Log all alerts locally
  - **Deadline:** Day 34
  - **Tech Stack:** Chrome Notifications API

- [ ] **4.6 - Extension Testing & Packaging**
  - Test on multiple websites
  - Package extension for Chrome Web Store
  - Create install instructions
  - **Deadline:** Day 35
  - **Tech Stack:** Chrome Developer Tools

---

### Phase 5: Integration & Testing (Week 6-7)
**Duration:** ~1.5 weeks
**Dependencies:** Phase 3 & 4 complete

#### Tasks:
- [ ] **5.1 - End-to-End Testing**
  - Test extension → API → ML model → response flow
  - Verify threat scores are returned correctly
  - Test feedback integration (corrections update database)
  - Validate explanation accuracy
  - **Deadline:** Day 38
  - **Tech Stack:** pytest, Selenium (for extension testing)

- [ ] **5.2 - Performance Testing**
  - Measure API latency (target: <500ms per request)
  - Load test with concurrent requests
  - Optimize database queries if needed
  - Profile ML inference time
  - **Deadline:** Day 40
  - **Tech Stack:** Apache JMeter, Locust, cProfile

- [ ] **5.3 - Data Contract Validation**
  - Run all data quality tests
  - Validate incoming/outgoing data schemas
  - Ensure freshness checks pass
  - **Deadline:** Day 41
  - **Tech Stack:** pytest, Great Expectations (optional)

- [ ] **5.4 - Security & Error Handling**
  - Add input sanitization
  - Implement rate limiting on API
  - Handle all edge cases (malformed requests, timeouts)
  - Test with invalid/suspicious inputs
  - **Deadline:** Day 42
  - **Tech Stack:** FastAPI middleware, security best practices

---

### Phase 6: Deployment & Monitoring (Week 7-8)
**Duration:** ~1.5 weeks
**Dependencies:** Phase 5 complete

#### Tasks:
- [ ] **6.1 - Docker & Docker-Compose Setup**
  - Create Dockerfiles for:
    - FastAPI backend
    - PostgreSQL database
  - Write docker-compose.yml orchestrating all services
  - Test local deployment
  - **Deadline:** Day 43
  - **Tech Stack:** Docker, Docker-Compose

- [ ] **6.2 - Alerting System**
  - Set up Slack/Discord webhook
  - Implement alert trigger (threat_score > 90%)
  - Create alert message template with:
    - URL/IP detected
    - Threat score
    - Top 3 reasons
    - Timestamp
  - Test alerts manually
  - **Deadline:** Day 45
  - **Tech Stack:** Slack/Discord API, Python requests

- [ ] **6.3 - Database Monitoring**
  - Set up database backups
  - Monitor disk usage & query performance
  - Create admin dashboard for log inspection
  - **Deadline:** Day 46
  - **Tech Stack:** PostgreSQL, scripts

- [ ] **6.4 - Grafana Setup (Optional but Recommended)**
  - Create Grafana dashboard
  - Display metrics:
    - Threats detected per hour
    - Model precision/recall over time
    - API latency percentiles
    - Database query times
  - Set up data source to PostgreSQL
  - **Deadline:** Day 47
  - **Tech Stack:** Grafana, Prometheus (optional)

- [ ] **6.5 - Cloud Deployment**
  - Choose: AWS, GCP, or Azure (Free Tier)
  - Deploy Docker containers to cloud
  - Set up public URL for dashboard/API
  - Configure SSL/TLS certificates
  - **Deadline:** Day 48
  - **Tech Stack:** AWS/GCP/Azure, Docker Registry

- [ ] **6.6 - CI/CD Pipeline**
  - Set up GitHub Actions or GitLab CI
  - Configure automatic tests on push
  - Build & push Docker images
  - Deploy to cloud on main branch
  - **Deadline:** Day 49
  - **Tech Stack:** GitHub Actions, Docker Registry

---

### Phase 7: Documentation & Final Report (Week 8-9)
**Duration:** ~1.5 weeks
**Dependencies:** Phase 6 complete

#### Tasks:
- [ ] **7.1 - API Documentation**
  - Auto-generate from Swagger (FastAPI)
  - Document all endpoints with examples
  - Include authentication (if applicable)
  - Provide curl/Python examples
  - **Deadline:** Day 50
  - **Tech Stack:** OpenAPI/Swagger

- [ ] **7.2 - Installation & Setup Guide**
  - Document system requirements
  - Provide step-by-step installation instructions
  - Include Docker setup commands
  - Provide configuration examples
  - **Deadline:** Day 51
  - **Tech Stack:** Markdown

- [ ] **7.3 - Chrome Extension Installation**
  - Publish on Chrome Web Store (or provide .crx file)
  - Write installation guide for users
  - Include troubleshooting section
  - **Deadline:** Day 52
  - **Tech Stack:** Chrome Web Store

- [ ] **7.4 - Technical Report (PDF)**
  - Executive Summary
  - Architecture explanation (diagrams)
  - ML Model performance section:
    - Precision, Recall, F1-Score, ROC-AUC
    - Confusion matrix
    - Class imbalance handling (SMOTE details)
  - Data Engineering approach
  - Challenges & solutions
  - Future improvements
  - Appendix: Code snippets, training process
  - **Deadline:** Day 53
  - **Tech Stack:** LaTeX/Markdown → PDF converter, Diagrams

- [ ] **7.5 - Demo Video**
  - Screen recording showing:
    - Extension installation
    - Normal browsing with safe sites (green)
    - Visit simulated malicious site (red)
    - Alert notification triggered
    - Dashboard showing threat logs
    - API documentation
  - Add narration explaining key features
  - Length: 5-10 minutes
  - **Deadline:** Day 54
  - **Tech Stack:** OBS/Camtasia, FFmpeg

- [ ] **7.6 - README & GitHub Release**
  - Update README.md with badges, overview, quick start
  - Create GitHub release with all deliverables
  - Tag version (v1.0)
  - **Deadline:** Day 55
  - **Tech Stack:** Git, GitHub

---

## 📊 Critical Dependencies Map

```
Phase 1 (Setup & Data)
    ↓
Phase 2 (ML Model) ⟵ Completed Phase 1
    ↓
Phase 3 (Backend API) ⟵ Completed Phase 2.5
    ↓ (parallel)
Phase 4 (Chrome Extension) ⟵ Completed Phase 3.2
    ↓
Phase 5 (Integration & Testing) ⟵ Completed Phase 3 & 4
    ↓
Phase 6 (Deployment & Monitoring) ⟵ Completed Phase 5
    ↓
Phase 7 (Documentation) ⟵ Completed Phase 6
```

---

## 🎯 Key Milestones

| Milestone | Target Date | Deliverable |
|-----------|------------|-------------|
| **M1:** Data & Model Ready | Day 25 | Trained ML model + evaluation metrics |
| **M2:** API Functional | Day 28 | POST /predict endpoint + tests |
| **M3:** Chrome Extension Basic | Day 34 | Color-coded UI, API communication |
| **M4:** Full Integration Tested | Day 42 | End-to-end flow working |
| **M5:** Deployed to Cloud | Day 49 | Public URL + CI/CD active |
| **M6:** Final Deliverables | Day 55 | Report, video, Git repo, extension release |

---

## ✅ Deliverables Checklist

- [ ] **Functional Chrome Extension** - Link for installation
- [ ] **API Documentation** - Swagger/OpenAPI spec
- [ ] **Demo Video** - 5-10 min walkthrough (YouTube or GitHub)
- [ ] **Git Repository** - Public with:
  - [ ] Source code (organized structure)
  - [ ] Unit tests (pytest)
  - [ ] CI/CD pipeline (.github/workflows)
  - [ ] Docker files
  - [ ] README.md
- [ ] **Deployed Application** - Public URL to dashboard
- [ ] **Technical Report (PDF)** - Including:
  - [ ] Architecture diagram
  - [ ] Model performance metrics (Precision, Recall, F1, ROC-AUC)
  - [ ] Class imbalance strategy (SMOTE)
  - [ ] Challenges & solutions
  - [ ] Future improvements

---

## 🚀 Success Criteria

| Criterion | Target |
|-----------|--------|
| **Model Recall** | > 90% (catch real threats) |
| **Model Precision** | > 85% (minimize false alarms) |
| **API Response Time** | < 500ms per request |
| **Extension Performance** | No noticeable browser slowdown |
| **Data Quality** | 100% schema compliance |
| **Uptime** | 99% (production) |
| **Alert Response** | Slack notification within 5 seconds |

---

## 📝 Notes & Assumptions

- **Data Sources:** Assume access to public threat intel APIs or datasets
- **Simulated Threats:** Use test URLs/IPs for demo (don't create real malicious content)
- **Scalability:** Current design handles moderate traffic; optimization for production can follow
- **Security:** Use dummy API keys for demo; secure proper keys in production
- **Privacy:** Ensure GDPR/privacy compliance when storing user data

---

## 🔧 Quick Reference - Key Commands

```bash
# Setup
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt

# Run locally
docker-compose up

# Run tests
pytest tests/ -v

# Format code
black .
flake8 .

# Build for production
docker-compose -f docker-compose.prod.yml up
```

---

**Last Updated:** 2026-03-17
