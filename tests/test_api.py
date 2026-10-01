import pytest
from fastapi.testclient import TestClient

from app import main

VALID_TITLE = "Agotamiento del pool de conexiones en base de datos PostgreSQL"
VALID_DESC = (
    "Alerta de monitoreo Zabbix: El cluster PostgreSQL alcanzo el limite max_connections "
    "y las aplicaciones no pueden abrir nuevas sesiones. Se solicita intervencion de la guardia tecnica."
)


@pytest.fixture
def client():
    with TestClient(main.app) as connection:
        yield connection


def test_api_classifies_valid_incident_and_returns_ranking_and_latency(client):
    payload = {"title": VALID_TITLE, "initial_description": VALID_DESC}
    response = client.post("/api/classify", json=payload)
    assert response.status_code == 200
    result = response.json()

    assert "suggested_category" in result
    assert result["suggested_category"] in main.app.state.bundle["labels"]
    assert "ranking" in result
    assert len(result["ranking"]) == 5

    scores = [row["score"] for row in result["ranking"]]
    assert scores == sorted(scores, reverse=True)
    assert sum(scores) == pytest.approx(1.0, abs=1e-3)

    assert "top_3" in result
    assert len(result["top_3"]) == 3
    assert result["top_3"][0]["category"] == result["suggested_category"]

    assert "latency_ms" in result
    assert result["latency_ms"] >= 0
    assert "model" in result
    assert "TF-IDF" in result["model"]


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"title": VALID_TITLE},
        {"initial_description": VALID_DESC},
        {"title": "Abc", "initial_description": VALID_DESC},  # title too short (<5)
        {"title": VALID_TITLE, "initial_description": "Corto"},  # desc too short (<15)
        {"title": "   ", "initial_description": VALID_DESC},
        {"title": VALID_TITLE, "initial_description": "   " * 10},
        {"title": "12345", "initial_description": VALID_DESC},  # title without enough letters
        {"title": VALID_TITLE, "initial_description": "1" * 30},  # desc without enough letters
        {"title": VALID_TITLE, "initial_description": "x" * 2001},  # exceeds max_length
        # Forbidden fields causing data leakage:
        {"title": VALID_TITLE, "initial_description": VALID_DESC, "category": "databases"},
        {"title": VALID_TITLE, "initial_description": VALID_DESC, "resolution": "reiniciado"},
        {"title": VALID_TITLE, "initial_description": VALID_DESC, "root_cause": "pool agotado"},
        {"title": VALID_TITLE, "initial_description": VALID_DESC, "assignee": "operador_guardia"},
        {"title": VALID_TITLE, "initial_description": VALID_DESC, "closing_text": "cerrado con exito"},
        {"title": VALID_TITLE, "initial_description": VALID_DESC, "solution": "ampliar max_connections"},
        {"title": VALID_TITLE, "initial_description": VALID_DESC, "final_assignment": "area_dba"},
    ],
)
def test_invalid_or_leaking_inputs_are_rejected(client, payload):
    response = client.post("/api/classify", json=payload)
    assert response.status_code == 422


def test_unseen_vocabulary_requests_human_review(client):
    payload = {
        "title": "zxqvplm asdfghj",
        "initial_description": "qwertyzz klmnbvc poiuytrew asdfghjk zxcvbnmlk",
    }
    response = client.post("/api/classify", json=payload)
    assert response.status_code == 200
    result = response.json()
    assert result["requires_review"] is True
    assert result["review_reason"] == "unknown_vocabulary"


def test_public_assets_metadata_and_documentation(client):
    assert client.get("/").status_code == 200
    assert client.get("/static/app.js").status_code == 200
    assert client.get("/docs").status_code == 200
    cats_resp = client.get("/api/categories").json()
    assert len(cats_resp["categories"]) == 5
    assert client.get("/api/health").json()["status"] == "ok"


def test_missing_model_still_serves_interface_but_returns_503(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "ARTIFACT_DIR", tmp_path)
    with TestClient(main.app) as connection:
        assert connection.get("/").status_code == 200
        assert connection.get("/api/metrics").status_code == 503
        assert (
            connection.post(
                "/api/classify",
                json={"title": VALID_TITLE, "initial_description": VALID_DESC},
            ).status_code
            == 503
        )
