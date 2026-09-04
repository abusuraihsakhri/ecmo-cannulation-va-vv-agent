# ECMO Cannulation Va Vv Agent

> **Domain:** Cardiovascular Medicine & Hemodynamic Analytics  
> **Reference Guidelines & Standards:** `AHA/ACC Practice Guidelines & ESC Clinical Standards`

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

**ECMO Cannulation Va Vv Agent** is an advanced analytical and computational platform implementing VA/VV ECMO Membrane Pressure Drop & Recirculation Tracker. It provides multi-agent consensus evaluation, cryptographic audit trails, and zero-PHI outbound protection for clinical decision support.

---

## ⚙️ Key Capabilities & Algorithmic Modules

### 🔬 Core Algorithmic & Evaluation Engines

- **`Severity`** — dedicated module for severity evaluation and state verification.
- **`DomainKnowledgeRegistry`**: Enterprise domain rules, guideline matrices, and evidence benchmarks.
- **`AgentAlert`** — dedicated module for agent alert evaluation and state verification.
- **`CircuitPressureMonitorAgent`**: Specialized Sub-Agent 1 for ecmo-cannulation-va-vv-agent
- **`GasExchangeEfficiencyAgent`**: Specialized Sub-Agent 2 for ecmo-cannulation-va-vv-agent
- **`RecirculationCalculatorAgent`**: Specialized Sub-Agent 3 for ecmo-cannulation-va-vv-agent

---

## 💻 CLI Quickstart & Usage

### Installation
```bash
pip install -e .
```

### 1. Run Single Audit
```bash
python cli.py audit --task-id TASK-001 --target KEY-01 --primary 28.5 --secondary 14.2
```

### 2. Chat with Supervisor
```bash
python cli.py chat "What is the system status?"
```

### 3. Batch Process CSV
```bash
python cli.py batch -i sample.csv -o results.csv
```

### 4. Verify Audit Trail
```bash
python cli.py verify-audit
```

### 5. Launch REST API Server
```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

### Parameter Reference
- `--task-id`: Unique task/case identifier
- `--target`: Target entity or specimen identifier
- `--primary`: Primary measurement value (float)
- `--secondary`: Secondary measurement value (float)
- `--critical`: Flag for emergency escalation
- `--status`: Status descriptor (e.g., NOMINAL, DISCORDANT)

### Input Data Schema

| Field | Description | Requirement |
|:------|:------------|:------------|
| `case_id` | Parameter / observation metric | Required |
| `patient_synthetic_id` | Parameter / observation metric | Required |
| `metric_primary` | Parameter / observation metric | Required |
| `metric_secondary` | Parameter / observation metric | Required |
| `is_stat` | Parameter / observation metric | Required |
| `status_flag` | Parameter / observation metric | Required |

---

## 🛡️ Security & Enterprise Architecture

* **Zero-PHI Outbound Interceptor:** Active regex inspection blocking SSNs, MRNs, phone numbers, and patient identifiers.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation and state transition.
* **Air-Gapped LLM Reasoning Adapter:** Agnostic integration for local Ollama instances (`llama3`, `mistral`), Claude 3.5 Sonnet, GPT-4o, and deterministic test mocks.
* **Active Learning Bayesian Calibration:** Dynamic tracker updating worker reliability weights and monitoring Brier calibration drift.
* **FastAPI & Prometheus Telemetry:** Exposes OpenAPI 3.1 REST endpoints and operational Prometheus metrics (`/metrics` and `/metrics/prometheus`).

### Security Configuration

Set a strong random key for production:
```bash
# Copy the example env file
cp .env.example .env

# Generate a strong key
python -c "import secrets; print(secrets.token_hex(32))"

# Edit .env and set AUDIT_SECRET_KEY
```

---

## 🧪 Testing & Verification

Run the automated test suite:

```bash
pytest -v
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py 1000
```

---

## 🐳 Container Deployment

### Docker
```bash
docker build -t ecmo-cannulation-va-vv-agent .
docker run -p 8000:8000 -e AUDIT_SECRET_KEY=your-secret-key ecmo-cannulation-va-vv-agent
```

### Docker Compose
```bash
# Copy and configure environment
cp .env.example .env
# Edit .env with your AUDIT_SECRET_KEY

# Launch
docker-compose up -d
```

---

## 📁 Project Structure

```
ecmo-cannulation-va-vv-agent/
├── agents/                    # Core agent package
│   ├── api.py                 # FastAPI REST server
│   ├── base.py                # Security, PHI guard, audit trail
│   ├── models.py              # Pydantic data models
│   ├── supervisor.py          # Multi-agent orchestrator
│   ├── workers.py             # Specialized evaluation workers
│   ├── metrics.py             # Prometheus metrics collector
│   ├── learning.py            # Bayesian calibration engine
│   ├── llm_factory.py         # LLM provider factory
│   └── streamer.py            # WebSocket telemetry broadcaster
├── ecmo_cannulation_va_vv_agent/  # Clinical agent package
│   ├── agents.py              # Clinical coordinator & sub-agents
│   ├── engine.py              # Clinical algorithmic engine
│   ├── models.py              # Clinical data models
│   ├── server.py              # FastAPI server factory
│   └── cli.py                 # Clinical CLI
├── tests/                     # Test suite
├── cli.py                     # Main CLI entry point
├── ecmo_sentinel.py           # Standalone ECMO sentinel module
├── simulator.py               # High-throughput simulation
├── enrichment.py              # Domain enrichment engines
├── web/index.html             # Operations console
├── Dockerfile                 # Container build
├── docker-compose.yml         # Container orchestration
└── pyproject.toml             # Project configuration
```
