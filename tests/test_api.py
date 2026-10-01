import numpy as np
import pytest
from fastapi.testclient import TestClient

from app import main

MESSAGE = "Mi usuario quedó bloqueado y no puedo iniciar sesión en el portal de trabajo."


@pytest.fixture
def client():
    with TestClient(main.app) as connection:
        yield connection


def test_api_matches_saved_pipeline_and_returns_five_ranked_categories(client):
    response = client.post("/api/classify", json={"message": MESSAGE})
    assert response.status_code == 200
    result = response.json()
    model = main.app.state.bundle["model"]
    assert result["category"] == model.predict([MESSAGE])[0]
    assert result["score"] == pytest.approx(model.predict_proba([MESSAGE])[0].max())
    assert len(result["ranking"]) == 5
    scores = [row["score"] for row in result["ranking"]]
    assert scores == sorted(scores, reverse=True)
    assert sum(scores) == pytest.approx(1)


@pytest.mark.parametrize("payload", [
    {}, {"message": "Corto"}, {"message": " " * 30}, {"message": "1" * 30},
    {"message": "x" * 2001}, {"message": 12345}, {"message": None},
    {"message": MESSAGE, "category": "access"}, {"message": MESSAGE, "resolution": "fixed"},
])
def test_invalid_or_leaking_inputs_are_rejected(client, payload):
    assert client.post("/api/classify", json=payload).status_code == 422


def test_unseen_vocabulary_requests_human_review(client):
    response = client.post("/api/classify", json={"message": "zxqvplm asdfghj qwertyzz klmnbvc"})
    assert response.status_code == 200
    assert response.json()["needs_review"] is True
    assert response.json()["review_reason"] == "unknown_vocabulary"


def test_signal_contributions_match_the_linear_model(client):
    result = client.post("/api/classify", json={"message": MESSAGE}).json()
    model = main.app.state.bundle["model"]
    vectorizer = model.named_steps["vectorizer"]
    classifier = model.named_steps["classifier"]
    vector = vectorizer.transform([MESSAGE])
    category_index = int(np.flatnonzero(classifier.classes_ == result["category"])[0])
    for signal in result["signals"]:
        index = vectorizer.vocabulary_[signal["term"]]
        assert signal["contribution"] == pytest.approx(float(vector[0, index] * classifier.coef_[category_index, index]))
        assert signal["contribution"] > 0


def test_public_assets_metadata_and_documentation(client):
    assert client.get("/").status_code == 200
    assert client.get("/static/app.js").status_code == 200
    assert client.get("/docs").status_code == 200
    assert len(client.get("/api/categories").json()["categories"]) == 5
    assert client.get("/api/health").json()["status"] == "ok"


def test_missing_model_still_serves_interface_but_returns_503(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "ARTIFACT_DIR", tmp_path)
    with TestClient(main.app) as connection:
        assert connection.get("/").status_code == 200
        assert connection.get("/api/metrics").status_code == 503
        assert connection.post("/api/classify", json={"message": MESSAGE}).status_code == 503
