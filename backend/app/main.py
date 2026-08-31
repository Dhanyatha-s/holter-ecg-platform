from fastapi import FastAPI

app = FastAPI(
    title="Holter ECG Analysis Platform API",
    version="0.1.0",
    description="Backend API for the on-premises Holter ECG analysis platform.",
)


@app.get("/health", tags=["system"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}
