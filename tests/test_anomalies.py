
from src.anomaly_service import (
    detect_priority_anomalies,
    detect_resolution_anomalies,
)


def test_resolution_anomalies():
    anomalies = detect_resolution_anomalies()

    assert not anomalies.empty
    assert "anomaly_type" in anomalies.columns


def test_priority_anomalies():
    anomalies = detect_priority_anomalies()

    assert not anomalies.empty
    assert "anomaly_type" in anomalies.columns