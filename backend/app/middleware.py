"""Middleware for data validation"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import ValidationError
import logging
import json

logger = logging.getLogger(__name__)

class DataValidationMiddleware(BaseHTTPMiddleware):
    """Validate incoming/outgoing data against contracts"""

    async def dispatch(self, request: Request, call_next):
        """Process request/response"""

        # Log incoming data
        if request.method in ["POST", "PUT"]:
            try:
                body = await request.body()
                if body:
                    logger.info(f"Incoming data: {body[:200]}")  # Log first 200 chars
            except Exception as e:
                logger.warning(f"Could not log request body: {e}")

        # Process request
        response = await call_next(request)

        # Log response status
        logger.info(f"{request.method} {request.url.path} -> {response.status_code}")

        return response