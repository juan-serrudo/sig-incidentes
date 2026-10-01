"""Expose the incident classifier API and local triage demonstration interface."""

import json
from contextlib import asynccontextmanager

import joblib
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.inference import classify_incident
from app.schemas import IncidentInput
from app.settings import ARTIFACT_DIR, CATEGORIES, FRONTEND_DIR, LABELS


@asynccontextmanager
async def lifespan(app):
    app.state.bundle = None
    app.state.report = None
    model_path = ARTIFACT_DIR / "model.joblib"
    report_path = ARTIFACT_DIR / "metrics.json"

    if model_path.exists() and report_path.exists():
        bundle = joblib.load(model_path)
        report = json.loads(report_path.read_text(encoding="utf-8"))
        if bundle["model_version"] != report["model_version"] or bundle["labels"] != LABELS:
            raise RuntimeError("Model, category definitions or report do not match. Retrain.")
        app.state.bundle, app.state.report = bundle, report
    yield


app = FastAPI(
    title="SIG-UOIT Incident Classifier",
    description="Sistema de clasificación automática de incidentes tecnológicos para la UOIT",
    version="1.0.0",
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.exception_handler(RequestValidationError)
async def invalid_input(request: Request, error: RequestValidationError):
    details = [
        {"loc": item["loc"], "msg": item["msg"], "type": item["type"]}
        for item in error.errors()
    ]
    return JSONResponse(status_code=422, content={"detail": details})


def require_model():
    if app.state.bundle is None:
        raise HTTPException(
            503, "Model unavailable. Generate data, train and restart the server."
        )
    return app.state.bundle


@app.get("/")
def home():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/api/health")
def health():
    return {
        "status": "ok" if app.state.bundle else "model_missing",
        "selected_model": app.state.bundle.get("model_name", "none") if app.state.bundle else None,
        "synthetic_data": True,
    }


@app.get("/api/categories")
def categories():
    return {
        "categories": CATEGORIES,
        "title_length": {"min": 5, "max": 200},
        "description_length": {"min": 15, "max": 2000},
    }


@app.get("/api/metrics")
def metrics():
    require_model()
    return app.state.report


@app.post("/api/classify")
def classify(incident: IncidentInput):
    return classify_incident(require_model(), incident.title, incident.initial_description)
