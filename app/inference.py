"""Inference service and explainability for operational incident triage."""

import time
import numpy as np

from app.baseline import rule_prediction
from app.settings import CATEGORIES


def classify_incident(bundle, title: str, initial_description: str):
    """Classify an incident using the real trained model, measuring real latency."""
    t0 = time.perf_counter()
    model = bundle["model"]
    features = model.named_steps["features"]
    classifier = model.named_steps["classifier"]

    combined_text = f"{title}. {initial_description}"
    probabilities = model.predict_proba([combined_text])[0]
    order = np.argsort(-probabilities)
    best_index = int(order[0])
    category = str(classifier.classes_[best_index])

    vector = features.transform([combined_text])
    try:
        word_vectorizer = dict(features.transformer_list)["word_tfidf"]
        word_vector = word_vectorizer.transform([combined_text])
        known_vocabulary = word_vector.nnz > 0
    except Exception:
        known_vocabulary = vector.nnz > 0

    score = float(probabilities[best_index])
    review_threshold = bundle.get("review_threshold", 0.5)
    needs_review = not known_vocabulary or score < review_threshold

    # Explainability: feature contributions to winning class
    try:
        terms = features.get_feature_names_out()
        weights = classifier.coef_[best_index]
        contributions = [
            (str(terms[index]).replace("word_tfidf__", "").replace("char_tfidf__", ""),
             float(value * weights[index]))
            for index, value in zip(vector.indices, vector.data)
            if value * weights[index] > 0
        ]
        contributions.sort(key=lambda item: item[1], reverse=True)
    except Exception:
        contributions = []

    reason = (
        "unknown_vocabulary"
        if not known_vocabulary
        else "below_threshold"
        if needs_review
        else "above_threshold"
    )

    ranking = [
        {
            "category": str(classifier.classes_[idx]),
            "name": CATEGORIES[str(classifier.classes_[idx])]["name"],
            "score": float(probabilities[idx]),
        }
        for idx in order
    ]

    latency_ms = round((time.perf_counter() - t0) * 1000, 2)

    return {
        "suggested_category": category,
        "category": category,
        "category_name": CATEGORIES[category]["name"],
        "score": score,
        "ranking": ranking,
        "top_3": ranking[:3],
        "requires_review": needs_review,
        "needs_review": needs_review,
        "review_reason": reason,
        "review_threshold": review_threshold,
        "signals": [
            {"term": term, "contribution": round(contrib, 4)}
            for term, contrib in contributions[:5]
        ],
        "baseline": rule_prediction(combined_text, bundle["baseline_fallback"]),
        "model": "TF-IDF (Palabras + Caracteres) + Regresión Logística (C=1.0)",
        "model_version": bundle.get("model_version", "uoit-v1"),
        "latency_ms": latency_ms,
        "synthetic_data": True,
    }


# Backward compatibility alias
def classify_message(bundle, message: str):
    return classify_incident(bundle, "Solicitud de soporte", message)
