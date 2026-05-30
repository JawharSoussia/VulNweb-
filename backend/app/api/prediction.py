"""Threat Prediction Endpoint - URL-based"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from typing import List, Optional
import numpy as np
import logging
from datetime import datetime
from backend.app.feature_extractor import URLFeatureExtractor

logger = logging.getLogger(__name__)

router = APIRouter()
feature_extractor = URLFeatureExtractor()


# ============================================================================
# SCHEMAS (Request/Response Models)
# ============================================================================

class PredictionRequest(BaseModel):
    """Input schema for URL threat prediction"""

    url: str = Field(..., description="Target URL to analyze", example="https://example.com/page")

    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://suspicious-site.com/download/?file=malware.exe"
            }
        }


class PredictionResponse(BaseModel):
    """Output schema for prediction response"""

    threat_score: float = Field(..., ge=0, le=100, description="Threat score 0-100")
    threat_level: str = Field(..., description="Threat level: safe, suspicious, critical")
    confidence: float = Field(..., ge=0, le=1, description="Model confidence 0-1")
    predicted_class: int = Field(..., description="0=Safe, 1=Threat Level 1, 2=Threat Level 2")
    probabilities: dict = Field(..., description="Class probabilities")
    explanation: List[str] = Field(..., max_length=3, description="Top 3 reasons for prediction")
    model_version: str = Field(..., description="Model version used")
    request_id: str = Field(..., description="Unique request identifier")
    timestamp: str = Field(..., description="Prediction timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "threat_score": 85.0,
                "threat_level": "critical",
                "confidence": 0.95,
                "predicted_class": 2,
                "probabilities": {
                    "safe": 0.02,
                    "threat_level_1": 0.03,
                    "threat_level_2": 0.95
                },
                "explanation": [
                    "num_colons: 5 (highly suspicious)",
                    "url_length: 92 (longer than average)",
                    "special_char_ratio: 0.18 (elevated)"
                ],
                "model_version": "XGBoost v1.0",
                "request_id": "req_1234567890",
                "timestamp": "2026-03-30T14:30:00Z"
            }
        }


# ============================================================================
# PREDICTION ENDPOINT
# ============================================================================

@router.post(
    "/predict",
    response_model=PredictionResponse,
    summary="Predict URL threat level",
    description="Analyze URL and predict threat level using ML model"
)
async def predict(request_data: PredictionRequest, request: Request) -> PredictionResponse:
    """
    Predict threat level for given URL

    **Parameters:**
    - url: Target URL to analyze

    **Returns:**
    - threat_score: 0-100 threat rating
    - threat_level: safe/suspicious/critical
    - confidence: Model confidence (0-1)
    - predicted_class: 0 (Safe), 1 (Threat Level 1), 2 (Threat Level 2)
    - probabilities: Class probabilities
    - explanation: Top 3 decision factors
    - model_version: Model used
    - request_id: Unique identifier
    - timestamp: Prediction time
    """

    request_id = f"req_{datetime.now().timestamp():.0f}"

    try:
        logger.info(f"[{request_id}] URL prediction request: {request_data.url[:80]}")

        # ====================================================================
        # 1. GET MODEL
        # ====================================================================

        model_package = request.app.state.model_package

        if model_package is None:
            logger.error(f"[{request_id}] Model not loaded")
            raise HTTPException(
                status_code=503,
                detail="Model not available - service temporarily unavailable"
            )

        # ====================================================================
        # 2. EXTRACT FEATURES
        # ====================================================================

        try:
            X = feature_extractor.extract(request_data.url)
            logger.info(f"[{request_id}] Features extracted: shape {X.shape}")
        except Exception as e:
            logger.error(f"[{request_id}] Feature extraction failed: {e}")
            raise HTTPException(
                status_code=400,
                detail=f"Invalid URL for feature extraction: {str(e)}"
            )

        # ====================================================================
        # 3. EXTRACT NEW THREAT FEATURES
        # ====================================================================

        # Extract the new threat detection features (last 3 features)
        # These are: is_shortener_url, has_executable_extension, has_redirect_parameter
        new_threat_features = {
            'is_shortener_url': X[0, -3],
            'has_executable_extension': X[0, -2],
            'has_redirect_parameter': X[0, -1]
        }

        # Use only the first 37 features for the model (backward compatibility)
        X_model = X[:, :37]

        # ====================================================================
        # 4. MAKE PREDICTION
        # ====================================================================

        prediction = model_package.predict(X_model)

        threat_score = prediction['threat_score']
        confidence = prediction['confidence']
        threat_level = prediction['threat_level']
        predicted_class = prediction['prediction']
        probabilities = prediction['probabilities']

        # ====================================================================
        # 5. APPLY THREAT FEATURE BOOSTING
        # ====================================================================

        threat_boost = 0
        threat_indicators = []

        # Check for URL shortener (high confidence signal)
        if new_threat_features['is_shortener_url'] > 0.5:
            threat_boost += 25
            threat_indicators.append("URL shortened (bit.ly, tinyurl, etc.)")

        # Check for executable file extensions
        if new_threat_features['has_executable_extension'] > 0.5:
            threat_boost += 30
            threat_indicators.append("Executable file download detected (.exe, .dll, etc.)")

        # Check for redirect parameters
        if new_threat_features['has_redirect_parameter'] > 0.5:
            threat_boost += 20
            threat_indicators.append("Redirect parameter detected in URL")

        # Apply threat boost to score
        if threat_boost > 0:
            threat_score = min(100, threat_score + threat_boost)
            # Update threat level if boosted above thresholds
            if threat_score >= 67 and predicted_class < 2:
                threat_level = "critical"
                predicted_class = 2
                probabilities['threat_level_2'] = max(probabilities.get('threat_level_2', 0), 0.8)
                probabilities['safe'] = min(probabilities.get('safe', 0), 0.1)
                probabilities['threat_level_1'] = 1 - probabilities['safe'] - probabilities.get('threat_level_2', 0)
            elif threat_score >= 34 and predicted_class < 1:
                threat_level = "suspicious"
                predicted_class = 1
                probabilities['threat_level_1'] = max(probabilities.get('threat_level_1', 0), 0.6)
                probabilities['safe'] = min(probabilities.get('safe', 0), 0.3)
                probabilities['threat_level_2'] = 1 - probabilities['safe'] - probabilities.get('threat_level_1', 0)

            logger.info(f"[{request_id}] Threat boost applied: +{threat_boost} → score={threat_score:.1f}")

        logger.info(
            f"[{request_id}] Prediction: {threat_level} "
            f"(score={threat_score:.1f}, class={predicted_class}, confidence={confidence:.3f})"
        )

        # ====================================================================
        # 4. GET EXPLANATIONS
        # ====================================================================

        explanation_list = []
        try:
            # Get SHAP explanations if available
            if model_package.explainer is not None:
                explanations = model_package.explain(X_model, k=3)
                if explanations and len(explanations) > 0:
                    explanation_list = explanations[0]
        except Exception as e:
            logger.warning(f"[{request_id}] SHAP explanations unavailable: {e}")

        # Add threat indicators from new features to explanations
        if threat_indicators and len(explanation_list) < 3:
            explanation_list.extend(threat_indicators)

        # Fallback explanations based on threat level
        if not explanation_list:
            if threat_level == "critical":
                explanation_list = [
                    "High threat indicators detected in URL structure",
                    "Suspicious character patterns identified",
                    "Domain characteristics suggest malicious intent"
                ]
            elif threat_level == "suspicious":
                explanation_list = [
                    "Several mild threat indicators detected",
                    "URL structure shows atypical patterns",
                    "Further investigation recommended"
                ]
            else:
                explanation_list = [
                    "URL appears to be legitimate",
                    "Normal domain structure observed",
                    "Low threat indicators detected"
                ]

        logger.info(f"[{request_id}] Explanations: {explanation_list}")

        # ====================================================================
        # 5. BUILD RESPONSE
        # ====================================================================

        response = PredictionResponse(
            threat_score=threat_score,
            threat_level=threat_level,
            confidence=confidence,
            predicted_class=predicted_class,
            probabilities=probabilities,
            explanation=explanation_list[:3],
            model_version=model_package.metadata.get('model_name', 'XGBoost v1.0'),
            request_id=request_id,
            timestamp=datetime.utcnow().isoformat() + "Z"
        )

        logger.info(f"[{request_id}] Response sent successfully")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Prediction error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Prediction failed"
        )


# ============================================================================
# BATCH PREDICTION ENDPOINT
# ============================================================================

class BatchPredictionRequest(BaseModel):
    """Batch prediction request"""
    urls: List[str] = Field(..., max_length=100, description="Up to 100 URLs")


class BatchPredictionResponse(BaseModel):
    """Batch predictions response"""
    results: List[PredictionResponse]
    batch_id: str
    total: int
    successful: int
    failed: int


@router.post(
    "/predict-batch",
    response_model=BatchPredictionResponse,
    summary="Batch URL threat predictions"
)
async def predict_batch(batch_request: BatchPredictionRequest, request: Request) -> BatchPredictionResponse:
    """
    Predict threats for multiple URLs

    **Parameters:**
    - urls: List of up to 100 URLs to analyze

    **Returns:**
    - Batch ID for tracking
    - Individual predictions for each URL
    - Success/failure statistics
    """

    batch_id = f"batch_{datetime.now().timestamp():.0f}"
    results = []
    failed = 0

    logger.info(f"[{batch_id}] Batch prediction: {len(batch_request.urls)} URLs")

    for idx, url in enumerate(batch_request.urls):
        try:
            pred_response = await predict(PredictionRequest(url=url), request)
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


# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================

@router.get(
    "/model-info",
    summary="Get model information",
    description="Returns metadata about loaded ML model"
)
async def get_model_info(request: Request):
    """Get model metadata and capabilities"""

    model_package = request.app.state.model_package

    if model_package is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    return {
        "model_name": model_package.metadata.get('model_name', 'Unknown'),
        "model_version": model_package.metadata.get('trained_at', 'Unknown'),
        "num_classes": model_package.num_classes,
        "class_names": ["Safe", "Threat Level 1", "Threat Level 2"],
        "num_features": len(model_package.feature_names),
        "feature_names": model_package.feature_names,
        "performance": model_package.metadata.get('cv_results', {})
    }


@router.get("/features")
async def get_features(request: Request):
    """Get list of features expected by the model"""

    model_package = request.app.state.model_package

    if model_package is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    return {
        "feature_count": len(model_package.feature_names),
        "features": model_package.feature_names,
        "description": "These are the URL features extracted for ML prediction"
    }


# ============================================================================
# RAW FEATURE PREDICTION ENDPOINT (For Chrome Extension)
# ============================================================================

class RawPredictionRequest(BaseModel):
    """Raw feature prediction request (bypasses feature extraction)"""
    features: List[float] = Field(..., description="34 pre-extracted features")


@router.post(
    "/predict-raw",
    response_model=PredictionResponse,
    summary="Predict from raw features",
    description="Make prediction from pre-extracted features (used by Chrome extension)"
)
async def predict_raw(request_data: RawPredictionRequest, request: Request) -> PredictionResponse:
    """
    Predict threat level from raw feature vector

    This endpoint is used by the Chrome extension which pre-computes features.
    It skips feature extraction and goes directly to model prediction.

    **Parameters:**
    - features: List of 34 float values (URL features)

    **Returns:**
    - Same as /api/predict endpoint
    """

    request_id = f"req_raw_{datetime.now().timestamp():.0f}"

    try:
        logger.info(f"[{request_id}] Raw feature prediction request")

        # Get model
        model_package = request.app.state.model_package
        if model_package is None:
            logger.error(f"[{request_id}] Model not loaded")
            raise HTTPException(
                status_code=503,
                detail="Model not available - service temporarily unavailable"
            )

        # Validate feature vector
        if len(request_data.features) != 34:
            raise HTTPException(
                status_code=400,
                detail=f"Expected 34 features, got {len(request_data.features)}"
            )

        # Convert to numpy array
        X = np.array(request_data.features).reshape(1, -1)

        # Make prediction
        prediction = model_package.predict(X)

        threat_score = prediction['threat_score']
        confidence = prediction['confidence']
        threat_level = prediction['threat_level']
        predicted_class = prediction['prediction']
        probabilities = prediction['probabilities']

        logger.info(
            f"[{request_id}] Raw prediction: {threat_level} "
            f"(score={threat_score:.1f}, class={predicted_class}, confidence={confidence:.3f})"
        )

        # Get explanations
        explanation_list = []
        try:
            if model_package.explainer is not None:
                explanations = model_package.explain(X, k=3)
                if explanations and len(explanations) > 0:
                    explanation_list = explanations[0]
        except Exception as e:
            logger.warning(f"[{request_id}] SHAP explanations unavailable: {e}")

        # Fallback explanations
        if not explanation_list:
            if threat_level == "critical":
                explanation_list = [
                    "High threat indicators detected in URL features",
                    "Suspicious pattern combination identified",
                    "Domain characteristics suggest malicious intent"
                ]
            elif threat_level == "suspicious":
                explanation_list = [
                    "Several mild threat indicators detected",
                    "Feature patterns show atypical characteristics",
                    "Further investigation recommended"
                ]
            else:
                explanation_list = [
                    "URL features appear to be legitimate",
                    "Normal feature distribution observed",
                    "Low threat indicators detected"
                ]

        # Build response
        response = PredictionResponse(
            threat_score=threat_score,
            threat_level=threat_level,
            confidence=confidence,
            predicted_class=predicted_class,
            probabilities=probabilities,
            explanation=explanation_list[:3],
            model_version=model_package.metadata.get('model_name', 'XGBoost v1.0'),
            request_id=request_id,
            timestamp=datetime.utcnow().isoformat() + "Z"
        )

        logger.info(f"[{request_id}] Raw prediction response sent successfully")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Raw prediction error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Prediction failed"
        )
