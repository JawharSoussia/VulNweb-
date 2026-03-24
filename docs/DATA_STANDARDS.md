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