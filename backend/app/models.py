"""Database Models"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Prediction(Base):
    """Prediction Log Model for Network Threats"""
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String, index=True)
    url = Column(String)
    threat_score = Column(Float)
    explanation = Column(String)
    confidence = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

class NetworkThreat(Base):
    """Network-based Threat Detection Model (UNSW-NB15)"""
    __tablename__ = "network_threats"

    id = Column(Integer, primary_key=True, index=True)
    source_ip = Column(String, index=True)
    destination_ip = Column(String, index=True)
    source_port = Column(Integer)
    destination_port = Column(Integer)
    protocol = Column(String)
    flow_duration = Column(Float)
    total_fwd_packets = Column(Integer)
    total_bwd_packets = Column(Integer)
    threat_score = Column(Float)
    threat_level = Column(String)  # "safe", "suspicious", "critical"
    model_confidence = Column(Float)
    attack_category = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class VirusTotalScan(Base):
    """VirusTotal Scan Results Model"""
    __tablename__ = "virustotal_scans"

    id = Column(Integer, primary_key=True, index=True)
    scan_target = Column(String, index=True)  # URL or file hash
    scan_type = Column(String)  # "url" or "file"
    malicious_detections = Column(Integer)
    total_vendors = Column(Integer)
    threat_level = Column(String)
    vt_scan_id = Column(String, nullable=True)
    additional_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Feedback(Base):
    """User Feedback Model"""
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    prediction_id = Column(Integer)
    user_feedback = Column(String)  # "correct" or "incorrect"
    created_at = Column(DateTime, default=datetime.utcnow)