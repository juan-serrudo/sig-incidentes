import json

import joblib
import numpy as np
import pandas as pd
import pytest

from app.baseline import rule_prediction
from app.evaluation import choose_review_threshold, classification_metrics, review_metrics
from app.settings import ARTIFACT_DIR, DATA_DIR, LABELS


def test_keyword_rules_use_whole_words_and_a_visible_fallback():
    assert rule_prediction("La contraseña de mi usuario no funciona", "access")["category"] == "access"
    assert rule_prediction("El buzón no recibe correo", "access")["category"] == "email"
    assert rule_prediction("Necesito una receta de cocina", "access")["used_fallback"] is True
    assert rule_prediction("La firmawarex es diferente", "access")["used_fallback"] is True


def test_metrics_include_all_five_categories():
    metrics = classification_metrics(LABELS, LABELS)
    assert metrics["macro_f1"] == 1
    assert metrics["accuracy"] == 1
    assert np.trace(metrics["confusion_matrix"]) == 5


def test_review_threshold_maximizes_supported_coverage():
    labels = np.array(["access"] * 40)
    probabilities = np.array([[0.9, 0.1]] * 20 + [[0.4, 0.6]] * 20)
    classes = np.array(["access", "email"])
    threshold = choose_review_threshold(labels, probabilities, classes, [True] * 40)
    result = review_metrics(labels, probabilities, classes, threshold, [True] * 40)
    assert threshold == 0.9
    assert result["accepted_count"] == 20
    assert result["accepted_accuracy"] == 1


def test_no_threshold_can_be_reported_without_enough_correct_cases():
    probabilities = np.array([[0.1, 0.9]] * 30)
    threshold = choose_review_threshold(["access"] * 30, probabilities, ["access", "email"], [True] * 30)
    assert threshold > 1
    result = review_metrics(["access"] * 30, probabilities, ["access", "email"], threshold, [True] * 30)
    assert result["coverage"] == 0
    assert result["accepted_accuracy"] is None


def test_unknown_vocabulary_is_reviewed_even_with_high_scores():
    result = review_metrics(["access"], np.array([[0.99, 0.01]]), ["access", "email"], 0.5, [False])
    assert result["accepted_count"] == 0


def test_saved_report_matches_predictions_for_every_test_message():
    bundle = joblib.load(ARTIFACT_DIR / "model.joblib")
    report = json.loads((ARTIFACT_DIR / "metrics.json").read_text())
    test = pd.read_csv(DATA_DIR / "test.csv")
    metrics = classification_metrics(test.category, bundle["model"].predict(test.message))
    assert metrics == report["test"]["model"]
    assert sum(sum(row) for row in metrics["confusion_matrix"]) == len(test)


def test_inference_does_not_learn_a_new_vocabulary():
    bundle = joblib.load(ARTIFACT_DIR / "model.joblib")
    vectorizer = bundle["model"].named_steps["vectorizer"]
    vocabulary = vectorizer.vocabulary_.copy()
    bundle["model"].predict(["zxqvplm asdfghj qwertyzz"])
    assert vectorizer.vocabulary_ == vocabulary
    assert "zxqvplm" not in vectorizer.vocabulary_


def test_model_configuration_and_threshold_follow_validation():
    report = json.loads((ARTIFACT_DIR / "metrics.json").read_text())
    selected = max(report["validation"]["candidates"], key=lambda item: (item["macro_f1"], -item["c"]))
    assert report["selected_c"] == selected["c"]
    policy = report["validation"]["review_policy"]
    if report["review_threshold"] <= 1:
        assert policy["accepted_accuracy"] >= report["target_accepted_accuracy"]
        assert policy["accepted_count"] >= report["minimum_accepted_cases"]

