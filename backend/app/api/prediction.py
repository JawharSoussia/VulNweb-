"""Prediction Routes"""
from fastapi import APIRouter, Request
from pydantic import BaseModel
import numpy as np
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class PredictionRequest(BaseModel):
    """Prediction request schema"""
    features: list[float]


class PredictionResponse(BaseModel):
    """Prediction response schema"""
    prediction: int
    threat_score: float
    threat_level: str
    confidence: float


@router.post("/predict", response_model=PredictionResponse)
async def predict(request: Request, pred_request: PredictionRequest):
    """Make a threat prediction"""
    if request.app.state.model_package is None:
        return {"error": "Model not loaded"}

    try:
        # Convert features to numpy array
        X = np.array(pred_request.features).reshape(1, -1)

        # Make prediction
        result = request.app.state.model_package.predict(X)

        return result
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return {"error": str(e)}
