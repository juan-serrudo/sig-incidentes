"""Expose a read-only classifier and the local teaching interface."""

import json
from contextlib import asynccontextmanager

import joblib
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.inference import classify_message
from app.schemas import TicketInput
from app.settings import ARTIFACT_DIR, CATEGORIES, FRONTEND_DIR, LABELS


@asynccontextmanager
async def lifespan(app):
    app.state.bundle = None
    app.state.report = None
    model_path, report_path = ARTIFACT_DIR / "model.joblib", ARTIFACT_DIR / "metrics.json"
    if model_path.exists() and report_path.exists():
        bundle = joblib.load(model_path)  # Only load this project's trusted local artifact.
        report = json.loads(report_path.read_text(encoding="utf-8"))
        if bundle["model_version"] != report["model_version"] or bundle["labels"] != LABELS:
            raise RuntimeError("Model, category definitions or report do not match. Retrain.")
        app.state.bundle, app.state.report = bundle, report
    yield


app = FastAPI(title="Support Triage Demo", version="1.0.0", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.exception_handler(RequestValidationError)
async def invalid_input(request: Request, error: RequestValidationError):
    details = [{"loc": item["loc"], "msg": item["msg"], "type": item["type"]} for item in error.errors()]
    return JSONResponse(status_code=422, content={"detail": details})


def require_model():
    if app.state.bundle is None:
        raise HTTPException(503, "Model unavailable. Generate data, train and restart the server.")
    return app.state.bundle


@app.get("/")
def home():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/api/health")
def health():
    return {"status": "ok" if app.state.bundle else "model_missing", "synthetic_data": True}


@app.get("/api/categories")
def categories():
    return {"categories": CATEGORIES, "minimum_length": 20, "maximum_length": 2000}


@app.get("/api/metrics")
def metrics():
    require_model()
    return app.state.report


@app.post("/api/classify")
def classify(ticket: TicketInput):
    return classify_message(require_model(), ticket.message)

