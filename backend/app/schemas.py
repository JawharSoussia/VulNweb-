"""Pydantic Schemas (Data Contracts)"""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class PredictionRequest(BaseModel):
    """Input schema for prediction request"""
    url: str
    ip_address: str
    file_hash: str = None
    logs: str = None

class ExplanationItem(BaseModel):
    """Single explanation reason"""
    reason: str
    importance: float

class PredictionResponse(BaseModel):
    """Output schema for prediction response"""
    threat_score: float  # 0-100
    confidence: float    # 0-1
    explanation: List[ExplanationItem]
    threat_level: str    # "safe", "suspicious", "critical"

class FeedbackRequest(BaseModel):
    """User feedback schema"""
    prediction_id: int
    is_correct: bool
    comments: str = None

# UNSW-NB15 Network Threat Schemas
class NetworkThreatRequest(BaseModel):
    """Request schema for network threat detection"""
    source_ip: str
    destination_ip: str
    source_port: int
    destination_port: int
    protocol: str
    flow_duration: float
    total_fwd_packets: int
    total_bwd_packets: int
    additional_features: Optional[Dict[str, float]] = None

class NetworkThreatResponse(BaseModel):
    """Response schema for network threat detection"""
    threat_score: float
    threat_level: str  # "safe", "suspicious", "critical"
    confidence: float
    attack_category: Optional[str]
    explanation: List[ExplanationItem]

class NetworkThreatLog(BaseModel):
    """Database model for network threat"""
    id: int
    source_ip: str
    destination_ip: str
    source_port: int
    destination_port: int
    protocol: str
    threat_score: float
    threat_level: str
    model_confidence: float
    created_at: datetime

    class Config:
        from_attributes = True

# VirusTotal Schemas
class VirusTotalURLScanRequest(BaseModel):
    """Request schema for VirusTotal URL scan"""
    url: str

class VirusTotalFileScanRequest(BaseModel):
    """Request schema for VirusTotal file hash scan"""
    file_hash: str

class VirusTotalScanResponse(BaseModel):
    """Response schema for VirusTotal scan"""
    scan_target: str
    scan_type: str  # "url" or "file"
    malicious_detections: int
    total_vendors: int
    detection_ratio: str
    threat_level: str
    additional_data: Optional[Dict[str, Any]] = None

class VirusTotalScanLog(BaseModel):
    """Database model for VirusTotal scan"""
    id: int
    scan_target: str
    scan_type: str
    malicious_detections: int
    total_vendors: int
    threat_level: str
    created_at: datetime

    class Config:
        from_attributes = True

# Batch Analysis Schemas
class BatchAnalysisRequest(BaseModel):
    """Request schema for batch analysis"""
    urls: Optional[List[str]] = None
    file_hashes: Optional[List[str]] = None
    network_flows: Optional[List[NetworkThreatRequest]] = None

class BatchAnalysisResponse(BaseModel):
    """Response schema for batch analysis"""
    total_items: int
    threats_detected: int
    critical_count: int
    suspicious_count: int
    results: List[Dict[str, Any]]