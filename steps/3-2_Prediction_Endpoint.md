# Task 3.2: Prediction Endpoint Implementation

**Phase:** Backend API Development
**Deadline:** Day 23
**Status:** ⏳ Pending
**Dependencies:** Task 3.1 complete

---

## 📋 Objective
Implement POST `/predict` endpoint for real-time threat prediction with validation, ML inference, and explanations.

---

## 🎯 What to Do

### Step 1: Create Prediction Route

**Create: `backend/app/api/prediction.py`**

```python
"""Threat Prediction Endpoint"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
import numpy as np
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# SCHEMAS (Request/Response Models)
# ============================================================================

class PredictionRequest(BaseModel):
    """Input schema for prediction request"""

    url: str = Field(..., description="Target URL")
    ip_address: str = Field(
        ...,
        pattern=r"^(\d{1,3}\.){3}\d{1,3}$",
        description="IPv4 address"
    )
    port: Optional[int] = Field(None, ge=0, le=65535, description="Port number")
    protocol: Optional[str] = Field(None, description="tcp or udp")
    bytes_in: Optional[float] = Field(None, ge=0, description="Bytes received")
    bytes_out: Optional[float] = Field(None, ge=0, description="Bytes sent")
    duration: Optional[float] = Field(None, ge=0, description="Connection duration")
    packets: Optional[int] = Field(None, ge=0, description="Number of packets")

    @field_validator('url')
    @classmethod
    def validate_url(cls, v):
        """Validate URL format"""
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://example.com/page",
                "ip_address": "192.168.1.1",
                "port": 443,
                "protocol": "tcp",
                "bytes_in": 1024,
                "bytes_out": 512,
                "duration": 2.5,
                "packets": 50
            }
        }


class ExplanationItem(BaseModel):
    """Single explanation reason"""

    reason: str = Field(..., description="Feature name and impact")
    importance: float = Field(..., ge=0, description="Importance score")


class PredictionResponse(BaseModel):
    """Output schema for prediction response"""

    threat_score: float = Field(..., ge=0, le=100, description="Threat score 0-100")
    threat_level: str = Field(
        ...,
        description="Threat level: safe, suspicious, critical"
    )
    confidence: float = Field(..., ge=0, le=1, description="Confidence 0-1")
    explanation: List[str] = Field(
        ...,
        max_length=3,
        description="Top 3 reasons for prediction"
    )
    model_version: str = Field(..., description="Model version used")
    request_id: str = Field(..., description="Unique request identifier")
    timestamp: str = Field(..., description="Prediction timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "threat_score": 85.5,
                "threat_level": "critical",
                "confidence": 0.92,
                "explanation": [
                    "IP: Known malware C2 server",
                    "Domain: Suspicious entropy 6.8",
                    "Protocol: Unusual port 8883"
                ],
                "model_version": "v1.0",
                "request_id": "req_123abc",
                "timestamp": "2026-03-17T12:34:56Z"
            }
        }


# ============================================================================
# PREDICTION ENDPOINT
# ============================================================================

@router.post(
    "/predict",
    response_model=PredictionResponse,
    summary="Predict threat level",
    description="Analyze URL/IP and predict threat level with explainability"
)
async def predict(request_data: PredictionRequest, request: Request) -> PredictionResponse:
    """
    Predict threat level for given URL/IP

    **Parameters:**
    - url: Target URL to analyze
    - ip_address: Source or target IP address
    - port: Connection port (optional)
    - protocol: tcp or udp (optional)
    - bytes_in/out: Byte counts (optional)
    - duration: Connection duration (optional)
    - packets: Packet count (optional)

    **Returns:**
    - threat_score: 0-100 scale
    - threat_level: safe/suspicious/critical
    - confidence: 0-1 probability
    - explanation: Top 3 decision reasons
    - model_version: Model used
    - request_id: Unique identifier
    - timestamp: Prediction time

    **Example:**
    ```
    POST /api/predict
    {
      "url": "https://example.com",
      "ip_address": "192.168.1.1",
      "port": 443
    }
    ```
    """

    request_id = f"req_{datetime.now().timestamp():.0f}"

    try:
        logger.info(f"[{request_id}] Prediction request: {request_data.url}")

        # ====================================================================
        # 1. VALIDATE INPUT
        # ====================================================================

        # Model package from app state
        model_package = request.app.state.model_package

        if model_package is None:
            logger.error(f"[{request_id}] Model not loaded")
            raise HTTPException(
                status_code=503,
                detail="Model not available - service temporarily unavailable"
            )

        # ====================================================================
        # 2. PREPARE FEATURES
        # ====================================================================

        # Build feature array matching training features
        feature_dict = {
            'url_length': len(request_data.url),
            'port': request_data.port or 0,
            'bytes_in': request_data.bytes_in or 0,
            'bytes_out': request_data.bytes_out or 0,
            'duration': request_data.duration or 0,
            'packets': request_data.packets or 0,
        }

        # Create feature vector in correct order
        X = np.array([
            feature_dict.get(fname, 0)
            for fname in model_package.feature_names
        ]).reshape(1, -1)

        logger.info(f"[{request_id}] Features prepared, shape: {X.shape}")

        # ====================================================================
        # 3. MAKE PREDICTION
        # ====================================================================

        prediction = model_package.predict(X)

        threat_score = prediction['threat_score']
        confidence = prediction['confidence']
        threat_level = prediction['threat_level']

        logger.info(f"[{request_id}] Prediction: {threat_level} ({threat_score:.1f}%)")

        # ====================================================================
        # 4. GET EXPLANATIONS
        # ====================================================================

        explanation_list = []
        try:
            explanations = model_package.explain(X, k=3)
            if explanations:
                explanation_list = explanations[0]
                logger.info(f"[{request_id}] Explanations: {len(explanation_list)} items")
        except Exception as e:
            logger.warning(f"[{request_id}] Could not generate explanations: {e}")

        # ====================================================================
        # 5. BUILD RESPONSE
        # ====================================================================

        response = PredictionResponse(
            threat_score=threat_score,
            threat_level=threat_level,
            confidence=confidence,
            explanation=explanation_list if explanation_list else [
                "Analysis complete",
                "Check threat score for details",
                "Request logged for monitoring"
            ],
            model_version=model_package.metadata.get('model_name', 'v1.0'),
            request_id=request_id,
            timestamp=datetime.utcnow().isoformat() + "Z"
        )

        logger.info(f"[{request_id}] Response sent successfully")

        # ====================================================================
        # 6. LOG PREDICTION (for feedback loop & monitoring)
        # ====================================================================

        # TODO: Store in database (Task 3.5)
        log_entry = {
            'request_id': request_id,
            'url': request_data.url,
            'ip_address': request_data.ip_address,
            'threat_score': threat_score,
            'threat_level': threat_level,
            'timestamp': datetime.utcnow().isoformat()
        }
        logger.info(f"[{request_id}] Logged: {log_entry}")

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
# BATCH PREDICTION ENDPOINT (Optional)
# ============================================================================

class BatchPredictionRequest(BaseModel):
    """Batch prediction requests"""

    requests: List[PredictionRequest] = Field(
        ...,
        max_length=100,
        description="Up to 100 prediction requests"
    )


class BatchPredictionResponse(BaseModel):
    """Batch predictions response"""

    results: List[PredictionResponse]
    batch_id: str
    total: int
    success: int
    failed: int


@router.post(
    "/predict-batch",
    response_model=BatchPredictionResponse,
    summary="Batch threat predictions"
)
async def predict_batch(batch_request: BatchPredictionRequest, request: Request) -> \
        BatchPredictionResponse:
    """
    Predict threats for multiple URLs/IPs in single request

    **Parameters:**
    - requests: List of prediction requests (max 100)

    **Returns:**
    - Batch ID for tracking
    - Individual predictions for each request
    - Success/failure counts
    """

    batch_id = f"batch_{datetime.now().timestamp():.0f}"
    results = []
    failed = 0

    logger.info(f"[{batch_id}] Batch prediction: {len(batch_request.requests)} items")

    for idx, pred_req in enumerate(batch_request.requests):
        try:
            response = await predict(pred_req, request)
            results.append(response)
        except Exception as e:
            logger.error(f"[{batch_id}] Item {idx} failed: {e}")
            failed += 1

    return BatchPredictionResponse(
        results=results,
        batch_id=batch_id,
        total=len(batch_request.requests),
        success=len(results),
        failed=failed
    )


# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================

@router.get(
    "/features",
    summary="Get expected features",
    description="Returns list of feature names expected by the model"
)
async def get_features(request: Request):
    """Get list of features the model expects"""

    model_package = request.app.state.model_package

    if model_package is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    return {
        "feature_count": len(model_package.feature_names),
        "features": model_package.feature_names,
        "description": "Use these feature names when sending predictions"
    }
```

