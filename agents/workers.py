"""
Specialized Domain Worker Agents for Ecmo Cannulation Va Vv Agent.
Domain: Cardiology & Intensive Care Systems
Standard: AHA/ACC Guidelines / Surviving Sepsis Campaign
"""
import uuid
from typing import Dict, Any, List, Optional
from .models import SystemTaskPayload, AgentAlert, UrgencyLevel, SystemIntegrityStatus


class InvariantQCWorker:
    """Worker 1: Primary Mathematical & Protocol Boundary Auditor."""

    @classmethod
    def evaluate(cls, payload: SystemTaskPayload) -> List[AgentAlert]:
        alerts = []
        if payload.primary_metric > 25.0:
            alerts.append(AgentAlert(
                alert_id=f"QC-{uuid.uuid4().hex[:6]}",
                origin_worker="InvariantQCWorker",
                urgency=UrgencyLevel.ELEVATED,
                summary="Primary Metric Threshold Exceeded",
                technical_details=f"Primary measurement ({payload.primary_metric:.2f}) exceeds upper reference limit (25.00) under an illustrative, unvalidated threshold.",
                actionable_remediation="Review the synthetic inputs; this threshold is not a clinical action limit.",
            ))
        return alerts


class SafetyEscalationWorker:
    """Worker 2: Safety Boundary, Toxicity & Emergency Interlock Worker."""

    @classmethod
    def evaluate(cls, payload: SystemTaskPayload) -> List[AgentAlert]:
        alerts = []
        if payload.is_critical_flag or payload.secondary_metric > 12.0:
            alerts.append(AgentAlert(
                alert_id=f"SAFE-{uuid.uuid4().hex[:6]}",
                origin_worker="SafetyEscalationWorker",
                urgency=UrgencyLevel.CRITICAL_STAT if payload.is_critical_flag else UrgencyLevel.ELEVATED,
                summary="Critical Safety Interlock Triggered",
                technical_details=f"CriticalFlag={payload.is_critical_flag} with secondary index {payload.secondary_metric:.2f}.",
                actionable_remediation="Illustrative flag only. Do not use this output for clinical escalation.",
            ))
        return alerts


class ProtocolConformanceWorker:
    """Worker 3: Spec Conformance, Anomaly Triage & Discordance Checker."""

    @classmethod
    def evaluate(cls, payload: SystemTaskPayload) -> List[AgentAlert]:
        alerts = []
        desc_upper = str(payload.status_descriptor).upper()
        if any(w in desc_upper for w in ["DISCORDANT", "ANOMALY", "MUTANT", "VIOLATION", "FAIL", "REJECT"]):
            alerts.append(AgentAlert(
                alert_id=f"CONF-{uuid.uuid4().hex[:6]}",
                origin_worker="ProtocolConformanceWorker",
                urgency=UrgencyLevel.ELEVATED,
                summary="Protocol Conformance Discordance Detected",
                technical_details=f"Descriptor '{payload.status_descriptor}' indicates discordance with the selected demonstration flags.",
                actionable_remediation="Review the synthetic descriptor; no clinical inference is made.",
            ))
        return alerts
