"""Unit tests for data contracts and validation"""
import pytest
from pydantic import ValidationError
from backend.app.data_contracts import (
    PredictionDataContract,
    PredictionResponseContract,
    FeedbackDataContract
)


class TestPredictionDataContract:
    """Test incoming prediction data validation"""

    def test_valid_prediction_request(self):
        """Valid prediction request passes"""
        data = {
            "url": "https://example.com",
            "ip_address": "192.168.1.1",
            "port": 443,
            "protocol": "tcp"
        }
        contract = PredictionDataContract(**data)
        assert contract.url == "https://example.com"
        assert contract.ip_address == "192.168.1.1"

    def test_invalid_url_format(self):
        """Invalid URL format fails"""
        data = {
            "url": "example.com",  # Missing protocol
            "ip_address": "192.168.1.1"
        }
        with pytest.raises(ValidationError):
            PredictionDataContract(**data)

    def test_invalid_ip_address(self):
        """Invalid IP address fails"""
        data = {
            "url": "https://example.com",
            "ip_address": "256.256.256.256"  # Out of range
        }
        with pytest.raises(ValidationError):
            PredictionDataContract(**data)

    def test_invalid_ip_format(self):
        """Invalid IP format fails"""
        data = {
            "url": "https://example.com",
            "ip_address": "192.168.1"  # Incomplete
        }
        with pytest.raises(ValidationError):
            PredictionDataContract(**data)

    def test_negative_bytes_rejected(self):
        """Negative bytes values rejected"""
        data = {
            "url": "https://example.com",
            "ip_address": "192.168.1.1",
            "bytes_sent": -100
        }
        with pytest.raises(ValidationError):
            PredictionDataContract(**data)

    def test_port_range_validation(self):
        """Port number validation"""
        # Valid port
        data = {
            "url": "https://example.com",
            "ip_address": "192.168.1.1",
            "port": 8080
        }
        contract = PredictionDataContract(**data)
        assert contract.port == 8080

        # Invalid port (too high)
        data['port'] = 70000
        with pytest.raises(ValidationError):
            PredictionDataContract(**data)


class TestPredictionResponseContract:
    """Test prediction response validation"""

    def test_valid_response(self):
        """Valid response passes"""
        data = {
            "threat_score": 75.5,
            "confidence": 0.92,
            "threat_level": "suspicious",
            "explanation": ["High entropy domain", "Known malware signature"],
            "model_version": "v1.0"
        }
        response = PredictionResponseContract(**data)
        assert response.threat_score == 75.5
        assert response.threat_level == "suspicious"

    def test_threat_score_range(self):
        """Threat score must be 0-100"""
        data = {
            "threat_score": 150,  # Out of range
            "confidence": 0.92,
            "threat_level": "critical",
            "explanation": ["Test"],
            "model_version": "v1.0"
        }
        with pytest.raises(ValidationError):
            PredictionResponseContract(**data)

    def test_confidence_range(self):
        """Confidence must be 0-1"""
        data = {
            "threat_score": 50,
            "confidence": 1.5,  # Out of range
            "threat_level": "suspicious",
            "explanation": ["Test"],
            "model_version": "v1.0"
        }
        with pytest.raises(ValidationError):
            PredictionResponseContract(**data)

    def test_threat_level_enum(self):
        """Threat level must be valid category"""
        data = {
            "threat_score": 50,
            "confidence": 0.92,
            "threat_level": "unknown",  # Invalid
            "explanation": ["Test"],
            "model_version": "v1.0"
        }
        with pytest.raises(ValidationError):
            PredictionResponseContract(**data)

    def test_explanation_max_length(self):
        """Explanation limited to 3 items"""
        data = {
            "threat_score": 50,
            "confidence": 0.92,
            "threat_level": "suspicious",
            "explanation": ["Reason 1", "Reason 2", "Reason 3", "Reason 4"],  # Too many
            "model_version": "v1.0"
        }
        with pytest.raises(ValidationError):
            PredictionResponseContract(**data)


class TestFeedbackDataContract:
    """Test feedback data validation"""

    def test_valid_feedback(self):
        """Valid feedback passes"""
        data = {
            "prediction_id": 123,
            "is_correct": True,
            "comments": "This was correctly identified as safe"
        }
        feedback = FeedbackDataContract(**data)
        assert feedback.prediction_id == 123
        assert feedback.is_correct is True

    def test_missing_required_field(self):
        """Missing required field fails"""
        data = {
            "is_correct": True
            # Missing prediction_id
        }
        with pytest.raises(ValidationError):
            FeedbackDataContract(**data)

    def test_invalid_prediction_id(self):
        """Invalid prediction ID fails"""
        data = {
            "prediction_id": 0,  # Must be > 0
            "is_correct": True
        }
        with pytest.raises(ValidationError):
            FeedbackDataContract(**data)