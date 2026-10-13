# ECMO VA/VV Educational Rule Explorer

### [Open the Live Application →](https://abusuraihsakhri.github.io/ecmo-cannulation-va-vv-agent/)

A Python rules-engine demonstration and static browser exercise for exploring synthetic VA/VV ECMO scenarios. The repository includes several historical prototypes; their generic numeric thresholds are **not calibrated to real ECMO circuit measurements**.

**Not for clinical use.** This software does not calculate validated transmembrane pressure drop, recirculation fraction, cannulation eligibility, differential hypoxemia, or patient-specific treatment decisions. Do not submit identifiable patient data.

## Browser interface

Open [web/index.html](web/index.html) in a modern browser. The page compares the basic purposes of VA and VV ECMO and evaluates synthetic, unitless inputs against illustrative software thresholds.

- Works offline as static HTML, CSS, and JavaScript; no Python runtime, Pyodide, or server.
- No external API, model inference, analytics, persistent storage, or fabricated audit signatures.
- Runs local input validation and can export an example JSON file.
- Published as a GitHub Pages static application by the repository's deployment workflow; it does not expose the Python REST API. The initial GitHub Actions deployment completed successfully.

## Python installation

Requires Python 3.10 or later.

```bash
python -m pip install -e ".[api,test]"
python -m pytest -v
```

The default application is a synthetic three-worker rule engine. It has illustrative thresholds (**primary >25**, **secondary >12**), a caller-defined critical flag, and a descriptor string. These have no clinical units or guideline provenance.

```bash
# Main CLI; not a medical evaluation
ecmo-sentinel audit --task-id DEMO-001 --target SYNTH-01 --primary 28.5 --secondary 14.2
ecmo-sentinel chat "What does the demo do?"
ecmo-sentinel batch -i examples.csv -o results.csv
ecmo-sentinel verify-audit

# Alternatively, from the checked-out repository
python cli.py audit --task-id DEMO-001 --target SYNTH-01 --primary 28.5 --secondary 14.2
```

The root CLI's CSV columns are `task_id,target_identifier,primary_metric,secondary_metric,status_descriptor,is_critical_flag`. Boolean values accept `true`, `1`, or `yes`. Invalid rows are skipped with a warning; output CSV adds severity and audit fields.

The older `ecmo-cannulation-va-vv-engine` console entry point, `python -m ecmo_cannulation_va_vv_agent`, and `python ecmo_sentinel.py` use **different historical example schemas and thresholds**. They are maintained for compatibility and should not be compared as clinically equivalent algorithms.

## Development API

```bash
uvicorn agents.api:app --host 127.0.0.1 --port 8000
```

Endpoints: `GET /health`, `POST /api/audit`, `POST /api/chat`, `GET /metrics`, `GET /metrics/prometheus`, and `GET /api/audit/logs`. Interactive OpenAPI documentation is at `/docs`. An alternate API factory exists at `ecmo_cannulation_va_vv_agent.server.create_app` and has a different schema.

The API has **no user authentication or authorization**. Run locally or behind a separately configured access-control boundary; do not expose it directly to the public Internet.

## Privacy and audit limits

The browser exercise processes inputs only within the open tab and exports files on explicit request. The Python service retains evaluated synthetic dossiers and HMAC audit entries **in process memory**; restarting discards them. `AUDIT_SECRET_KEY` can provide a fixed signing key for that process. Without it, the application generates an ephemeral development key and emits a warning. Chain verification checks the HMAC of every entry and all predecessor links. This is not a persistent compliance-grade audit system.

The regex-based identifier filter blocks a limited set of recognizable identifiers, but **does not implement HIPAA Safe Harbor de-identification** and cannot guarantee PHI removal. Do not supply real patient records, names, contact information, or identifiers.

## Container

```bash
cp .env.example .env
# Replace AUDIT_SECRET_KEY with a strong random value in .env
docker compose up --build
```

The container runs the API on port 8000. The environment example is not a usable production secret.

## Technology and tests

Python, Pydantic 2, FastAPI (optional API extra), Uvicorn, pytest; standalone HTML/CSS/JavaScript. CI installs the Python package, checks dependency consistency, compiles source, and runs tests on Python 3.10–3.12. Browser exercise is compatible with modern desktop and mobile browsers; automated end-to-end browser deployment verification is not yet established.

## License

[MIT](LICENSE).
