"""
VulNweb API Usage Examples

This script demonstrates how to use the VulNweb API with:
- VirusTotal integration
- UNSW-NB15 network threat detection
- Batch analysis
"""

import requests
import json
from typing import Dict, Any

# API base URL
BASE_URL = "http://localhost:8000"


class VulNwebClient:
    """Client for interacting with VulNweb API"""

    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()

    def health_check(self) -> Dict[str, Any]:
        """Check API health"""
        response = self.session.get(f"{self.base_url}/health")
        return response.json()

    def scan_url(self, url: str) -> Dict[str, Any]:
        """Scan URL with VirusTotal"""
        response = self.session.post(
            f"{self.base_url}/threats/virustotal/scan-url",
            json={"url": url}
        )
        return response.json()

    def scan_file_hash(self, file_hash: str) -> Dict[str, Any]:
        """Scan file hash with VirusTotal"""
        response = self.session.post(
            f"{self.base_url}/threats/virustotal/scan-file",
            json={"file_hash": file_hash}
        )
        return response.json()

    def analyze_network_flow(
        self,
        source_ip: str,
        destination_ip: str,
        source_port: int,
        destination_port: int,
        protocol: str,
        flow_duration: float,
        total_fwd_packets: int,
        total_bwd_packets: int
    ) -> Dict[str, Any]:
        """Analyze network flow for threats"""
        response = self.session.post(
            f"{self.base_url}/threats/network/analyze",
            json={
                "source_ip": source_ip,
                "destination_ip": destination_ip,
                "source_port": source_port,
                "destination_port": destination_port,
                "protocol": protocol,
                "flow_duration": flow_duration,
                "total_fwd_packets": total_fwd_packets,
                "total_bwd_packets": total_bwd_packets
            }
        )
        return response.json()

    def batch_analyze(
        self,
        urls: list = None,
        file_hashes: list = None,
        network_flows: list = None
    ) -> Dict[str, Any]:
        """Perform batch analysis"""
        response = self.session.post(
            f"{self.base_url}/threats/batch-analyze",
            json={
                "urls": urls,
                "file_hashes": file_hashes,
                "network_flows": network_flows
            }
        )
        return response.json()

    def get_dataset_info(self) -> Dict[str, Any]:
        """Get UNSW-NB15 dataset information"""
        response = self.session.get(f"{self.base_url}/threats/dataset/info")
        return response.json()

    def download_dataset(self) -> Dict[str, Any]:
        """Download UNSW-NB15 dataset"""
        response = self.session.get(f"{self.base_url}/threats/download-dataset")
        return response.json()


def example_health_check():
    """Example: Check API health"""
    print("=" * 60)
    print("Example 1: Health Check")
    print("=" * 60)

    client = VulNwebClient()
    result = client.health_check()
    print(json.dumps(result, indent=2))
    print()


def example_virustotal_url_scan():
    """Example: Scan URL with VirusTotal"""
    print("=" * 60)
    print("Example 2: VirusTotal URL Scan")
    print("=" * 60)

    client = VulNwebClient()

    # Scan a safe URL
    result = client.scan_url("https://www.google.com")
    print("Scanning: https://www.google.com")
    print(json.dumps(result, indent=2))
    print()

    # Scan another URL
    result = client.scan_url("https://www.github.com")
    print("Scanning: https://www.github.com")
    print(json.dumps(result, indent=2))
    print()


def example_virustotal_file_scan():
    """Example: Scan file hash with VirusTotal"""
    print("=" * 60)
    print("Example 3: VirusTotal File Hash Scan")
    print("=" * 60)

    client = VulNwebClient()

    # Example file hashes (these are famous malware hashes)
    file_hashes = [
        "affe6aff8a5de9f59dc4a3e7b02a6ddf",  # Fake hash for demo
    ]

    for file_hash in file_hashes:
        result = client.scan_file_hash(file_hash)
        print(f"Scanning file hash: {file_hash}")
        print(json.dumps(result, indent=2))
        print()


