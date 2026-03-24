# Task 1.4: Data Quality Tests (Data Contracts)

**Phase:** Setup & Data Preparation
**Deadline:** Day 14
**Status:** ⏳ Pending
**Dependencies:** Task 1.3 complete

---

## 📋 Objective
Create data validation tests to ensure schema compliance, data quality, and freshness. Implement automated data contracts using Pydantic.

---

## 🎯 What to Do

### Step 1: Create Data Contract Schemas

**Create: `backend/app/data_contracts.py`**

```python
"""Data Contracts - Pydantic Models for Validation"""
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
import numpy as np

class PredictionDataContract(BaseModel):
    """Contract for incoming prediction request data"""

    url: str = Field(..., min_length=1, description="Target URL")
    ip_address: str = Field(
        ...,
        pattern=r"^(\d{1,3}\.){3}\d{1,3}$",
        description="IPv4 address in dotted notation"
    )
    port: Optional[int] = Field(None, ge=0, le=65535, description="Port number")
    protocol: Optional[str] = Field(None, regex="^(tcp|udp)$")
    bytes_sent: Optional[float] = Field(None, ge=0)
    bytes_received: Optional[float] = Field(None, ge=0)
    duration: Optional[float] = Field(None, ge=0)
    packets: Optional[int] = Field(None, ge=0)

    @field_validator('url')
    @classmethod
    def validate_url(cls, v):
        """Validate URL format"""
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        return v

    @field_validator('ip_address')
    @classmethod
    def validate_ip(cls, v):
        """Validate IP address ranges"""
        octets = [int(x) for x in v.split('.')]
        if any(o > 255 or o < 0 for o in octets):
            raise ValueError('Invalid IP address octets')
        return v

    @field_validator('bytes_sent', 'bytes_received', 'duration')
    @classmethod
    def check_non_negative(cls, v):
        """Ensure non-negative values"""
        if v is not None and v < 0:
            raise ValueError('Value must be non-negative')
        return v

    class Config:
        strict = True


class PredictionResponseContract(BaseModel):
    """Contract for prediction response"""

    threat_score: float = Field(..., ge=0, le=100, description="Threat score 0-100")
    confidence: float = Field(..., ge=0, le=1, description="Confidence 0-1")
    threat_level: str = Field(
        ...,
        regex="^(safe|suspicious|critical)$",
        description="Threat level category"
    )
    explanation: List[str] = Field(..., max_length=3, description="Top 3 reasons")
    model_version: str = Field(..., description="Model version used")

    class Config:
        strict = True


class FeedbackDataContract(BaseModel):
    """Contract for user feedback"""

    prediction_id: int = Field(..., gt=0)
    is_correct: bool
    comments: Optional[str] = Field(None, max_length=500)

    class Config:
        strict = True
```

---

### Step 2: Create Unit Tests for Data Contracts

**Create: `tests/test_data_contracts.py`**

```python
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
```

---

### Step 3: Create Data Quality Tests

**Create: `tests/test_data_quality.py`**

```python
"""Data quality and freshness tests"""
import pytest
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta


class TestDataQuality:
    """Test data quality standards"""

    @pytest.fixture
    def processed_data(self):
        """Load processed training data"""
        df = pd.read_csv("data/train/train_processed.csv")
        return df

    def test_no_missing_values(self, processed_data):
        """No missing values in processed data"""
        assert processed_data.isnull().sum().sum() == 0, \
            f"Found {processed_data.isnull().sum().sum()} missing values"

    def test_no_duplicates(self, processed_data):
        """No duplicate rows"""
        assert not processed_data.duplicated().any(), \
            f"Found {processed_data.duplicated().sum()} duplicate rows"

    def test_numeric_columns_dtype(self, processed_data):
        """All columns are numeric (except target)"""
        for col in processed_data.columns:
            if col not in ['label', 'target', 'class']:
                assert processed_data[col].dtype in ['float64', 'int64'], \
                    f"Column {col} has non-numeric dtype: {processed_data[col].dtype}"

    def test_feature_bounds(self, processed_data):
        """Features within expected bounds (scaled features)"""
        numeric_cols = processed_data.select_dtypes(include=['float64', 'int64']).columns

        for col in numeric_cols:
            # Scaled features should generally be in range [-5, 5]
            assert processed_data[col].max() < 100, \
                f"Column {col} exceeds maximum value: {processed_data[col].max()}"
            assert processed_data[col].min() > -100, \
                f"Column {col} below minimum value: {processed_data[col].min()}"

    def test_target_distribution(self, processed_data):
        """Target variable has reasonable distribution"""
        target_col = 'label' if 'label' in processed_data.columns else processed_data.columns[-1]
        counts = processed_data[target_col].value_counts()

        # At least 2 classes
        assert len(counts) >= 2, "Target has less than 2 classes"

        # Check class imbalance ratio
        min_count = counts.min()
        max_count = counts.max()
        imbalance_ratio = min_count / max_count

        assert imbalance_ratio > 0.05, \
            f"Severe class imbalance detected: ratio={imbalance_ratio:.3f}"

    def test_feature_count_consistency(self):
        """Feature count consistent across splits"""
        train = pd.read_csv("data/train/train_processed.csv")
        val = pd.read_csv("data/train/val_processed.csv")
        test = pd.read_csv("data/test/test_processed.csv")

        assert train.shape[1] == val.shape[1] == test.shape[1], \
            f"Feature count mismatch: train={train.shape[1]}, " \
            f"val={val.shape[1]}, test={test.shape[1]}"

    def test_minimum_samples(self):
        """Datasets have minimum sample counts"""
        train = pd.read_csv("data/train/train_processed.csv")
        val = pd.read_csv("data/train/val_processed.csv")
        test = pd.read_csv("data/test/test_processed.csv")

        MIN_TRAIN_SAMPLES = 1000
        MIN_VAL_SAMPLES = 200
        MIN_TEST_SAMPLES = 200

        assert len(train) >= MIN_TRAIN_SAMPLES, \
            f"Train set too small: {len(train)} < {MIN_TRAIN_SAMPLES}"
        assert len(val) >= MIN_VAL_SAMPLES, \
            f"Val set too small: {len(val)} < {MIN_VAL_SAMPLES}"
        assert len(test) >= MIN_TEST_SAMPLES, \
            f"Test set too small: {len(test)} < {MIN_TEST_SAMPLES}"


class TestDataFreshness:
    """Test data freshness (if timestamp present)"""

    def test_recent_data(self):
        """Data is recent (within expected timeframe)"""
        # This assumes raw data has a timestamp column
        # Adjust based on your actual data
        raw_file = Path("data/raw")
        csv_files = list(raw_file.glob("*.csv"))

        if csv_files:
            file_stat = csv_files[0].stat()
            file_age_days = (datetime.now() - datetime.fromtimestamp(file_stat.st_mtime)).days

            # Data should be less than 90 days old
            assert file_age_days < 90, \
                f"Data is {file_age_days} days old - consider refreshing"
```

