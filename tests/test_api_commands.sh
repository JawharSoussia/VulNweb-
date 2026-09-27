#!/bin/bash
# VulNweb Extension API Testing Commands
# Usage: bash test_api_commands.sh

BASE_URL="http://localhost:8000"

echo "=================================================="
echo "VulNweb API Testing Commands"
echo "=================================================="
echo ""

# 1. Health Check
echo "1️⃣  Test Health Endpoint"
echo "Command: curl $BASE_URL/health"
echo ""
curl -s "$BASE_URL/health" | jq . || echo "⚠️  API not running"
echo ""
echo ""

# 2. Batch Prediction
echo "2️⃣  Test Batch Prediction (Multiple URLs)"
echo "Command: curl -X POST $BASE_URL/api/predict-batch"
echo ""
curl -s -X POST "$BASE_URL/api/predict-batch" \
  -H "Content-Type: application/json" \
  -d '{
    "urls": [
      "https://www.google.com",
      "https://www.github.com",
      "https://www.wikipedia.org"
    ]
  }' | jq . || echo "⚠️  Batch analysis failed"
echo ""
echo ""

# 3. URL Threat Prediction
echo "3️⃣  Test URL Threat Prediction"
echo "Command: curl -X POST $BASE_URL/api/predict"
echo ""
curl -s -X POST "$BASE_URL/api/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/login?redirect=http://evil.test"
  }' | jq . || echo "⚠️  URL prediction failed"
echo ""
echo ""

# 4. Raw Feature Prediction
echo "4️⃣  Test Raw Feature Prediction"
echo "Command: curl -X POST $BASE_URL/api/predict-raw"
echo ""
curl -s -X POST "$BASE_URL/api/predict-raw" \
  -H "Content-Type: application/json" \
  -d '{"features": [5, 443, 64, 0, 2, 1, 10, 20, 1, 5, 0, 0, 0, 0, 1, 10, 0, 1, 0, 100, 0.1, 0.2, 50, 100, 0, 64, 100, 2.5, 0.8, 1024, 0.1, 2048, 1.5, 256]}' | jq . || echo "⚠️  Raw prediction failed"
echo ""
echo ""

# 5. API Documentation
echo "5️⃣  API Documentation"
echo "URL: $BASE_URL/docs"
echo "Open this URL in your browser to see interactive Swagger UI"
echo ""

echo "=================================================="
echo "Testing Complete!"
echo "=================================================="
