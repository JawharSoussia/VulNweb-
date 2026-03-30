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
app.include_router(health.router, prefix="/api", tags=["Health"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=True
    )