---

### Step 2: Create Feedback Route

**Create: `backend/app/api/feedback.py`**

```python
"""User Feedback Endpoint"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class FeedbackRequest(BaseModel):
    """User feedback schema"""

    request_id: str = Field(..., description="Original prediction request ID")
    is_correct: bool = Field(
        ...,
        description="Was the prediction correct?"
    )
    comments: str = Field(
        None,
        max_length=500,
        description="Optional feedback comments"
    )


class FeedbackResponse(BaseModel):
    """Feedback confirmation response"""

    status: str
    feedback_id: str
    message: str


@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(feedback: FeedbackRequest) -> FeedbackResponse:
    """
    Submit user feedback about prediction accuracy

    **Parameters:**
    - request_id: ID from original prediction
    - is_correct: Whether prediction was correct
    - comments: Optional feedback comments

    **Returns:**
    - Confirmation that feedback was received
    - Feedback ID for tracking

    **Purpose:**
    Collects data to improve model performance through:
    - False positive identification
    - False negative identification
    - User corrections
    """

    feedback_id = f"feedback_{datetime.now().timestamp():.0f}"

    try:
        logger.info(f"[{feedback_id}] Received feedback: {feedback.request_id}")
        logger.info(f"  Correct: {feedback.is_correct}")
        if feedback.comments:
            logger.info(f"  Comments: {feedback.comments}")

        # TODO: Store in database (Task 3.5)
        # This will be used for model retraining

        return FeedbackResponse(
            status="accepted",
            feedback_id=feedback_id,
            message="Thank you for your feedback! This helps us improve."
        )

    except Exception as e:
        logger.error(f"[{feedback_id}] Feedback error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to process feedback"
        )
```

