"""
Mock Test Data Generator for VulNweb Extension Testing
Generates synthetic threat predictions without needing real malicious URLs
"""

import requests
import json
import random
from datetime import datetime

BASE_URL = "http://localhost:8000"

# Test URLs with different threat scenarios
TEST_CASES = [
    {
        "url": "https://example-safe.com",
        "name": "Safe Website",
        "threat_level": 1,
        "description": "Legitimate website"
    },
    {
        "url": "https://suspicious-site.xyz",
        "name": "Suspicious Site",
        "threat_level": 5,
        "description": "Site with suspicious characteristics"
    },
    {
        "url": "https://malware-download.net",
        "name": "Malware Site",
        "threat_level": 9,
        "description": "Known malware distribution site"
    },
    {
        "url": "https://phishing-attempt.org",
        "name": "Phishing Attempt",
        "threat_level": 8,
        "description": "Phishing/credential harvesting"
    },
    {
        "url": "https://botnet-command.cc",
        "name": "Botnet C&C",
        "threat_level": 10,
        "description": "Command & Control server"
    },
]

def generate_mock_network_flow():
    """Generate mock UNSW-NB15 network flow data"""
    features = {
        "dur": random.uniform(0.1, 1000),
        "sbytes": random.randint(0, 1000000),
        "dbytes": random.randint(0, 1000000),
        "spkts": random.randint(1, 10000),
        "dpkts": random.randint(1, 10000),
        "swin": random.randint(1, 65535),
        "dwin": random.randint(1, 65535),
        "sload": random.uniform(0, 1000),
        "dload": random.uniform(0, 1000),
        "stcpb": random.randint(0, 1),
        "dtcpb": random.randint(0, 1),
        "smeansz": random.uniform(0, 1500),
        "dmeansz": random.uniform(0, 1500),
        "response_body_len": random.randint(0, 100000),
        "sjit": random.uniform(0, 1),
        "djit": random.uniform(0, 1),
        "stime": random.randint(0, 1000000),
        "ltime": random.randint(0, 1000000),
        "sintpkt": random.uniform(0, 1),
        "dintpkt": random.uniform(0, 1),
        "tcprtt": random.uniform(0, 1),
        "synack": random.uniform(0, 1),
        "ackdat": random.uniform(0, 1),
        "is_sm_ips_ports": random.randint(0, 1),
        "ct_state_ttl": random.randint(0, 255),
        "ct_flw_http_mthd": random.randint(0, 30),
        "is_ftp_login": random.randint(0, 1),
        "ct_ftp_cmd": random.randint(0, 50),
        "ct_srv_src": random.randint(0, 255),
        "ct_srv_dst": random.randint(0, 255),
        "ct_dst_ltm": random.randint(0, 255),
        "ct_src_ltm": random.randint(0, 255),
        "ct_src_dport_ltm": random.randint(0, 255),
        "ct_dst_sport_ltm": random.randint(0, 255),
        "ct_dst_src_ltm": random.randint(0, 255),
        "is_sb_flow": random.randint(0, 1),
    }
    return features

