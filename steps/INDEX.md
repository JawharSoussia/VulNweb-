# Project Tasks Index

**Navigation for VulNweb Project - Complete Implementation Guide**

---

## 📑 Quick Navigation

### 🔵 Phase 1: Setup & Data Preparation (Days 1-14)

| Task | File | Status | Deadline |
|------|------|--------|----------|
| **1.1** Project Initialization | [1-1_Project_Initialization.md](1-1_Project_Initialization.md) | ⏳ | Day 2 |
| **1.2** Data Collection & EDA | [1-2_Data_Collection_and_EDA.md](1-2_Data_Collection_and_EDA.md) | ⏳ | Day 8 |
| **1.3** Feature Engineering | [1-3_Feature_Engineering.md](1-3_Feature_Engineering.md) | ⏳ | Day 12 |
| **1.4** Data Quality Tests | [1-4_Data_Quality_Tests.md](1-4_Data_Quality_Tests.md) | ⏳ | Day 14 |

**Deliverables:**
- ✅ Project structure with Git repo
- ✅ Training/validation/test datasets
- ✅ Preprocessed features
- ✅ Data quality validation pipeline

---

### 🟢 Phase 2: ML Model Development (Days 15-25)

| Task | File | Status | Deadline |
|------|------|--------|----------|
| **2.1** Model Selection & Training | [2-1_Model_Selection_and_Training.md](2-1_Model_Selection_and_Training.md) | ⏳ | Day 18 |
| **2.2** Class Imbalance (SMOTE) | [2-2_Class_Imbalance_SMOTE.md](2-2_Class_Imbalance_SMOTE.md) | ⏳ | Day 20 |
| **2.3** Model Evaluation | [2-3_Model_Evaluation.md](2-3_Model_Evaluation.md) | ⏳ | Day 21 |
| **2.4** Explainability (SHAP) | [2-4_Explainability_SHAP.md](2-4_Explainability_SHAP.md) | ⏳ | Day 24 |
| **2.5** Model Serialization | [2-5_Model_Serialization.md](2-5_Model_Serialization.md) | ⏳ | Day 25 |

**Deliverables:**
- ✅ Trained XGBoost/Random Forest model
- ✅ Recall ≥ 90%, F1 ≥ 0.85
- ✅ SHAP explanations for predictions
- ✅ Model package (serialized + metadata)

---

### 🟡 Phase 3: Backend API Development (Days 16-28)

| Task | File | Status | Deadline |
|------|------|--------|----------|
| **3.1** FastAPI Setup | [3-1_FastAPI_Setup.md](3-1_FastAPI_Setup.md) | ⏳ | Day 20 |
| **3.2** Prediction Endpoint | [3-2_Prediction_Endpoint.md](3-2_Prediction_Endpoint.md) | ⏳ | Day 23 |
| **3.3** Feedback Loop | `3-3_Feedback_Endpoint.md` (in progress) | ⏳ | Day 24 |
| **3.4** Threat Intelligence | `3-4_Threat_Intelligence.md` (planned) | ⏳ | Day 26 |
| **3.5** Database Setup | `3-5_Database_Setup.md` (planned) | ⏳ | Day 27 |
| **3.6** API Testing | `3-6_API_Testing.md` (planned) | ⏳ | Day 28 |

**Deliverables:**
- ✅ FastAPI server with CORS
- ✅ POST /predict endpoint
- ✅ Real-time threat detection
- ✅ PostgreSQL integration
- ✅ API documentation

---

### 🟣 Phase 4: Chrome Extension (Days 21-35)

| Task | File | Status | Deadline |
|------|------|--------|----------|
| **4.1** Extension Setup | `4-1_Extension_Setup.md` (planned) | ⏳ | Day 26 |
| **4.2** Content Script | `4-2_Content_Script.md` (planned) | ⏳ | Day 29 |
| **4.3** API Communication | `4-3_API_Communication.md` (planned) | ⏳ | Day 31 |
| **4.4** UI/UX Threat Indicator | `4-4_UI_Threat_Indicator.md` (planned) | ⏳ | Day 33 |
| **4.5** Alert System | `4-5_Alert_System.md` (planned) | ⏳ | Day 34 |
| **4.6** Packaging | `4-6_Extension_Packaging.md` (planned) | ⏳ | Day 35 |

