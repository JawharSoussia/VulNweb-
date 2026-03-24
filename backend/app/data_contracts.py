"""Data Contracts - Pydantic Models for Validation"""
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
import numpy as np

class PredictionDataContract(BaseModel):
    """Contract for incoming prediction request data"""

    url: str = Field(..., min_length=1, description="Target URL")
    ip_address: str = Field(
        ...,
        pattern=r"^(\d{1,3}\.){3}\d{1,3}$",
        description="IPv4 address in dotted notation"
    )
    port: Optional[int] = Field(None, ge=0, le=65535, description="Port number")
    protocol: Optional[str] = Field(None, pattern="^(tcp|udp|icmp)$", description="Protocol type")
    bytes_sent: Optional[float] = Field(None, ge=0)
    bytes_received: Optional[float] = Field(None, ge=0)
    duration: Optional[float] = Field(None, ge=0)
    packets: Optional[int] = Field(None, ge=0)

    @field_validator('url')
    @classmethod
    def validate_url(cls, v):
        """Validate URL format"""
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        return v

    @field_validator('ip_address')
    @classmethod
    def validate_ip(cls, v):
        """Validate IP address ranges"""
        octets = [int(x) for x in v.split('.')]
        if any(o > 255 or o < 0 for o in octets):
            raise ValueError('Invalid IP address octets')
        return v

    @field_validator('bytes_sent', 'bytes_received', 'duration')
    @classmethod
    def check_non_negative(cls, v):
        """Ensure non-negative values"""
        if v is not None and v < 0:
            raise ValueError('Value must be non-negative')
        return v

    class Config:
        strict = True


class PredictionResponseContract(BaseModel):
    """Contract for prediction response"""

    threat_score: float = Field(..., ge=0, le=100, description="Threat score 0-100")
    confidence: float = Field(..., ge=0, le=1, description="Confidence 0-1")
    threat_level: str = Field(
        ...,
        pattern="^(safe|suspicious|critical)$",
        description="Threat level category"
    )
    explanation: List[str] = Field(..., max_length=3, description="Top 3 reasons")
    model_version: str = Field(..., description="Model version used")

    class Config:
        strict = True


class FeedbackDataContract(BaseModel):
    """Contract for user feedback"""

    prediction_id: int = Field(..., gt=0)
    is_correct: bool
    comments: Optional[str] = Field(None, max_length=500)

    class Config:
        strict = True