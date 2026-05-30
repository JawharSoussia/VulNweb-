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

# 2. Batch Analysis
echo "2️⃣  Test Batch Analysis (Multiple URLs)"
echo "Command: curl -X POST $BASE_URL/threats/batch-analyze"
echo ""
curl -s -X POST "$BASE_URL/threats/batch-analyze" \
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

# 3. Network Threat Analysis
echo "3️⃣  Test Network Threat Analysis"
echo "Command: curl -X POST $BASE_URL/threats/network/analyze"
echo ""
curl -s -X POST "$BASE_URL/threats/network/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "flow_data": {
      "dur": 100.5,
      "sbytes": 5000,
      "dbytes": 10000,
      "spkts": 50,
      "dpkts": 100,
      "swin": 65535,
      "dwin": 65535,
      "sload": 500.0,
      "dload": 1000.0,
      "stcpb": 1,
      "dtcpb": 1,
      "smeansz": 100.0,
      "dmeansz": 100.0,
      "response_body_len": 50000,
      "sjit": 0.5,
      "djit": 0.5,
      "stime": 1000,
      "ltime": 2000,
      "sintpkt": 0.1,
      "dintpkt": 0.1,
      "tcprtt": 0.05,
      "synack": 0.02,
      "ackdat": 0.03,
      "is_sm_ips_ports": 0,
      "ct_state_ttl": 64,
      "ct_flw_http_mthd": 1,
      "is_ftp_login": 0,
      "ct_ftp_cmd": 0,
      "ct_srv_src": 10,
      "ct_srv_dst": 10,
      "ct_dst_ltm": 5,
      "ct_src_ltm": 5,
      "ct_src_dport_ltm": 3,
      "ct_dst_sport_ltm": 3,
      "ct_dst_src_ltm": 2,
      "is_sb_flow": 0
    }
  }' | jq . || echo "⚠️  Network analysis failed"
echo ""
echo ""

# 4. VirusTotal Scan (if API key is configured)
echo "4️⃣  Test VirusTotal Scan"
echo "Command: curl -X POST $BASE_URL/threats/virustotal/scan-url"
echo ""
curl -s -X POST "$BASE_URL/threats/virustotal/scan-url" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.eicar.org/download/eicar.com.txt"}' | jq . || echo "⚠️  VirusTotal scan failed (API key may not be configured)"
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