**Deliverables:**
- ✅ Chrome extension
- ✅ Color-coded threat UI
- ✅ Browser notifications
- ✅ Real-time threat detection

---

### 🟠 Phase 5: Integration & Testing (Days 36-42)

| Task | Status | Deadline |
|------|--------|----------|
| 5.1 End-to-End Testing | ⏳ | Day 38 |
| 5.2 Performance Testing | ⏳ | Day 40 |
| 5.3 Data Contract Validation | ⏳ | Day 41 |
| 5.4 Security & Error Handling | ⏳ | Day 42 |

---

### 🔴 Phase 6: Deployment & Monitoring (Days 43-49)

| Task | Status | Deadline |
|------|--------|----------|
| 6.1 Docker & Docker-Compose | ⏳ | Day 43 |
| 6.2 Alerting System | ⏳ | Day 45 |
| 6.3 Database Monitoring | ⏳ | Day 46 |
| 6.4 Grafana Dashboard | ⏳ | Day 47 |
| 6.5 Cloud Deployment | ⏳ | Day 48 |
| 6.6 CI/CD Pipeline | ⏳ | Day 49 |

---

### 📚 Phase 7: Documentation (Days 50-55)

| Task | Status | Deadline |
|------|--------|----------|
| 7.1 API Documentation | ⏳ | Day 50 |
| 7.2 Installation Guide | ⏳ | Day 51 |
| 7.3 Extension Installation | ⏳ | Day 52 |
| 7.4 Technical Report | ⏳ | Day 53 |
| 7.5 Demo Video | ⏳ | Day 54 |
| 7.6 GitHub Release | ⏳ | Day 55 |

---

## 🚀 How to Use These Files

### For Each Task:

1. **Open the task markdown file**
2. **Follow "What to Do" section step-by-step**
3. **Copy code from provided code blocks**
4. **Run commands as shown**
5. **Verify checklist items completed**
6. **Commit your changes to Git**
7. **Move to next task**

### Example Workflow:

```bash
# Day 1-2: Project Setup
cd projet\ 2
cat steps/1-1_Project_Initialization.md
# Follow all steps in the file
git add . && git commit -m "Initial setup"

# Day 3-8: Data Collection
cat steps/1-2_Data_Collection_and_EDA.md
# Implement and follow
git add . && git commit -m "Add data EDA"

# Continue sequentially...
```

---

## 📊 Project Timeline

```
Week 1: ║██████════════════════════════════════════ Phase 1 (Data/Setup)
Week 2: ║════██████════════════════════════════════ Phase 1 + Phase 2 (ML)
Week 3: ║════════██████████████════════════════════ Phase 2 + Phase 3 (API)
Week 4: ║════════════════██████████════════════════ Phase 3 (API) + Phase 4 (Extension)
Week 5: ║════════════════════████████████════════  Phase 4 (Extension)
Week 6: ║════════════════════════████████████████  Phase 4 + Phase 5 (Integration)
Week 7: ║════════════════════════════████████████  Phase 5 + Phase 6 (Deploy)
Week 8: ║════════════════════════════════████████  Phase 6 + Phase 7 (Docs)
```

---

## 🎯 Success Milestones

| Milestone | Target Date | Status | Files |
|-----------|-------------|--------|-------|
| **M1** Data & Model Ready | Day 25 | ⏳ | 1.1-2.5 |
| **M2** API Functional | Day 28 | ⏳ | 3.1-3.2 |
| **M3** Extension Basic | Day 34 | ⏳ | 4.1-4.4 |
| **M4** Full Integration | Day 42 | ⏳ | 5.1-5.4 |
| **M5** Deployed | Day 49 | ⏳ | 6.1-6.6 |
| **M6** Final Deliverables | Day 55 | ⏳ | 7.1-7.6 |

