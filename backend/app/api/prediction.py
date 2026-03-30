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

        # Extract input values
        url_length = len(request_data.url)
        port = request_data.port or 443
        bytes_in = request_data.bytes_in or 0
        bytes_out = request_data.bytes_out or 0
        duration = request_data.duration or 1.0
        packets = request_data.packets or 1

        # Derive additional network features from input data
        # These simulate realistic UNSW-NB15 network flow characteristics
        feature_dict = {}

        # Basic flow features
        feature_dict['dur'] = max(duration, 0.1)
        feature_dict['sbytes'] = max(bytes_out, 0)
        feature_dict['dbytes'] = max(bytes_in, 0)
        feature_dict['spkts'] = max(packets, 1)
        feature_dict['dpkts'] = max(packets // 2, 1)

        # Derived metrics
        feature_dict['swin'] = 65535
        feature_dict['dwin'] = 65535
        feature_dict['sload'] = (bytes_out / max(duration, 0.1)) if duration > 0 else 0
        feature_dict['dload'] = (bytes_in / max(duration, 0.1)) if duration > 0 else 0
        feature_dict['stcpb'] = 1 if request_data.protocol == "tcp" else 0
        feature_dict['dtcpb'] = 1 if request_data.protocol == "tcp" else 0
        feature_dict['smeansz'] = bytes_out / max(packets, 1)
        feature_dict['dmeansz'] = bytes_in / max(packets // 2, 1)
        feature_dict['response_body_len'] = bytes_in
        feature_dict['sjit'] = 0.1
        feature_dict['djit'] = 0.1
        feature_dict['stime'] = 0
        feature_dict['ltime'] = int(duration)
        feature_dict['sintpkt'] = 0.01
        feature_dict['dintpkt'] = 0.01
        feature_dict['tcprtt'] = 0.05
        feature_dict['synack'] = 0.02
        feature_dict['ackdat'] = 0.03
        feature_dict['is_sm_ips_ports'] = 0
        feature_dict['ct_state_ttl'] = 64
        feature_dict['ct_flw_http_mthd'] = 1 if port in [80, 443, 8080] else 0
        feature_dict['is_ftp_login'] = 0
        feature_dict['ct_ftp_cmd'] = 0
        feature_dict['ct_srv_src'] = 1
        feature_dict['ct_srv_dst'] = 1
        feature_dict['ct_dst_ltm'] = 1
        feature_dict['ct_src_ltm'] = 1
        feature_dict['ct_src_dport_ltm'] = 1
        feature_dict['ct_dst_sport_ltm'] = 1
        feature_dict['ct_dst_src_ltm'] = 1
        feature_dict['is_sb_flow'] = 0

        # Add derived features for threat detection
        # High bytes_out relative to bytes_in may indicate data exfiltration
        feature_dict['bytes_ratio'] = (bytes_out / max(bytes_in, 1)) if bytes_in > 0 else 1.0
        feature_dict['packet_ratio'] = (packets / max(packets // 2, 1)) if (packets // 2) > 0 else 1.0

        # Create feature vector in correct order using model's expected feature names
        X = np.array([
            feature_dict.get(fname, 0)
            for fname in model_package.feature_names
        ]).reshape(1, -1)

        logger.info(f"[{request_id}] Features prepared: {X.shape[1]} features")
        logger.info(f"[{request_id}] Duration: {duration}s, Bytes: {bytes_out}→{bytes_in}, Packets: {packets}")

        # ====================================================================
        # 3. MAKE PREDICTION
        # ====================================================================

        prediction = model_package.predict(X)

        threat_score = prediction['threat_score']
        confidence = prediction['confidence']
        threat_level = prediction['threat_level']

        # ====================================================================
        # HEURISTIC THREAT SCORING (enhance model with feature analysis)
        # ====================================================================

        # Calculate suspicious indicators from network flow
        heuristic_score = 0.0
        reasons = []

        # 1. Data exfiltration indicators (high bytes_out relative to bytes_in)
        bytes_ratio = feature_dict.get('bytes_ratio', 0)
        if bytes_ratio > 3:  # Lowered from 10 to 5
            heuristic_score += 50
            reasons.append(f"Abnormal data flow: {bytes_ratio:.1f}x more outbound than inbound")
        elif bytes_ratio > 2:
            heuristic_score += 35
            reasons.append("High outbound data ratio")

        # 2. Large data transfer on unusual ports
        sbytes = feature_dict.get('sbytes', 0)
        port = request_data.port or 0
        if sbytes > 100000 and port not in [80, 443, 8080]:  # Lowered from 1M to 100K
            heuristic_score += 40
            reasons.append(f"Large data transfer on non-standard port {port}")

        # 3. High packet count in short duration (potential DDoS/scanning)
        spkts = feature_dict.get('spkts', 0)
        duration = feature_dict.get('dur', 1)
        pps = spkts / max(duration, 0.1)  # packets per second
        if pps > 500:  # Lowered from 1000 to 500
            heuristic_score += 50
            reasons.append(f"High packet rate ({pps:.0f} pps): Potential scanning or flooding")
        elif pps > 250:
            heuristic_score += 35
            reasons.append(f"Elevated packet rate ({pps:.0f} pps)")

        # 4. Suspicious protocol combinations
        is_tcp = feature_dict.get('stcpb', 0)
        is_http = feature_dict.get('ct_flw_http_mthd', 0)
        if is_tcp and not is_http and port in [80, 443]:
            heuristic_score += 25
            reasons.append("Non-HTTP protocol on HTTP port (unusual)")

        # 5. Multiple service connections from single source
        ct_srv_src = feature_dict.get('ct_srv_src', 1)
        if ct_srv_src > 50:
            heuristic_score += 35
            reasons.append(f"Multiple services from single source ({ct_srv_src} connections)")

        # 6. Very long connections might indicate command & control
        duration_hours = duration / 3600
        if duration_hours > 0.5:  # Long-lived connection (>30 mins)
            heuristic_score += 50
            reasons.append(f"Prolonged connection ({duration_hours:.1f}hrs): Potential C2 or persistence")
        elif duration_hours > 0.1:
            heuristic_score += 25
            reasons.append(f"Elevated connection duration ({duration_hours*60:.0f} minutes)")

        # Combine model prediction with heuristic scoring
        # Give 40% weight to model, 60% to heuristics (heuristics more important for real detections)
        combined_score = (threat_score * 0.4) + (heuristic_score * 0.6)

        # Ensure score stays in valid range
        combined_score = min(max(combined_score, 0), 100)

        # Update threat level based on combined score
        if combined_score >= 70:
            threat_level = "critical"
        elif combined_score >= 30:
            threat_level = "suspicious"
        else:
            threat_level = "safe"

        # Add heuristic analysis to explanation
        if not reasons:
            reasons = ["Normal network behavior"]

        logger.info(f"[{request_id}] Model score: {threat_score:.2f}, Heuristic: {heuristic_score:.2f}, Combined: {combined_score:.2f}")
        logger.info(f"[{request_id}] Threat indicators: {reasons[:3]}")

        # Update threat_score with combined score
        threat_score = combined_score

        # ====================================================================
        # 4. GET EXPLANATIONS
        # ====================================================================

        explanation_list = reasons[:3]  # Use heuristic reasons
        try:
            # Try to get additional model explanations
            explanations = model_package.explain(X, k=2)
            if explanations:
                model_reasons = explanations[0]
                # Combine heuristic + model explanations
                explanation_list = reasons[:2] + model_reasons[:1]
        except Exception as e:
            logger.warning(f"[{request_id}] Could not generate model explanations: {e}")

        logger.info(f"[{request_id}] Explanation: {explanation_list}")

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


# ============================================================================
# RAW FEATURES ENDPOINT (Direct UNSW-NB15 features)
# ============================================================================

class RawPredictionRequest(BaseModel):
    """Raw feature vector input (34 UNSW-NB15 features)"""

    features: List[float] = Field(
        ...,
        min_length=34,
        max_length=34,
        description="34 network flow features from UNSW-NB15 dataset"
    )


@router.post(
    "/predict-raw",
    response_model=PredictionResponse,
    summary="Predict from raw features",
    description="Direct prediction using 34 UNSW-NB15 network features"
)
async def predict_raw(raw_request: RawPredictionRequest, request: Request) -> PredictionResponse:
    """
    Make prediction using raw UNSW-NB15 features directly

    **Parameters:**
    - features: List of exactly 34 network flow feature values

    **Feature order:**
    ```
    0: dintpkt, 1: sport, 2: sttl, 3: dloss, 4: ct_srv_src,
    5: ct_srv_dst, 6: ct_dst_ltm, 7: ct_src_ltm, 8: ct_dst_sport,
    9: ct_dst_src_ltm, 10: ct_flw_http_mthd, 11: is_ftp_login,
    12: ct_ftp_cmd, 13: ct_srv_admin, 14: ct_srv_http, 15: ct_src_dport_ltm,
    16: ct_proto_udp, 17: ct_proto_tcp, 18: ct_proto_icmp, 19: dmeansz,
    20: djit, 21: drate, 22: dminsz, 23: dpkt, 24: dscore,
    25: dtwin, 26: dttl, 27: dur, 28: rate, 29: res_bdy_len,
    30: res_del_time, 31: response_body_len, 32: service_response_time,
    33: smeansz
    ```

    **Returns:**
    - threat_score: 0-100 scale (higher = more threatening)
    - threat_level: "safe" (0-30) / "suspicious" (30-70) / "critical" (70-100)
    - confidence: Model confidence (0-1)
    - explanation: Top 3 decision factors
    - model_version: Model name
    - request_id: Unique request ID
    - timestamp: Prediction time

    **Example:**
    ```
    POST /api/predict-raw
    {
      "features": [1.0, 443, 64, 0, 2, 1, 5, 10, 2, 15, 0, 0,
                   0, 0, 0, 0, 0, 1, 0, 100, 0.5, 0.2, 20, 50,
                   0, 64, 100, 2.5, 0.8, 1024, 0.1, 2048, 1.5, 256]
    }
    ```
    """

    request_id = f"req_{datetime.now().timestamp():.0f}"

    try:
        logger.info(f"[{request_id}] Raw prediction request with {len(raw_request.features)} features")

        model_package = request.app.state.model_package

        if model_package is None:
            logger.error(f"[{request_id}] Model not loaded")
            raise HTTPException(
                status_code=503,
                detail="Model not available"
            )

        # Convert features to numpy array
        X = np.array(raw_request.features).reshape(1, -1)

        logger.info(f"[{request_id}] Features shape: {X.shape}")

        # Make prediction
        prediction = model_package.predict(X)

        threat_score = prediction['threat_score']
        confidence = prediction['confidence']
        threat_level = prediction['threat_level']

        logger.info(f"[{request_id}] Prediction: {threat_level} (score={threat_score:.1f}%)")

        # Get explanations
        explanation_list = []
        try:
            explanations = model_package.explain(X, k=3)
            if explanations:
                explanation_list = explanations[0]
        except Exception as e:
            logger.warning(f"[{request_id}] Explanations unavailable: {e}")

        response = PredictionResponse(
            threat_score=threat_score,
            threat_level=threat_level,
            confidence=confidence,
            explanation=explanation_list if explanation_list else [
                "Network analysis complete",
                "Check threat score for details",
                "Request ID: " + request_id
            ],
            model_version=model_package.metadata.get('model_name', 'v1.0'),
            request_id=request_id,
            timestamp=datetime.utcnow().isoformat() + "Z"
        )

        logger.info(f"[{request_id}] Response sent")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Raw prediction error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Prediction failed")