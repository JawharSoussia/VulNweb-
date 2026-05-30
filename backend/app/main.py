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


# Import route modules
from .api import prediction, feedback, health
from .feature_extractor import URLFeatureExtractor
from .api.prediction import PredictionRequest, PredictionResponse
from fastapi import HTTPException
from datetime import datetime
import logging

extractor = URLFeatureExtractor()
logger = logging.getLogger(__name__)

# Override predict endpoint with threat boost
@app.post("/api/predict", response_model=PredictionResponse)
async def predict_with_boost(request_data: PredictionRequest, request: Request) -> PredictionResponse:
    """Predict threat level with enhanced threat feature boost"""
    request_id = f"req_{datetime.now().timestamp():.0f}"

    try:
        logger.info(f"[{request_id}] Prediction with boost: {request_data.url[:80]}")

        # Get model
        model_package = request.app.state.model_package
        if model_package is None:
            raise HTTPException(status_code=503, detail="Model not available")

        # Extract features
        X = extractor.extract(request_data.url)

        # Extract threat features
        new_threat_features = {
            'is_shortener_url': X[0, -3],
            'has_executable_extension': X[0, -2],
            'has_redirect_parameter': X[0, -1]
        }

        # Use only first 37 features for model
        X_model = X[:, :37]
        prediction = model_package.predict(X_model)

        threat_score = prediction['threat_score']
        confidence = prediction['confidence']
        threat_level = prediction['threat_level']
        predicted_class = prediction['prediction']
        probabilities = prediction['probabilities']

        # Apply threat boost
        threat_boost = 0
        threat_indicators = []

        if new_threat_features['is_shortener_url'] > 0.5:
            threat_boost += 25
            threat_indicators.append("URL shortened (bit.ly, tinyurl, etc.)")

        if new_threat_features['has_executable_extension'] > 0.5:
            threat_boost += 30
            threat_indicators.append("Executable file download detected (.exe, .dll, etc.)")

        if new_threat_features['has_redirect_parameter'] > 0.5:
            threat_boost += 20
            threat_indicators.append("Redirect parameter detected in URL")

        if threat_boost > 0:
            threat_score = min(100, threat_score + threat_boost)
            if threat_score >= 67 and predicted_class < 2:
                threat_level = "critical"
                predicted_class = 2
            elif threat_score >= 34 and predicted_class < 1:
                threat_level = "suspicious"
                predicted_class = 1
            logger.info(f"[{request_id}] Boost: +{threat_boost} -> {threat_score:.0f}")

        # Build response
        response = PredictionResponse(
            threat_score=threat_score,
            threat_level=threat_level,
            confidence=confidence,
            predicted_class=predicted_class,
            probabilities=probabilities,
            explanation=threat_indicators[:3],
            model_version=model_package.metadata.get('model_name', 'XGBoost v1.0'),
            request_id=request_id,
            timestamp=datetime.utcnow().isoformat() + "Z"
        )

        logger.info(f"[{request_id}] Response: {threat_level} ({threat_score:.0f})")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Prediction failed")

# Batch prediction endpoint (uses the predict_with_boost function above)
from typing import List
from pydantic import BaseModel, Field

class BatchPredictionRequest(BaseModel):
    urls: List[str] = Field(..., max_length=100)

class BatchPredictionResponse(BaseModel):
    results: List[PredictionResponse]
    batch_id: str
    total: int
    successful: int
    failed: int

@app.post("/api/predict-batch", response_model=BatchPredictionResponse)
async def predict_batch_with_boost(batch_request: BatchPredictionRequest, request: Request) -> BatchPredictionResponse:
    """Batch predictions with threat boost"""
    batch_id = f"batch_{datetime.now().timestamp():.0f}"
    results = []
    failed = 0

    for idx, url in enumerate(batch_request.urls):
        try:
            pred_response = await predict_with_boost(PredictionRequest(url=url), request)
            results.append(pred_response)
        except Exception as e:
            logger.error(f"[{batch_id}] URL {idx} failed: {e}")
            failed += 1

    return BatchPredictionResponse(
        results=results,
        batch_id=batch_id,
        total=len(batch_request.urls),
        successful=len(results),
        failed=failed
    )

# Include other routers (prediction handled directly above)
# app.include_router(prediction.router, prefix="/api", tags=["Prediction"], include_in_schema=False)
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