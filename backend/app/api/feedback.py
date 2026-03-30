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