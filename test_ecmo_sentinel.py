import os
import tempfile
import pytest
from ecmo_sentinel import CircuitPressureMonitorAgent, GasExchangeEfficiencyAgent, RecirculationCalculatorAgent, ECMOCoordinator, Severity, main


def test_sub_agents():
    a1 = CircuitPressureMonitorAgent()
    alerts1 = a1.evaluate({"metric_primary": 35.0})
    assert len(alerts1) == 1

    a2 = GasExchangeEfficiencyAgent()
    alerts2 = a2.evaluate({"critical_flag": True})
    assert len(alerts2) == 1

    a3 = RecirculationCalculatorAgent()
    alerts3 = a3.evaluate({"status_text": "DISCORDANT_FINDING"})
    assert len(alerts3) == 1


def test_severity_enum():
    """Test that Severity is a proper Enum."""
    assert Severity.INFO.value == "INFO"
    assert Severity.ADVISORY.value == "ADVISORY"
    assert Severity.WARNING.value == "WARNING"
    assert Severity.CRITICAL.value == "CRITICAL_ACTION_REQUIRED"


def test_coordinator():
    coord = ECMOCoordinator()
    dossier = coord.audit_case({"case_id": "TEST-100", "metric_primary": 10.0, "metric_secondary": 2.0})
    assert dossier["overall_status"] == "CONCORDANT_NORMAL"
    assert dossier["total_alerts"] == 0

    ans = coord.query_assistant("What are the guidelines?")
    assert "guidelines" in ans or "standards" in ans


def test_coordinator_critical():
    """Test coordinator with critical flag."""
    coord = ECMOCoordinator()
    dossier = coord.audit_case({"case_id": "TEST-CRIT", "metric_primary": 30.0, "metric_secondary": 15.0, "critical_flag": True, "status_text": "DISCORDANT"})
    assert dossier["overall_status"] == "CRITICAL_ACTION_REQUIRED"
    assert dossier["total_alerts"] >= 2


def test_cli():
    assert main(["audit", "--case-id", "CLI-01"]) == 0
    assert main(["chat", "What", "is", "the", "system", "status?"]) == 0


def test_domain_registry():
    from ecmo_sentinel import DomainKnowledgeRegistry
    assert DomainKnowledgeRegistry.ZERO_PHI_COMPLIANCE is True
    assert "PRO" in DomainKnowledgeRegistry.SYSTEM_VERSION


def test_batch_csv_processing():
    """Test batch CSV processing with valid input."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
        f.write("case_id,patient_synthetic_id,metric_primary,metric_secondary,is_stat,status_flag\n")
        f.write("CASE-B01,SYNTH-B01,15.0,5.0,False,NORMAL\n")
        f.write("CASE-B02,SYNTH-B02,35.0,15.0,True,DISCORDANT\n")
        input_path = f.name

    output_path = input_path + "_output.csv"
    try:
        result = main(["batch", "-i", input_path, "-o", output_path])
        assert result == 0
        assert os.path.exists(output_path)
        with open(output_path, 'r') as f:
            content = f.read()
            assert "CASE-B01" in content
            assert "CASE-B02" in content
    finally:
        os.unlink(input_path)
        if os.path.exists(output_path):
            os.unlink(output_path)


def test_batch_csv_missing_file():
    """Test batch CSV processing with missing input file."""
    result = main(["batch", "-i", "nonexistent_file_xyz.csv"])
    assert result == 1


def test_domain_knowledge_registry_security():
    """Test DomainKnowledgeRegistry security audit."""
    from ecmo_sentinel import DomainKnowledgeRegistry
    warnings = DomainKnowledgeRegistry.audit_security_and_integrity({"patient_name": "John Doe", "safe_key": "value"})
    assert len(warnings) >= 1
    assert "PHI_DEFENSE_TRIGGERED" in warnings[0]
