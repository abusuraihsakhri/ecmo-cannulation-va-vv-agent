"""Regression coverage for audit integrity, finite values, and synthetic-input safety."""
import math

import pytest
from pydantic import ValidationError

from agents.base import AuditTrail, PHIGuard, SecurityException
from agents.models import SystemTaskPayload
from agents.supervisor import SystemSupervisor
from ecmo_cannulation_va_vv_agent.cli import parse_boolean
from ecmo_cannulation_va_vv_agent.models import ClinicalCasePayload


@pytest.mark.parametrize("field", ["actor", "timestamp", "event_type", "payload_hash", "current_hash"])
def test_audit_detects_tampered_signed_fields(field):
    trail = AuditTrail(secret_key="test-integrity-key")
    trail.log("demo", "supervisor", "SIMULATED", {"status": "OK"})
    assert trail.verify_integrity()
    trail.logs[0][field] = "TAMPERED"
    assert not trail.verify_integrity()


def test_audit_detects_broken_middle_chain():
    trail = AuditTrail(secret_key="test-integrity-key")
    for _ in range(3):
        trail.log("demo", "supervisor", "SIMULATED", {"status": "OK"})
    assert trail.verify_integrity()
    trail.logs[1]["prev_hash"] = "another-value"
    assert not trail.verify_integrity()


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf])
def test_nonfinite_metrics_rejected(value):
    with pytest.raises(ValidationError):
        SystemTaskPayload(task_id="TASK-01", target_identifier="DEMO-01", primary_metric=value)
    with pytest.raises(ValueError):
        ClinicalCasePayload("CASE-01", "SYNTH-01", 1.0, value, "NOMINAL")


def test_empty_ids_are_rejected():
    with pytest.raises(ValidationError):
        SystemTaskPayload(task_id="", target_identifier="DEMO-01", primary_metric=2.0)


def test_metadata_identifier_is_blocked():
    supervisor = SystemSupervisor()
    payload = SystemTaskPayload(
        task_id="TASK-01", target_identifier="DEMO-01", primary_metric=2.0,
        attributes={"comment": "Contact 555-123-4567"}
    )
    with pytest.raises(SecurityException):
        supervisor.process_task(payload)


@pytest.mark.parametrize("value,expected", [
    ("False", False), ("0", False), ("No", False), ("", False),
    ("True", True), ("1", True), ("yes", True)
])
def test_csv_boolean_parser(value, expected):
    assert parse_boolean(value) is expected


def test_csv_boolean_parser_rejects_ambiguous_values():
    with pytest.raises(ValueError):
        parse_boolean("sometimes")


def test_api_rejects_invalid_numeric_inputs():
    from fastapi.testclient import TestClient
    from agents.api import app
    client = TestClient(app)
    response = client.post("/api/audit", json={
        "task_id": "DEMO-01", "target_identifier": "SYNTH-01", "primary_metric": "nan"
    })
    assert response.status_code == 422
