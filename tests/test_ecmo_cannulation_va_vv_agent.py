"""
Automated Pytest Test Suite for Ecmo Cannulation Va Vv Agent.
Domain: Cardiology & Intensive Care Systems
Standard: AHA/ACC Guidelines / Surviving Sepsis Campaign
"""
import os
import sys
import tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from agents.base import PHIGuard, AuditLogger, SecurityException, AuditTrail
from agents.models import SystemTaskPayload, UrgencyLevel, SystemIntegrityStatus
from agents.workers import InvariantQCWorker, SafetyEscalationWorker, ProtocolConformanceWorker
from agents.supervisor import SystemSupervisor
from cli import main


def test_phi_guard_enforcement():
    with pytest.raises(SecurityException):
        PHIGuard.assert_no_phi("Patient MRN-994827 blood culture positive for Staphylococcus")

    # Clean text passes
    PHIGuard.assert_no_phi("Analytical assay specimen KEY-001 optimal")


def test_phi_guard_redaction():
    text = "Contact patient at 555-123-4567 or test@example.com"
    redacted = PHIGuard.redact_phi(text)
    assert "555-123-4567" not in redacted
    assert "test@example.com" not in redacted
    assert "[REDACTED_IDENTIFIER]" in redacted


def test_specialized_workers():
    # Worker 1: QC Invariant
    p1 = SystemTaskPayload(task_id="T1", target_identifier="KEY-01", primary_metric=35.0)
    alerts1 = InvariantQCWorker.evaluate(p1)
    assert len(alerts1) == 1
    assert alerts1[0].urgency == UrgencyLevel.ELEVATED

    # Worker 2: Safety
    p2 = SystemTaskPayload(task_id="T2", target_identifier="KEY-02", primary_metric=10.0, is_critical_flag=True)
    alerts2 = SafetyEscalationWorker.evaluate(p2)
    assert len(alerts2) == 1
    assert alerts2[0].urgency == UrgencyLevel.CRITICAL_STAT

    # Worker 3: Protocol Conformance
    p3 = SystemTaskPayload(task_id="T3", target_identifier="KEY-03", primary_metric=10.0, status_descriptor="DISCORDANT_ANOMALY")
    alerts3 = ProtocolConformanceWorker.evaluate(p3)
    assert len(alerts3) == 1


def test_supervisor_consensus_and_audit():
    supervisor = SystemSupervisor(model_provider="mock")
    payload = SystemTaskPayload(
        task_id="TASK-PROD-01",
        target_identifier="KEY-PROD-01",
        primary_metric=12.0,
        secondary_metric=4.0,
        status_descriptor="NOMINAL"
    )
    dossier = supervisor.process_task(payload)
    assert dossier.overall_urgency == UrgencyLevel.ROUTINE
    assert dossier.integrity_status == SystemIntegrityStatus.VALIDATED
    assert dossier.audit_hash != ""

    # Verify cryptographic audit trail
    assert AuditLogger.verify_integrity() is True

    # CLI tests
    assert main(["audit", "--task-id", "CLI-TEST-01"]) == 0
    assert main(["chat", "Explain", "specifications"]) == 0
    assert main(["verify-audit"]) == 0


def test_batch_csv_processing():
    """Test batch CSV processing with valid input."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
        f.write("task_id,target_identifier,primary_metric,secondary_metric,status_descriptor,is_critical_flag\n")
        f.write("TASK-BATCH-01,TARGET-B01,15.0,5.0,NOMINAL,false\n")
        f.write("TASK-BATCH-02,TARGET-B02,35.0,15.0,DISCORDANT,true\n")
        input_path = f.name

    output_path = input_path + "_output.csv"
    try:
        result = main(["batch", "-i", input_path, "-o", output_path])
        assert result == 0
        assert os.path.exists(output_path)
        with open(output_path, 'r') as f:
            content = f.read()
            assert "TASK-BATCH-01" in content
            assert "TASK-BATCH-02" in content
    finally:
        os.unlink(input_path)
        if os.path.exists(output_path):
            os.unlink(output_path)


def test_batch_csv_missing_file():
    """Test batch CSV processing with missing input file."""
    result = main(["batch", "-i", "nonexistent_file_xyz.csv"])
    assert result == 1


def test_audit_trail_integrity():
    """Test that audit trail maintains cryptographic integrity."""
    trail = AuditLogger.get_trail()
    if len(trail) > 1:
        for i in range(1, len(trail)):
            assert trail[i]["prev_hash"] == trail[i-1]["current_hash"]
    assert AuditLogger.verify_integrity() is True


def test_audit_trail_with_custom_key():
    """Test AuditTrail with a custom secret key."""
    custom_trail = AuditTrail(secret_key="test-secret-key-12345")
    entry = custom_trail.log("test_actor", "test_tier", "TEST_EVENT", {"key": "value"})
    assert entry["current_hash"] != ""
    assert entry["prev_hash"] == "GENESIS_BLOCK_0000000000000000"
    assert custom_trail.verify_integrity() is True


def test_supervisor_phi_rejection():
    """Test that supervisor rejects PHI-containing task IDs."""
    supervisor = SystemSupervisor(model_provider="mock")
    payload = SystemTaskPayload(
        task_id="Patient John Doe MRN-12345",
        target_identifier="KEY-01",
        primary_metric=10.0,
    )
    with pytest.raises(SecurityException):
        supervisor.process_task(payload)
