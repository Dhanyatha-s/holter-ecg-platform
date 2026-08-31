# Backend

FastAPI backend for the Holter ECG Analysis Platform.

## Local development

From `backend/`:

```bash
python -m venv .venv
```

Activate the virtual environment, install dependencies, then run:

```bash
uvicorn app.main:app --reload
```

The initial health endpoint is available at `/health`.
