import json

import joblib
import numpy as np
import pandas as pd
import pytest

from app.baseline import rule_prediction
from app.evaluation import choose_review_threshold, classification_metrics, review_metrics, top_k_accuracy
from app.linear_baseline import prepare_incident_text
from app.settings import ARTIFACT_DIR, DATA_DIR, LABELS


def test_keyword_rules_use_uoit_keywords_and_fallback():
    assert (
        rule_prediction("El pool de conexiones de la base de datos esta saturado", "applications_services")["category"]
        == "databases"
    )
    assert (
        rule_prediction("El switch de red WAN no responde al enrutamiento", "applications_services")["category"]
        == "networks_connectivity"
    )
    assert (
        rule_prediction("El certificado SSL institucional de seguridad expiro anoche", "applications_services")["category"]
        == "security_access"
    )
    assert (
        rule_prediction("Quisiera una receta de cocina vegetariana", "applications_services")["used_fallback"]
        is True
    )


def test_metrics_include_all_five_categories_and_top_k():
    metrics = classification_metrics(LABELS, LABELS)
    assert metrics["macro_f1"] == 1.0
    assert metrics["accuracy"] == 1.0
    assert np.trace(metrics["confusion_matrix"]) == 5

    # Test Top-3 accuracy
    probs = np.array([
        [0.7, 0.2, 0.1, 0.0, 0.0],
        [0.1, 0.6, 0.2, 0.0, 0.1],
    ])
    classes = np.array(LABELS)
    actual = [LABELS[0], LABELS[2]]  # first is top-1, second is in top-3
    assert top_k_accuracy(actual, probs, classes, k=3) == 1.0


def test_review_threshold_maximizes_supported_coverage():
    labels = np.array(["databases"] * 40)
    probabilities = np.array([[0.9, 0.1]] * 20 + [[0.4, 0.6]] * 20)
    classes = np.array(["databases", "networks_connectivity"])
    threshold = choose_review_threshold(labels, probabilities, classes, [True] * 40)
    result = review_metrics(labels, probabilities, classes, threshold, [True] * 40)
    assert threshold == 0.9
    assert result["accepted_count"] == 20
    assert result["accepted_accuracy"] == 1.0


def test_no_threshold_can_be_reported_without_enough_correct_cases():
    probabilities = np.array([[0.1, 0.9]] * 30)
    threshold = choose_review_threshold(["databases"] * 30, probabilities, ["databases", "networks_connectivity"], [True] * 30)
    assert threshold > 1.0
    result = review_metrics(["databases"] * 30, probabilities, ["databases", "networks_connectivity"], threshold, [True] * 30)
    assert result["coverage"] == 0.0
    assert result["accepted_accuracy"] is None


def test_unknown_vocabulary_is_reviewed_even_with_high_scores():
    result = review_metrics(["databases"], np.array([[0.99, 0.01]]), ["databases", "networks_connectivity"], 0.5, [False])
    assert result["accepted_count"] == 0


def test_saved_report_matches_predictions_for_every_test_incident():
    bundle = joblib.load(ARTIFACT_DIR / "model.joblib")
    report = json.loads((ARTIFACT_DIR / "metrics.json").read_text(encoding="utf-8"))
    test = pd.read_csv(DATA_DIR / "test.csv")
    test_texts = prepare_incident_text(test)

    predictions = bundle["model"].predict(test_texts)
    probabilities = bundle["model"].predict_proba(test_texts)
    metrics = classification_metrics(test.category, predictions, probabilities, bundle["model"].classes_)

    assert metrics["macro_f1"] == pytest.approx(report["test"]["linear_baseline"]["macro_f1"], abs=1e-4)
    assert metrics["accuracy"] == pytest.approx(report["test"]["linear_baseline"]["accuracy"], abs=1e-4)
    assert sum(sum(row) for row in metrics["confusion_matrix"]) == len(test)
    assert len(test) == 180


def test_selected_operational_model_is_linear_baseline_by_validation_decision():
    report = json.loads((ARTIFACT_DIR / "metrics.json").read_text(encoding="utf-8"))
    assert report["selected_model"] == "linear_baseline"
    b_val = report["validation"]["linear_baseline"]["macro_f1"]
    t_val = report["validation"]["proposed_transformer"]["macro_f1"]
    assert b_val >= t_val  # Verified selection rule
