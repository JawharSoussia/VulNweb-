"""Feedback Routes"""
from fastapi import APIRouter
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class FeedbackRequest(BaseModel):
    """Feedback request schema"""
    prediction_id: str
    actual_label: int
    comments: str = ""


@router.post("/feedback")
async def submit_feedback(feedback: FeedbackRequest):
    """Submit feedback on a prediction"""
    logger.info(f"Received feedback for prediction {feedback.prediction_id}: "
                f"actual_label={feedback.actual_label}")

    return {
        "message": "Feedback received",
        "prediction_id": feedback.prediction_id
    }
