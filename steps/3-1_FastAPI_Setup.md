# Task 3.1: FastAPI Setup & Project Structure

**Phase:** Backend API Development
**Deadline:** Day 20
**Status:** ⏳ Pending
**Dependencies:** Task 2.5 complete

---

## 📋 Objective
Set up FastAPI application with proper structure, CORS configuration, logging, and error handling.

---

## 🎯 What to Do

### Step 1: Update Backend Main Application

**Update: `backend/app/main.py`**

```python
"""FastAPI Application Setup"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from typing import Optional
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage app startup and shutdown"""
    # Startup
    logger.info("🚀 VulNweb API starting up...")
    logger.info("Loading ML model package...")

    # Load model on startup
    try:
        from ml_model.inference import ModelPackage
        global model_package
        model_package = ModelPackage()
        model_package.load_all()
        logger.info("✓ ML model loaded successfully")
        app.state.model_package = model_package
    except Exception as e:
        logger.error(f"❌ Failed to load model: {e}")
        app.state.model_package = None

    yield

    # Shutdown
    logger.info("🛑 VulNweb API shutting down...")


# Create FastAPI app
app = FastAPI(
    title="VulNweb Threat Detection API",
    description="Real-time cyber threat surveillance system with ML-powered threat prediction",
    version="0.1.0",
    lifespan=lifespan
)


# ============================================================================
# MIDDLEWARE CONFIGURATION
# ============================================================================

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",      # Local dev
        "http://localhost:8080",      # Alt port
        "chrome-extension://*",        # Chrome extension
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests"""
    logger.info(f"{request.method} {request.url.path}")

    try:
        response = await call_next(request)
        logger.info(f"  → {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"  → Error: {e}")
        raise


# ============================================================================
# EXCEPTION HANDLERS
# ============================================================================

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


# ============================================================================
# ROUTES
# ============================================================================

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "service": "VulNweb Threat Detection API",
        "version": "0.1.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    model_loaded = app.state.model_package is not None

    return {
        "status": "healthy" if model_loaded else "degraded",
        "model_loaded": model_loaded,
        "version": "0.1.0"
    }


@app.get("/docs")
async def docs():
    """API documentation"""
    return {
        "documentation": "See /docs for interactive Swagger UI",
        "endpoints": {
            "GET /": "Root endpoint",
            "GET /health": "Health check",
            "POST /predict": "Make threat prediction",
            "POST /feedback": "Send user feedback",
            "GET /model-info": "Model information"
        }
    }


@app.get("/model-info")
async def model_info():
    """Get model information"""
    if app.state.model_package is None:
        return {"error": "Model not loaded"}

    metadata = app.state.model_package.metadata or {}

    return {
        "model_name": metadata.get('model_name', 'unknown'),
        "version": metadata.get('trained_at', 'unknown'),
        "features": len(app.state.model_package.feature_names),
        "feature_names": app.state.model_package.feature_names[:10]  # Show first 10
    }


# Import route modules (will be created in next step)
from .api import prediction, feedback, health

app.include_router(prediction.router, prefix="/api", tags=["Prediction"])
app.include_router(feedback.router, prefix="/api", tags=["Feedback"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=True
    )
```

---

### Step 2: Create API Route Structure

```bash
# Create API package
mkdir -p backend/app/api
touch backend/app/api/__init__.py

# Create route modules
touch backend/app/api/prediction.py
touch backend/app/api/feedback.py
touch backend/app/api/health.py
```

**Create: `backend/app/api/__init__.py`**

```python
"""API Routes Package"""
```

**Create: `backend/app/api/health.py`**

```python
"""Health Check Routes"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/status")
async def status():
    """API status endpoint"""
    return {"status": "operational"}
```

---

### Step 3: Create Configuration Module

**Create: `backend/app/config.py`**

```python
"""Application Configuration"""
from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    """Application settings"""

    # App
    app_name: str = "VulNweb"
    app_version: str = "0.1.0"
    debug: bool = True

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Database (will add in Phase 3.5)
    database_url: str = "postgresql://user:password@localhost:5432/vulnweb"
    db_echo: bool = False

    # Model
    model_path: str = "ml_model/inference/models/xgboost_smote_model.pkl"
    preprocessor_path: str = "ml_model/training/preprocessor.pkl"

    # API
    api_timeout: int = 30
    max_batch_size: int = 100

    # Logging
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False


# Load settings
settings = Settings()
```

---

### Step 4: Create Environment Configuration

**Create: `.env` (for local development)**

```bash
cat > .env << 'EOF'
APP_NAME=VulNweb
APP_VERSION=0.1.0
DEBUG=true

HOST=0.0.0.0
PORT=8000

DATABASE_URL=postgresql://vulnweb:password123@localhost:5432/vulnweb_db
DB_ECHO=false

MODEL_PATH=ml_model/inference/models/xgboost_smote_model.pkl
PREPROCESSOR_PATH=ml_model/training/preprocessor.pkl

API_TIMEOUT=30
MAX_BATCH_SIZE=100

LOG_LEVEL=info
EOF

# Add to .gitignore
echo ".env" >> .gitignore
```

---

### Step 5: Create Logging Configuration

**Create: `backend/app/logging_config.py`**

```python
"""Logging Configuration"""
import logging
import sys
from pathlib import Path

# Create logs directory
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Get logger
logger = logging.getLogger(__name__)
logger.info("Logging configured")
```

---

### Step 6: Verify Setup

```bash
# Activate virtual environment
source venv/bin/activate

# Install any missing dependencies
pip install -r requirements.txt

# Test import
python -c "from backend.app.main import app; print('✓ FastAPI app imports successfully')"

# Start dev server
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

---

### Step 7: Test Endpoints

```bash
# In another terminal
curl http://localhost:8000/health
curl http://localhost:8000/api/status
```

---

## 📊 Expected Directory Structure

```
backend/app/
├── __init__.py
├── main.py
├── config.py
├── logging_config.py
├── models.py
├── schemas.py
├── data_contracts.py
├── middleware.py
└── api/
    ├── __init__.py
    ├── health.py
    ├── prediction.py
    └── feedback.py
```

---

## ✅ Checklist

- [ ] FastAPI main app created with lifespan management
- [ ] CORS middleware configured
- [ ] Request logging middleware implemented
- [ ] Exception handlers added
- [ ] Configuration module created
- [ ] Environment file (.env) created
- [ ] API routes structure created
- [ ] Logging configured
- [ ] Dev server starts without errors
- [ ] Health endpoints responding
- [ ] Commit: `git add . && git commit -m "Add FastAPI setup and configuration"`

---

## 🔗 Next Steps

✅ **Task 3.1 Complete** → Move to **Task 3.2: Prediction Endpoint**

---

**Created:** 2026-03-17
