"""FastAPI Application Setup"""
from contextlib import asynccontextmanager
import logging
from pathlib import Path
import sys

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

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
    logger.info("VulNweb API starting up...")
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
        logger.error(f" Failed to load model: {e}")
        app.state.model_package = None

    yield

    # Shutdown
    logger.info(" VulNweb API shutting down...")


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


@app.get("/api/endpoints")
async def endpoints():
    """List the frozen API contract"""
    return {
        "namespace": "/api",
        "endpoints": {
            "POST /api/predict": "Predict URL threat level",
            "POST /api/predict-raw": "Predict threat from raw feature vector",
            "POST /api/predict-batch": "Predict threats for a batch of URLs",
            "GET /api/features": "List model feature names",
            "GET /api/model-info": "Get loaded model metadata",
            "POST /api/feedback": "Submit prediction feedback",
            "GET /api/status": "API status route"
        },
        "documentation": "See /docs for interactive Swagger UI"
    }


# Import route modules
from .api import feedback, health, prediction

app.include_router(feedback.router, prefix="/api", tags=["Feedback"])
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(prediction.router, prefix="/api", tags=["Prediction"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=True
    )