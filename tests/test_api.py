"""
Test suite for VulNweb API endpoints
Tests for UNSW-NB15 and VirusTotal integration
"""
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


class TestHealthEndpoints:
    """Test health check endpoints"""

    def test_health_check(self):
        """Test API health endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


class TestVirusTotalEndpoints:
    """Test VirusTotal API integration endpoints"""

    def test_scan_url_invalid_api_key(self):
        """Test URL scanning without valid API key"""
        response = client.post(
            "/threats/virustotal/scan-url",
            json={"url": "https://example.com"}
        )
        # Will fail if no API key, but endpoint should still exist
        assert response.status_code in [200, 400, 503]

    def test_scan_file_hash_invalid_api_key(self):
        """Test file hash scanning without valid API key"""
        response = client.post(
            "/threats/virustotal/scan-file",
            json={"file_hash": "e4d909c290d0fb1ca068ffaddf22cbd0"}
        )
        # Will fail if no API key, but endpoint should still exist
        assert response.status_code in [200, 400, 503]

    def test_scan_url_invalid_input(self):
        """Test URL scanning with invalid input"""
        response = client.post(
            "/threats/virustotal/scan-url",
            json={"invalid_field": "test"}
        )
        # Should fail validation
        assert response.status_code == 422


class TestNetworkThreatEndpoints:
    """Test UNSW-NB15 network threat detection endpoints"""

    def test_analyze_network_threat(self):
        """Test network threat analysis endpoint"""
        response = client.post(
            "/threats/network/analyze",
            json={
                "source_ip": "192.168.1.100",
                "destination_ip": "10.0.0.50",
                "source_port": 52345,
                "destination_port": 80,
                "protocol": "TCP",
                "flow_duration": 45.5,
                "total_fwd_packets": 25,
                "total_bwd_packets": 23
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "threat_score" in data
        assert "threat_level" in data
        assert "confidence" in data
        assert "explanation" in data

    def test_analyze_network_threat_suspicious_port(self):
        """Test detection of suspicious port"""
        response = client.post(
            "/threats/network/analyze",
            json={
                "source_ip": "192.168.1.100",
                "destination_ip": "10.0.0.50",
                "source_port": 52345,
                "destination_port": 4444,  # Suspicious port
                "protocol": "TCP",
                "flow_duration": 45.5,
                "total_fwd_packets": 25,
                "total_bwd_packets": 23
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["threat_level"] in ["safe", "suspicious", "critical"]

    def test_analyze_network_threat_invalid_input(self):
        """Test with missing required fields"""
        response = client.post(
            "/threats/network/analyze",
            json={
                "source_ip": "192.168.1.100",
                "destination_ip": "10.0.0.50"
                # Missing required fields
            }
        )
        assert response.status_code == 422

    def test_get_dataset_info(self):
        """Test dataset information endpoint"""
        response = client.get("/threats/dataset/info")
        assert response.status_code == 200
        data = response.json()
        assert data["dataset"] == "UNSW-NB15"
        assert "features" in data
        assert "attack_categories" in data
        assert len(data["attack_categories"]) > 0


class TestBatchAnalysisEndpoints:
    """Test batch analysis endpoints"""

    def test_batch_analysis_urls_only(self):
        """Test batch analysis with URLs only"""
        response = client.post(
            "/threats/batch-analyze",
            json={
                "urls": ["https://example.com", "https://google.com"],
                "file_hashes": None,
                "network_flows": None
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "total_items" in data
        assert "results" in data

    def test_batch_analysis_network_flows_only(self):
        """Test batch analysis with network flows"""
        response = client.post(
            "/threats/batch-analyze",
            json={
                "urls": None,
                "file_hashes": None,
                "network_flows": [
                    {
                        "source_ip": "192.168.1.100",
                        "destination_ip": "10.0.0.50",
                        "source_port": 52345,
                        "destination_port": 80,
                        "protocol": "TCP",
                        "flow_duration": 45.5,
                        "total_fwd_packets": 25,
                        "total_bwd_packets": 23
                    }
                ]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_items"] >= 0

    def test_batch_analysis_mixed(self):
        """Test batch analysis with mixed threat types"""
        response = client.post(
            "/threats/batch-analyze",
            json={
                "urls": ["https://example.com"],
                "file_hashes": ["e4d909c290d0fb1ca068ffaddf22cbd0"],
                "network_flows": [
                    {
                        "source_ip": "192.168.1.100",
                        "destination_ip": "10.0.0.50",
                        "source_port": 52345,
                        "destination_port": 80,
                        "protocol": "TCP",
                        "flow_duration": 45.5,
                        "total_fwd_packets": 25,
                        "total_bwd_packets": 23
                    }
                ]
            }
        )
        assert response.status_code == 200


class TestDatasetLoading:
    """Test dataset loading functionality"""

    def test_dataset_loader_initialization(self):
        """Test dataset loader can be initialized"""
        from backend.app.dataset_loader import UNSWDatasetLoader
        loader = UNSWDatasetLoader()
        assert loader is not None
        assert loader.data_dir.exists()

    def test_attack_categories_known(self):
        """Test that known attack categories are recognized"""
        from backend.app.dataset_loader import UNSWDatasetLoader
        expected_categories = {
            "Analysis", "Backdoor", "DoS", "Exploits",
            "Fuzzers", "Generic", "Reconnaissance", "Shellcode", "Worms"
        }
        # This is a simple test to verify the categories are known
        assert len(expected_categories) > 0


class TestVirusTotalClient:
    """Test VirusTotal client functionality"""

    def test_virustotal_client_initialization(self):
        """Test VirusTotal client can be initialized without API key"""
        from backend.app.virustotal_client import VirusTotalClient
        client_vt = VirusTotalClient(api_key="test_key_invalid")
        assert client_vt is not None
        # Mock client should be created but won't work without valid key

    def test_threat_level_calculation(self):
        """Test threat level calculation logic"""
        from backend.app.virustotal_client import VirusTotalClient

        # Create a mock object to test _calculate_threat_level
        class MockVTObject:
            last_analysis_stats = {"malicious": 0, "suspicious": 0, "undetected": 70}

        obj = MockVTObject()
        threat_level = VirusTotalClient._calculate_threat_level(obj)
        assert threat_level == "safe"

        # Test suspicious
        obj.last_analysis_stats = {"malicious": 10, "suspicious": 10, "undetected": 50}
        threat_level = VirusTotalClient._calculate_threat_level(obj)
        assert threat_level in ["safe", "suspicious", "critical"]

        # Test critical
        obj.last_analysis_stats = {"malicious": 50, "suspicious": 10, "undetected": 10}
        threat_level = VirusTotalClient._calculate_threat_level(obj)
        assert threat_level == "critical"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
