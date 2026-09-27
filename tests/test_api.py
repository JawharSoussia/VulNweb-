"""API contract tests for frozen /api namespace."""
from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_health_endpoint_shape():
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert "status" in body
    assert body["status"] in {"healthy", "degraded"}
    assert "model_loaded" in body
    assert "version" in body


def test_api_status_endpoint():
    response = client.get("/api/status")
    assert response.status_code == 200
    assert response.json() == {"status": "operational"}


def test_api_endpoints_contract_route():
    response = client.get("/api/endpoints")
    assert response.status_code == 200
    body = response.json()
    assert body["namespace"] == "/api"
    assert "POST /api/predict" in body["endpoints"]
    assert "POST /api/predict-raw" in body["endpoints"]


def test_features_contract():
    response = client.get("/api/features")
    assert response.status_code == 200
    body = response.json()
    assert body["feature_count"] == 34
    assert len(body["features"]) == 34


def test_predict_raw_invalid_length():
    response = client.post("/api/predict-raw", json={"features": [1.0, 2.0, 3.0]})
    assert response.status_code in {400, 503}
    if response.status_code == 400:
        assert "Expected 34 features" in response.json()["detail"]


def test_feedback_contract():
    payload = {
        "request_id": "req_test_123",
        "is_correct": True,
        "comments": "contract test"
    }
    response = client.post("/api/feedback", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "accepted"
    assert "feedback_id" in body
