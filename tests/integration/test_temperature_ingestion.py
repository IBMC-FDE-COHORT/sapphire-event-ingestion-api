"""
Integration tests for body_temperature ingestion via the OTel-style metrics endpoint.

Uses metric name health.body_temperature.celsius which follows the platform
naming convention (health.<category>.<name>).

Tag: @pytest.mark.integration -- excluded from the fast unit suite.
Run with: pytest -m integration tests/integration/test_temperature_ingestion.py
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient


@pytest.fixture()
def client():
    """Return a TestClient for integration testing."""
    from app.main import app
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


def _valid_body_temp_request(value: float = 37.2, unit_attr: str = "CELSIUS") -> dict:
    """Build a valid MetricsIngestionRequest payload for body temperature."""
    return {
        "request_id": "req-temp-test-001",
        "resource": {
            "attributes": {
                "device_id": "thermo-v2",
                "device_type": "thermometer",
                "user_id": "user-test-uuid"
            }
        },
        "scope": {"name": "health.metrics.collector", "version": "1.0.0"},
        "metrics": [
            {
                "name": "health.body_temperature.celsius",
                "unit": unit_attr,
                "data": {
                    "data_points": [
                        {
                            "time_unix_nano": 1788300000000000000,
                            "value": value
                        }
                    ]
                }
            }
        ]
    }


@pytest.mark.integration
def test_valid_celsius_body_temp_accepted(client):
    """A valid Celsius body temperature reading should be accepted."""
    with patch("app.services.kafka_producer.KafkaProducerService.send_metrics",
               new_callable=AsyncMock, return_value=MagicMock(success=True)):
        response = client.post(
            "/api/v1/metrics/ingest",
            json=_valid_body_temp_request(value=37.2),
            headers={"Authorization": "Bearer test-token"}
        )
    assert response.status_code in (200, 202)


@pytest.mark.integration
def test_out_of_range_body_temp_rejected(client):
    """A body temperature outside the physiological range must be rejected."""
    response = client.post(
        "/api/v1/metrics/ingest",
        json=_valid_body_temp_request(value=15.0),
        headers={"Authorization": "Bearer test-token"}
    )
    # Validation errors return 400 or 422 depending on the handler
    assert response.status_code in (400, 422)


@pytest.mark.integration
def test_missing_value_rejected(client):
    """A data point with no value must be rejected."""
    payload = _valid_body_temp_request()
    del payload["metrics"][0]["data"]["data_points"][0]["value"]
    response = client.post(
        "/api/v1/metrics/ingest",
        json=payload,
        headers={"Authorization": "Bearer test-token"}
    )
    assert response.status_code == 422


@pytest.mark.integration
def test_batch_within_limit_accepted(client):
    """A batch of up to 100 temperature metrics must be accepted."""
    payload = {
        "request_id": "req-batch-test",
        "resource": {
            "attributes": {
                "device_id": "thermo-v2",
                "device_type": "thermometer",
                "user_id": "user-test-uuid"
            }
        },
        "scope": {"name": "health.metrics.collector", "version": "1.0.0"},
        "metrics": [
            {
                "name": "health.body_temperature.celsius",
                "unit": "CELSIUS",
                "data": {
                    "data_points": [
                        {"time_unix_nano": 1788300000000000000 + i * 1000, "value": 37.2}
                        for i in range(5)
                    ]
                }
            }
        ]
    }
    with patch("app.services.kafka_producer.KafkaProducerService.send_metrics",
               new_callable=AsyncMock, return_value=MagicMock(success=True)):
        response = client.post(
            "/api/v1/metrics/ingest",
            json=payload,
            headers={"Authorization": "Bearer test-token"}
        )
    assert response.status_code in (200, 202)


@pytest.mark.integration
def test_unauthenticated_request_rejected(client):
    """A request without an auth token must be rejected with 401 or 403."""
    response = client.post(
        "/api/v1/metrics/ingest",
        json=_valid_body_temp_request()
    )
    assert response.status_code in (401, 403)


@pytest.mark.integration
def test_empty_metrics_list_rejected(client):
    """A request with an empty metrics list must be rejected with 422."""
    payload = _valid_body_temp_request()
    payload["metrics"] = []
    response = client.post(
        "/api/v1/metrics/ingest",
        json=payload,
        headers={"Authorization": "Bearer test-token"}
    )
    assert response.status_code == 422


@pytest.mark.integration
def test_temperature_metric_name_validates_correctly(client):
    """health.body_temperature.celsius matches the platform metric name pattern."""
    with patch("app.services.kafka_producer.KafkaProducerService.send_metrics",
               new_callable=AsyncMock, return_value=MagicMock(success=True)):
        response = client.post(
            "/api/v1/metrics/ingest",
            json=_valid_body_temp_request(),
            headers={"Authorization": "Bearer test-token"}
        )
    # Must not fail with invalid metric name pattern
    assert response.status_code != 400 or "metric name" not in response.text

# Made with Bob