def example_network_threat_analysis():
    """Example: Analyze network flows for threats"""
    print("=" * 60)
    print("Example 4: Network Threat Analysis (UNSW-NB15)")
    print("=" * 60)

    client = VulNwebClient()

    # Example network flows
    flows = [
        {
            "label": "Normal HTTPS traffic",
            "source_ip": "192.168.1.100",
            "destination_ip": "142.250.185.46",  # google.com
            "source_port": 54321,
            "destination_port": 443,
            "protocol": "TCP",
            "flow_duration": 120.5,
            "total_fwd_packets": 150,
            "total_bwd_packets": 140
        },
        {
            "label": "Suspicious port communication",
            "source_ip": "192.168.1.50",
            "destination_ip": "10.0.0.1",
            "source_port": 12345,
            "destination_port": 4444,  # Suspicious port
            "protocol": "TCP",
            "flow_duration": 300.0,
            "total_fwd_packets": 50,
            "total_bwd_packets": 200
        },
        {
            "label": "DoS-like traffic pattern",
            "source_ip": "203.0.113.50",
            "destination_ip": "192.168.1.1",  # Local gateway
            "source_port": 65432,
            "destination_port": 80,
            "protocol": "TCP",
            "flow_duration": 5000.0,
            "total_fwd_packets": 1000,
            "total_bwd_packets": 50
        }
    ]

    for flow in flows:
        label = flow.pop("label")
        print(f"\nAnalyzing: {label}")
        result = client.analyze_network_flow(**flow)
        print(json.dumps(result, indent=2))


def example_batch_analysis():
    """Example: Batch analysis of multiple threats"""
    print("=" * 60)
    print("Example 5: Batch Analysis")
    print("=" * 60)

    client = VulNwebClient()

    # Prepare batch data
    batch_data = {
        "urls": [
            "https://www.google.com",
            "https://www.github.com"
        ],
        "file_hashes": [
            "affe6aff8a5de9f59dc4a3e7b02a6ddf"
        ],
        "network_flows": [
            {
                "source_ip": "192.168.1.100",
                "destination_ip": "142.250.185.46",
                "source_port": 54321,
                "destination_port": 443,
                "protocol": "TCP",
                "flow_duration": 120.5,
                "total_fwd_packets": 150,
                "total_bwd_packets": 140
            }
        ]
    }

    result = client.batch_analyze(
        urls=batch_data["urls"],
        file_hashes=batch_data["file_hashes"],
        network_flows=batch_data["network_flows"]
    )

    print("Batch Analysis Results:")
    print(f"Total items analyzed: {result['total_items']}")
    print(f"Threats detected: {result['threats_detected']}")
    print(f"Critical: {result['critical_count']}")
    print(f"Suspicious: {result['suspicious_count']}")
    print("\nDetailed Results:")
    print(json.dumps(result, indent=2))
    print()


def example_dataset_info():
    """Example: Get dataset information"""
    print("=" * 60)
    print("Example 6: UNSW-NB15 Dataset Information")
    print("=" * 60)

    client = VulNwebClient()

    result = client.get_dataset_info()
    print("Dataset Information:")
    print(json.dumps(result, indent=2))
    print()


def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("VulNweb API Usage Examples")
    print("=" * 60 + "\n")

    try:
        # Test health first
        client = VulNwebClient()
        health = client.health_check()
        if health["status"] != "ok":
            print("ERROR: API is not healthy. Make sure the server is running.")
            print("Start the server with: uvicorn backend.app.main:app --reload")
            return

        # Run examples
        example_health_check()
        example_dataset_info()

        # These examples may fail if API keys are not configured
        try:
            example_virustotal_url_scan()
        except Exception as e:
            print(f"VirusTotal examples skipped: {e}")
            print("Set VIRUSTOTAL_API_KEY environment variable to enable.\n")

        example_network_threat_analysis()
        example_batch_analysis()

    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to API at http://localhost:8000")
        print("Make sure the API server is running:")
        print("  uvicorn backend.app.main:app --reload")
    except Exception as e:
        print(f"ERROR: {e}")


if __name__ == "__main__":
    main()