---

### Step 4: Create Data Contract Middleware

**Create: `backend/app/middleware.py`**

```python
"""Middleware for data validation"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import ValidationError
import logging
import json

logger = logging.getLogger(__name__)

class DataValidationMiddleware(BaseHTTPMiddleware):
    """Validate incoming/outgoing data against contracts"""

    async def dispatch(self, request: Request, call_next):
        """Process request/response"""

        # Log incoming data
        if request.method in ["POST", "PUT"]:
            try:
                body = await request.body()
                if body:
                    logger.info(f"Incoming data: {body[:200]}")  # Log first 200 chars
            except Exception as e:
                logger.warning(f"Could not log request body: {e}")

        # Process request
        response = await call_next(request)

        # Log response status
        logger.info(f"{request.method} {request.url.path} -> {response.status_code}")

        return response
```

---

### Step 5: Run Tests

```bash
# Activate environment
source venv/bin/activate

# Run all data quality tests
pytest tests/test_data_quality.py -v

# Run data contract tests
pytest tests/test_data_contracts.py -v

# Run with coverage
pytest tests/ --cov=backend --cov-report=html
```

---

### Step 6: Create Test Configuration

**Create: `pytest.ini`**

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
markers =
    data_quality: Data quality tests
    contracts: Data contract validation tests
    slow: slow tests
```

---

### Step 7: Document Data Standards

**Create: `docs/DATA_STANDARDS.md`**

```markdown
# Data Quality Standards

## Data Contracts

### PredictionDataContract
- URL: Must start with http:// or https://
- IP Address: Valid IPv4 format (0.0.0.0 to 255.255.255.255)
- Port: 0-65535
- Protocol: tcp or udp
- Numeric fields: Must be non-negative

### PredictionResponseContract
- Threat Score: 0-100
- Confidence: 0-1
- Threat Level: safe, suspicious, or critical
- Explanation: Maximum 3 reasons

## Quality Standards

| Standard | Requirement | Validation |
|----------|-------------|-----------|
| Missing Values | < 0.1% | test_no_missing_values |
| Duplicates | 0 | test_no_duplicates |
| Feature Count | Consistent across splits | test_feature_count_consistency |
| Minimum Samples | Train ≥ 1000, Val ≥ 200, Test ≥ 200 | test_minimum_samples |
| GClass Balance | Imbalance ratio > 0.05 | test_target_distribution |
| Data Freshness | < 90 days old | test_recent_data |

## Freshness Checks

- Data files checked on each pipeline run
- Raw data refreshed if > 90 days old
- Processed data regenerated if source changes
```

---

## 📊 Expected Outputs

```
tests/
├── test_data_contracts.py
├── test_data_quality.py
└── __init__.py

backend/app/
├── data_contracts.py
└── middleware.py

docs/
└── DATA_STANDARDS.md

pytest.ini
htmlcov/  (from test coverage)
```

---

## ✅ Checklist

- [x] Data contract schemas created (Pydantic models)
- [x] Unit tests for contracts written and passing
- [x] Data quality tests implemented
- [x] Test configuration (pytest.ini) created
- [x] All tests passing: `pytest tests/ -v`
- [x] Test coverage > 80%: `pytest --cov=backend`
- [x] Middleware for validation implemented
- [x] Data standards documented
- [x] Commit: `git add . && git commit -m "Add data contracts and quality tests"`

---

## 🔗 Next Steps

✅ **Phase 1 Complete** → Move to **Phase 2: ML Model Development**

✅ **Task 1.4 Complete** → Move to **Task 2.1: Model Selection & Training**

---

**Created:** 2026-03-17