---

### Step 3: Test Prediction Endpoint

```bash
# Start server
uvicorn backend.app.main:app --reload

# In another terminal, test with curl
curl -X POST "http://localhost:8000/api/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://suspicious-domain.com",
    "ip_address": "192.51.100.1",
    "port": 443,
    "protocol": "tcp",
    "bytes_in": 5000,
    "bytes_out": 2000,
    "duration": 3.5,
    "packets": 75
  }'

# Test features endpoint
curl "http://localhost:8000/api/features"

# Test feedback endpoint
curl -X POST "http://localhost:8000/api/feedback" \
  -H "Content-Type: application/json" \
  -d '{
    "request_id": "req_123",
    "is_correct": true,
    "comments": "Good prediction!"
  }'
```

---

## ✅ Checklist

- [x] Prediction request schema created with validation
- [x] Prediction response schema with all fields
- [x] POST /predict endpoint implemented
- [x] Input validation working
- [x] Model inference integrated
- [x] Explanations included in response
- [x] Request logging implemented
- [x] Batch endpoint created (optional)
- [x] Feedback endpoint implemented
- [x] Features endpoint created
- [x] All endpoints tested with curl
- [x] Error handling implemented
- [x] Commit: `git add . && git commit -m "Add prediction and feedback endpoints"`

---

## 🔗 Next Steps

✅ **Task 3.2 Complete** → Move to **Task 3.3: Feedback Loop Endpoint** (or 3.5: Database Setup)

---

**Created:** 2026-03-17
