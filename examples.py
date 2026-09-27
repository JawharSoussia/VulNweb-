"""
VulNweb API Usage Examples (frozen /api contract)
"""

import json
from typing import Any, Dict, List

import requests

BASE_URL = "http://localhost:8000"


class VulNwebClient:
    """Client for interacting with VulNweb API."""

    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()

    def health_check(self) -> Dict[str, Any]:
        return self.session.get(f"{self.base_url}/health").json()

    def status(self) -> Dict[str, Any]:
        return self.session.get(f"{self.base_url}/api/status").json()

    def get_features(self) -> Dict[str, Any]:
        return self.session.get(f"{self.base_url}/api/features").json()

    def get_model_info(self) -> Dict[str, Any]:
        return self.session.get(f"{self.base_url}/api/model-info").json()

    def predict_url(self, url: str) -> Dict[str, Any]:
        return self.session.post(
            f"{self.base_url}/api/predict",
            json={"url": url}
        ).json()

    def predict_raw(self, features: List[float]) -> Dict[str, Any]:
        return self.session.post(
            f"{self.base_url}/api/predict-raw",
            json={"features": features}
        ).json()

    def predict_batch(self, urls: List[str]) -> Dict[str, Any]:
        return self.session.post(
            f"{self.base_url}/api/predict-batch",
            json={"urls": urls}
        ).json()

    def submit_feedback(self, request_id: str, is_correct: bool, comments: str = "") -> Dict[str, Any]:
        return self.session.post(
            f"{self.base_url}/api/feedback",
            json={
                "request_id": request_id,
                "is_correct": is_correct,
                "comments": comments
            }
        ).json()


def print_section(title: str):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def main():
    client = VulNwebClient()

    print_section("Health")
    health = client.health_check()
    print(json.dumps(health, indent=2))
    if health.get("status") not in {"healthy", "degraded"}:
        print("API is not reachable or healthy enough to continue.")
        return

    print_section("API Status + Metadata")
    print(json.dumps(client.status(), indent=2))
    print(json.dumps(client.get_model_info(), indent=2))
    print(json.dumps(client.get_features(), indent=2))

    print_section("URL Prediction")
    url_result = client.predict_url("https://example.com/login")
    print(json.dumps(url_result, indent=2))

    print_section("Raw Feature Prediction")
    raw_features = [5, 443, 64, 0, 2, 1, 10, 20, 1, 5, 0, 0, 0, 0, 1, 10, 0, 1, 0, 100, 0.1, 0.2, 50, 100, 0, 64, 100, 2.5, 0.8, 1024, 0.1, 2048, 1.5, 256]
    raw_result = client.predict_raw(raw_features)
    print(json.dumps(raw_result, indent=2))

    print_section("Batch Prediction")
    batch_result = client.predict_batch([
        "https://www.google.com",
        "https://example.com/download?file=test.exe"
    ])
    print(json.dumps(batch_result, indent=2))

    print_section("Feedback")
    request_id = url_result.get("request_id") or raw_result.get("request_id") or "req_example"
    feedback_result = client.submit_feedback(
        request_id=request_id,
        is_correct=True,
        comments="Example feedback from API usage script"
    )
    print(json.dumps(feedback_result, indent=2))


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to API at http://localhost:8000")
        print("Start with: uvicorn backend.app.main:app --reload")