def test_predict(threat_level):
    """Test prediction endpoint"""
    print(f"\n> Testing Prediction with URL (Threat Level Simulation: {threat_level}/10)...")

    # Create varied test URLs based on threat level
    urls = [
        "https://www.google.com",          # Safe
        "https://suspicious-site.xyz",     # Suspicious
        "https://malware-download.net",    # Malware
        "https://phishing-attempt.org"     # Phishing
    ]

    test_url = urls[min(threat_level // 3, len(urls) - 1)]

    prediction_request = {
        "url": test_url,
        "ip_address": f"192.168.{random.randint(1, 254)}.{random.randint(1, 254)}",
        "port": random.choice([80, 443, 8080]),
        "protocol": random.choice(["tcp", "udp"]),
        "bytes_in": random.randint(0, 100000) * threat_level,
        "bytes_out": random.randint(0, 50000) * threat_level,
        "duration": random.uniform(0.1, 100) * threat_level / 5,
        "packets": random.randint(1, 1000) * threat_level
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/predict",
            json=prediction_request,
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            print(f" Prediction Response:")
            print(f"  - URL: {prediction_request['url']}")
            print(f"  - Threat Score: {data.get('threat_score', 'N/A')}")
            print(f"  - Threat Level: {data.get('threat_level', 'N/A')}")
            print(f"  - Confidence: {data.get('confidence', 'N/A')}")
            print(f"  - Explanation: {data.get('explanation', [])[:2]}")
            return data
        else:
            print(f" Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f" Connection Error: {e}")


def test_virustotal_scan(url, threat_level):
    """Test prediction endpoint with external URL"""
    print(f"\n Testing Prediction with External URL: {url}")

    prediction_request = {
        "url": url,
        "ip_address": f"192.168.{random.randint(1, 254)}.{random.randint(1, 254)}",
        "port": 443,
        "protocol": "tcp"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/predict",
            json=prediction_request,
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            print(f" Prediction Response:")
            print(f"  - Threat Score: {data.get('threat_score', 'N/A')}")
            print(f"  - Threat Level: {data.get('threat_level', 'N/A')}")
            print(f"  - Confidence: {data.get('confidence', 'N/A')}")
            return data
        else:
            print(f" Error: {response.status_code} - {response.text}")
    except requests.exceptions.Timeout:
        print(f" Request Timeout")
    except Exception as e:
        print(f" Connection Error: {e}")


def test_health_check():
    """Test API health endpoint"""
    print(" Testing API Health Check...")

    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)

        if response.status_code == 200:
            data = response.json()
            print(f" API is {data.get('status', 'unknown').upper()}")
            print(f"  - Model Loaded: {data.get('model_loaded', False)}")
            print(f"  - Version: {data.get('version', 'N/A')}")
            return True
        else:
            print(f" Error: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f" Cannot connect to API at {BASE_URL}")
        print(f"   Make sure backend is running: python -m uvicorn backend.app.main:app --reload")
        return False
    except Exception as e:
        print(f" Error: {e}")
        return False


def test_batch_analysis():
    """Test batch prediction endpoint"""
    print(f"\n Testing Batch Prediction...")

    batch_requests = [
        {
            "url": "https://www.google.com",
            "ip_address": "192.168.1.1",
            "port": 443,
            "protocol": "tcp"
        },
        {
            "url": "https://www.github.com",
            "ip_address": "192.168.1.2",
            "port": 443,
            "protocol": "tcp",
            "bytes_in": 50000,
            "bytes_out": 25000
        },
        {
            "url": "https://suspicious-site.xyz",
            "ip_address": "192.168.1.3",
            "port": 8080,
            "protocol": "tcp",
            "bytes_in": 500000,
            "bytes_out": 250000,
            "packets": 5000
        }
    ]

    batch_data = {
        "requests": batch_requests
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/predict-batch",
            json=batch_data,
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            print(f" Batch Prediction Response:")
            print(f"  - Batch ID: {data.get('batch_id', 'N/A')}")
            print(f"  - Total Requests: {data.get('total', 0)}")
            print(f"  - Successful: {data.get('success', 0)}")
            print(f"  - Failed: {data.get('failed', 0)}")

            if data.get('results'):
                print(f"\n  Individual Results:")
                for i, result in enumerate(data.get('results', [])[:3]):
                    print(f"    [{i+1}] {result.get('threat_level', 'N/A')} (Score: {result.get('threat_score', 'N/A')})")
            return data
        else:
            print(f" Error: {response.status_code}")
    except Exception as e:
        print(f" Error: {e}")


def run_all_tests():
    """Run complete test suite"""
    print("=" * 70)
    print("VulNweb Extension - Complete Test Suite")
    print("=" * 70)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 1. Health Check
    if not test_health_check():
        print("\n  Backend is not running. Skipping other tests.")
        print("Start backend with: python -m uvicorn backend.app.main:app --reload")
        return

    # 2. Prediction Tests
    print("\n" + "=" * 70)
    print("THREAT PREDICTION TESTS")
    print("=" * 70)

    threat_levels = [1, 4, 7, 10]
    for level in threat_levels:
        test_predict(level)
        print()

    # 3. External URL Tests
    print("=" * 70)
    print("EXTERNAL URL TESTS")
    print("=" * 70)

    for case in TEST_CASES[:3]:
        test_virustotal_scan(case["url"], case["threat_level"])
        print()

    # 4. Batch Analysis
    print("=" * 70)
    print("BATCH ANALYSIS TEST")
    print("=" * 70)
    test_batch_analysis()

    print("\n" + "=" * 70)
    print(" Test Suite Complete")
    print("=" * 70)
    print("\nNext Steps:")
    print("1. Open Chrome and navigate to a test website (e.g., https://www.google.com)")
    print("2. Click the VulNweb extension icon")
    print("3. You should see threat analysis results")
    print("4. Check the background console for detailed logs (F12 in extension popup)")


if __name__ == "__main__":
    run_all_tests()
