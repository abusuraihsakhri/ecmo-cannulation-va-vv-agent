"""
FastAPI REST API Server for Ecmo Cannulation Va Vv Agent.
"""
import time
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from .base import AuditLogger, PHIGuard, SecurityException
from .models import SystemTaskPayload, ConsensusDossier
from .supervisor import SystemSupervisor
from .metrics import GLOBAL_METRICS

supervisor = SystemSupervisor(model_provider="mock")

app = FastAPI(
    title="Ecmo Cannulation Va Vv Agent API",
    description="Enterprise Distributed Component Platform (Cardiology & Intensive Care Systems)",
    version="3.0.0-ENTERPRISE",
)


class ChatRequest(BaseModel):
    query: str


@app.get("/health")
def health():
    return {"status": "HEALTHY", "service": "ecmo-cannulation-va-vv-agent", "domain": "Cardiology & Intensive Care Systems", "standard": "AHA/ACC Guidelines / Surviving Sepsis Campaign", "version": "3.0.0-ENTERPRISE"}


@app.get("/metrics")
def metrics_json():
    return {
        "dossiers_processed_total": len(supervisor.dossier_registry),
        "audit_blocks_total": len(AuditLogger.get_trail()),
        "system_status": "NOMINAL_OPTIMAL"
    }


@app.get("/metrics/prometheus", response_class=PlainTextResponse)
def metrics_prometheus():
    return GLOBAL_METRICS.export_prometheus_text()


@app.post("/api/audit")
def api_audit(payload: SystemTaskPayload):
    start = time.time()
    try:
        dossier = supervisor.process_task(payload)
        GLOBAL_METRICS.record_task(dossier.overall_urgency.value, time.time() - start)
        return dossier.to_dict()
    except SecurityException as e:
        GLOBAL_METRICS.record_phi_block()
        raise HTTPException(status_code=422, detail=str(e))


@app.post("/api/chat")
def api_chat(req: ChatRequest):
    try:
        ans = supervisor.query_supervisory_chat(req.query)
        return {"response": ans}
    except SecurityException as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/audit/logs")
def api_audit_logs():
    return {"audit_trail": AuditLogger.get_trail(), "verified": AuditLogger.verify_integrity()}
