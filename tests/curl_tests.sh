#!/bin/bash

# VulNweb API Curl Tests
# ========================

BASE_URL="http://localhost:8000"

echo "======================================================================"
echo "TEST 1: Health Check"
echo "======================================================================"
curl -X GET "$BASE_URL/health" \
  -H "Content-Type: application/json"

echo -e "\n\n======================================================================"
echo "TEST 2: Get Features List"
echo "======================================================================"
curl -X GET "$BASE_URL/api/features" \
  -H "Content-Type: application/json"

echo -e "\n\n======================================================================"
echo "TEST 3: Prediction with Raw Features (Benign Traffic)"
echo "======================================================================"
curl -X POST "$BASE_URL/api/predict-raw" \
  -H "Content-Type: application/json" \
  -d '{
    "features": [5, 443, 64, 0, 2, 1, 10, 20, 1, 5, 0, 0, 0, 0, 1, 10, 0, 1, 0, 100, 0.1, 0.2, 50, 100, 0, 64, 100, 2.5, 0.8, 1024, 0.1, 2048, 1.5, 256]
  }'

echo -e "\n\n======================================================================"
echo "TEST 4: Prediction with Raw Features (Suspicious Traffic)"
echo "======================================================================"
curl -X POST "$BASE_URL/api/predict-raw" \
  -H "Content-Type: application/json" \
  -d '{
    "features": [50, 8883, 32, 100, 50, 40, 100, 200, 30, 50, 1, 1, 5, 10, 40, 100, 1, 0, 0, 500, 10, 5.0, 10, 5000, 1, 32, 50, 10, 50, 50000, 10, 100000, 50, 5000]
  }'

echo -e "\n\n======================================================================"
echo "TEST 5: Submit Feedback (Correct Prediction)"
echo "======================================================================"
# Note: Use a request_id from a previous prediction response
curl -X POST "$BASE_URL/api/feedback" \
  -H "Content-Type: application/json" \
  -d '{
    "request_id": "req_1774378169",
    "is_correct": true,
    "comments": "Prediction was accurate, good job!"
  }'

echo -e "\n\n======================================================================"
echo "TEST 6: Submit Feedback (Incorrect Prediction)"
echo "======================================================================"
curl -X POST "$BASE_URL/api/feedback" \
  -H "Content-Type: application/json" \
  -d '{
    "request_id": "req_1774378169",
    "is_correct": false,
    "comments": "This should have been flagged as suspicious"
  }'

echo -e "\n\n======================================================================"
echo "TEST 7: Batch Predictions"
echo "======================================================================"
curl -X POST "$BASE_URL/api/predict-batch" \
  -H "Content-Type: application/json" \
  -d '{
    "requests": [
      {
        "url": "https://example.com",
        "ip_address": "192.168.1.1",
        "port": 443
      },
      {
        "url": "https://suspicious.com",
        "ip_address": "10.0.0.1",
        "port": 8883
      }
    ]
  }'

echo -e "\n\nAll tests completed!\n"
