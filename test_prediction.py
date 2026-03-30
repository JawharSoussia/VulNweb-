"""Test script for API prediction endpoints"""
import requests
import numpy as np
import json

BASE_URL = "http://localhost:8000"

# Feature names in order (34 total)
FEATURE_NAMES = [
    'dintpkt', 'sport', 'sttl', 'dloss', 'ct_srv_src',
    'ct_srv_dst', 'ct_dst_ltm', 'ct_src_ltm', 'ct_dst_sport',
    'ct_dst_src_ltm', 'ct_flw_http_mthd', 'is_ftp_login',
    'ct_ftp_cmd', 'ct_srv_admin', 'ct_srv_http', 'ct_src_dport_ltm',
    'ct_proto_udp', 'ct_proto_tcp', 'ct_proto_icmp', 'dmeansz',
    'djit', 'drate', 'dminsz', 'dpkt', 'dscore',
    'dtwin', 'dttl', 'dur', 'rate', 'res_bdy_len',
    'res_del_time', 'response_body_len', 'service_response_time', 'smeansz'
]


def test_raw_prediction():
    """Test raw prediction endpoint"""
    print("\n" + "="*70)
    print("TEST 1: Raw Prediction (Direct Features)")
    print("="*70)

    # Example 1: Safe network traffic (random benign features)
    print("\n[Test 1a] Benign traffic:")
    benign_features = [
        5, 443, 64, 0, 2, 1, 10, 20, 1,  # Network params (0-8)
        5, 0, 0, 0, 0, 1, 10,  # Connection counts (9-15)
        0, 1, 0,  # Protocol: TCP dominant (16-18)
        100, 0.1, 0.2, 50, 100,  # Packet metrics (19-23)
        0, 64, 100,  # Flags (24-26)
        2.5, 0.8,  # Duration & rate (27-28)
        1024, 0.1, 2048, 1.5,  # Response metrics (29-32)
        256  # Packet size (33)
    ]

    response = requests.post(
        f"{BASE_URL}/api/predict-raw",
        json={"features": benign_features}
    )
    result = response.json()

    print(f"  Status: {result.get('threat_level').upper()}")
    print(f"  Score: {result.get('threat_score'):.1f}%")
    print(f"  Confidence: {result.get('confidence'):.4f}")

    # Example 2: Suspicious traffic
    print("\n[Test 1b] Suspicious traffic:")
    suspicious_features = [
        50, 8883, 32, 100, 50, 40, 100, 200, 30,  # Many packets to many IPs
        50, 1, 1, 5, 10, 40, 100,  # High connection counts
        1, 0, 0,  # UDP dominant
        500, 10, 5.0, 10, 5000,  # Large packets
        1, 32, 50,
        10, 50,
        50000, 10, 100000, 50,
        5000
    ]

    response = requests.post(
        f"{BASE_URL}/api/predict-raw",
        json={"features": suspicious_features}
    )
    result = response.json()

    print(f"  Status: {result.get('threat_level').upper()}")
    print(f"  Score: {result.get('threat_score'):.1f}%")
    print(f"  Confidence: {result.get('confidence'):.4f}")


def test_features_endpoint():
    """Test features info endpoint"""
    print("\n" + "="*70)
    print("TEST 2: Model Features Information")
    print("="*70)

    response = requests.get(f"{BASE_URL}/api/features")
    result = response.json()

    print(f"\nFeatures expected: {result.get('feature_count')}")
    print(f"Feature names:")
    for i, fname in enumerate(result.get('features', []), 1):
        print(f"  {i:2d}. {fname}")


def test_health():
    """Test health endpoint"""
    print("\n" + "="*70)
    print("TEST 3: API Health Check")
    print("="*70)

    response = requests.get(f"{BASE_URL}/health")
    result = response.json()

    print(f"\nStatus: {result.get('status')}")
    print(f"Model loaded: {result.get('model_loaded')}")
    print(f"Version: {result.get('version')}")


if __name__ == "__main__":
    print("\n[INFO] VulNweb API - Prediction Endpoint Tests")
    print("[INFO] Make sure API is running: python -m uvicorn backend.app.main:app --reload")

    try:
        # Test health
        test_health()

        # Test features endpoint
        test_features_endpoint()

        # Test predictions
        test_raw_prediction()

        print("\n" + "="*70)
        print("All tests completed successfully!")
        print("="*70 + "\n")

    except requests.exceptions.ConnectionError:
        print("\n[ERROR] Could not connect to API at", BASE_URL)
        print("Make sure the server is running with:")
        print("  python -m uvicorn backend.app.main:app --reload")
    except Exception as e:
        print(f"\n[ERROR] {e}")
