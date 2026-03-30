"""
Quick Reference: VulNweb API Prediction Endpoints
==================================================

SOLUTION SUMMARY:
The API now has a working /api/predict-raw endpoint that accepts the 34 UNSW-NB15
network features that the model was trained on. This returns meaningful predictions.

ENDPOINTS:
===========

1. GET /health
   Status check
   Response: {status, model_loaded, version}

2. GET /api/features
   List all 34 expected features
   Response: {feature_count, features: [...], description}

3. POST /api/predict-raw ✅ USE THIS
   Direct feature prediction
   Body: {"features": [<34 float values>]}
   Response: {threat_score, threat_level, confidence, explanation, model_version, request_id, timestamp}

4. POST /api/predict (legacy)
   URL/IP prediction (needs feature engineering)
   Body: {"url": "...", "ip_address": "..."}

QUICK TEST:
===========

# Run API
python -m uvicorn backend.app.main:app --reload

# In another terminal, run tests
python test_prediction.py

# Or use Python directly:
python -c "
import requests
features = [5, 443, 64, 0, 2, 1, 10, 20, 1, 5, 0, 0, 0, 0, 1, 10, 0, 1, 0, 100, 0.1, 0.2, 50, 100, 0, 64, 100, 2.5, 0.8, 1024, 0.1, 2048, 1.5, 256]
r = requests.post('http://localhost:8000/api/predict-raw', json={'features': features})
print(r.json())
"

EXAMPLE RESPONSE:
=================
{
  "threat_score": 3.4,
  "threat_level": "safe",
  "confidence": 0.0344,
  "explanation": ["Network analysis complete", "Check threat score for details", "Request ID: req_123"],
  "model_version": "XGBoost",
  "request_id": "req_1774378169",
  "timestamp": "2026-03-24T18:49:29Z"
}

THREAT LEVELS:
==============
- safe:       0-30% threat score
- suspicious: 30-70% threat score
- critical:   70-100% threat score

34 FEATURES (in order):
=======================
0-8:   dintpkt, sport, sttl, dloss, ct_srv_src, ltime, ackdat, dload, ct_srv_dst
9-17:  djit, swin, stcpb, dtcpb, ct_src_ltm, dttl, ct_dst_src_ltm, sjit, dwin
18-25: tcprtt, synack, stime, spkts, ct_src_dport_ltm, sload, dpkts, dur
26-34: ct_dst_ltm, sintpkt, packet_ratio, src_bytes_per_pkt, dst_bytes_per_pkt,
       high_duration, log_duration, ttl_diff

All numeric, float type expected.
"""