---

## 📋 Essential Commands Cheat Sheet

```bash
# Project Management
cd "Desktop/DS/S2/Apprentissage supervisé/projet 2"
source venv/bin/activate                    # Activate env
pip install -r requirements.txt             # Install deps

# Testing
pytest tests/ -v                            # Run all tests
pytest tests/ --cov=backend                 # With coverage
python ml_model/training/train.py           # Train model

# Running
uvicorn backend.app.main:app --reload      # Start API
docker-compose up                           # Start services
docker-compose down                         # Stop services

# Git
git add .                                   # Stage all
git commit -m "Message"                     # Commit
git log --oneline                           # View history
```

---

## 🔗 File Locations Reference

```
projet 2/
├── steps/                           ← Task files (you are here!)
│   ├── 1-1_Project_Initialization.md
│   ├── 1-2_Data_Collection_and_EDA.md
│   ├── 1-3_Feature_Engineering.md
│   ├── 1-4_Data_Quality_Tests.md
│   ├── 2-1_Model_Selection_and_Training.md
│   ├── 2-2_Class_Imbalance_SMOTE.md
│   ├── 2-3_Model_Evaluation.md
│   ├── 2-4_Explainability_SHAP.md
│   ├── 2-5_Model_Serialization.md
│   ├── 3-1_FastAPI_Setup.md
│   └── 3-2_Prediction_Endpoint.md
│
├── backend/                         ← API code
│   ├── app/
│   │   ├── main.py
│   │   ├── schemas.py
│   │   ├── models.py
│   │   └── api/
│   └── requirements.txt
│
├── ml_model/                        ← ML code
│   ├── training/
│   │   ├── train.py
│   │   ├── evaluate.py
│   │   └── models/
│   └── inference/
│       ├── model_loader.py
│       └── predictor.py
│
├── frontend/                        ← Extension code
│   ├── extension/
│   │   ├── manifest.json
│   │   ├── popup.html
│   │   └── content.js
│
├── data/                            ← Datasets
│   ├── raw/
│   ├── processed/
│   ├── train/
│   └── test/
│
├── tests/                           ← Test files
│   ├── test_data_contracts.py
│   └── test_data_quality.py
│
├── docs/                            ← Documentation
│   ├── eda_reports/
│   └── DATA_STANDARDS.md
│
├── PROJECT_PLAN.md                  ← Master plan
├── README.md
├── requirements.txt
├── docker-compose.yml
└── .gitignore
```

---

## ✅ Pre-Implementation Checklist

Before starting, ensure:

- [x] Python 3.10+ installed
- [x] Virtual environment created
- [x] Docker Desktop installed (for later phases)
- [x] Git repository initialized
- [x] Read entire PROJECT_PLAN.md
- [x] Access to threat dataset
- [x] Chrome Browser (for extension testing)

---

## 🆘 Need Help?

- **Stuck on a step?** Re-read the "What to Do" section carefully
- **Code error?** Check the checklist - you may have missed a file
- **Import error?** Ensure dependencies installed: `pip install -r requirements.txt`
- **Database error?** Ensure PostgreSQL running (Phase 3.5+)
- **Questions?** Review the code comments and docstrings

---

## 📈 Progress Tracking

Mark your progress as you complete each task:

```markdown
- [x] 1.1 Project Initialization
- [x] 1.2 Data Collection
- [ ] 1.3 Feature Engineering
- [ ] 1.4 Data Quality Tests
- [ ] 2.1 Model Training
- [ ] 2.2 SMOTE
- [ ] 2.3 Evaluation
...
```

---

**Last Updated:** 2026-03-17
**Total Tasks:** 40+
**Estimated Duration:** 8 weeks
**Status:** Ready to Start! 🚀

---

## Next Steps

→ Start with **[1-1_Project_Initialization.md](1-1_Project_Initialization.md)**

Once complete → **[1-2_Data_Collection_and_EDA.md](1-2_Data_Collection_and_EDA.md)**
