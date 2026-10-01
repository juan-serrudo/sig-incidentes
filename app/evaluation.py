"""Evaluate all requests, then separately report the review policy's coverage."""

import numpy as np
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_recall_fscore_support

from app.settings import LABELS, MIN_ACCEPTED_ACCURACY, MIN_ACCEPTED_CASES


def classification_metrics(actual, predicted):
    precision, recall, f1, support = precision_recall_fscore_support(actual, predicted, labels=LABELS, zero_division=0)
    return {
        "macro_f1": float(f1_score(actual, predicted, labels=LABELS, average="macro", zero_division=0)),
        "weighted_f1": float(f1_score(actual, predicted, labels=LABELS, average="weighted", zero_division=0)),
        "accuracy": float(accuracy_score(actual, predicted)),
        "confusion_matrix": confusion_matrix(actual, predicted, labels=LABELS).tolist(),
        "by_category": [{"category": label, "precision": float(precision[index]), "recall": float(recall[index]), "f1": float(f1[index]), "support": int(support[index])} for index, label in enumerate(LABELS)],
    }


def review_metrics(actual, probabilities, classes, threshold, known_vocabulary):
    scores = probabilities.max(axis=1)
    predicted = np.asarray(classes)[probabilities.argmax(axis=1)]
    accepted = (scores >= threshold) & np.asarray(known_vocabulary)
    accepted_count = int(accepted.sum())
    return {
        "coverage": float(accepted.mean()), "accepted_count": accepted_count,
        "review_count": int(len(actual) - accepted_count),
        "accepted_accuracy": float(np.mean(predicted[accepted] == np.asarray(actual)[accepted])) if accepted_count else None,
    }


def choose_review_threshold(actual, probabilities, classes, known_vocabulary):
    """Maximize validation coverage while meeting a teaching accuracy target."""
    for threshold in np.unique(probabilities.max(axis=1)):
        result = review_metrics(actual, probabilities, classes, float(threshold), known_vocabulary)
        if result["accepted_count"] >= MIN_ACCEPTED_CASES and result["accepted_accuracy"] >= MIN_ACCEPTED_ACCURACY:
            return float(threshold)
    return 1.000001  # No supported threshold: request human review for every message.

