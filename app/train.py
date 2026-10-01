"""Train text pipelines, choose on family-held-out validation, evaluate once on test."""

import hashlib
import json
import platform
from importlib.metadata import version

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from app.baseline import rule_prediction
from app.data import split_by_family, validate_tickets
from app.evaluation import choose_review_threshold, classification_metrics, review_metrics
from app.settings import ARTIFACT_DIR, CATEGORIES, DATA_DIR, LABELS, MIN_ACCEPTED_ACCURACY, MIN_ACCEPTED_CASES, SEED


def build_model(regularization_c):
    return Pipeline([
        ("vectorizer", TfidfVectorizer(lowercase=True, strip_accents="unicode", ngram_range=(1, 2), min_df=2, sublinear_tf=True, max_features=8000)),
        ("classifier", LogisticRegression(C=regularization_c, class_weight="balanced", max_iter=1000, random_state=SEED)),
    ])


def describe_split(part):
    return {"rows": len(part), "families": int(part.family_id.nunique()), "by_category": {label: int(part.category.eq(label).sum()) for label in LABELS}}


def write_report(report):
    model, baseline = report["test"]["model"], report["test"]["baseline"]
    lines = [
        "# Resultados del experimento", "",
        "Clasificación de solicitudes iniciales en cinco categorías. Datos sintéticos en español; las cifras no prueban utilidad en una mesa de ayuda real.", "",
        "## Datos separados por familia", "", "| Partición | Mensajes | Familias |", "|---|---:|---:|",
    ]
    for name, split in report["splits"].items():
        lines.append(f"| {name} | {split['rows']} | {split['families']} |")
    lines += ["", "Las dos paráfrasis y todas las variantes de una familia permanecen en la misma partición. Se comprueban duplicados normalizados. El vocabulario se aprende solo con entrenamiento.", "", "## Selección en validación", "", "| C | Macro-F1 |", "|---|---:|"]
    for candidate in report["validation"]["candidates"]:
        lines.append(f"| {candidate['c']} | {candidate['macro_f1']:.4f} |")
    lines += ["", f"C elegido: **{report['selected_c']}**. Umbral de revisión: **{report['review_threshold']:.6f}**.", "", "## Prueba sobre todos los mensajes", "", "| Métrica | Reglas por palabras | TF-IDF + regresión logística |", "|---|---:|---:|"]
    for key, title in [("macro_f1", "Macro-F1"), ("weighted_f1", "F1 ponderado"), ("accuracy", "Exactitud")]:
        lines.append(f"| {title} | {baseline[key]:.4f} | {model[key]:.4f} |")
    verdict = "Las reglas superan al modelo en Macro-F1. Este experimento no justifica sustituirlas por el modelo; conviene ampliar la diversidad de datos y reservar una prueba nueva antes de otra comparación." if baseline["macro_f1"] >= model["macro_f1"] else "El modelo supera a las reglas en Macro-F1 sobre esta simulación. Se necesita una evaluación con datos reales antes de recomendar su uso operativo."
    lines += ["", verdict]
    lines += ["", "### Desempeño del modelo por categoría", "", "| Categoría | Precisión | Recall | F1 | Casos |", "|---|---:|---:|---:|---:|"]
    for row in model["by_category"]:
        lines.append(f"| {CATEGORIES[row['category']]['name']} | {row['precision']:.3f} | {row['recall']:.3f} | {row['f1']:.3f} | {row['support']} |")
    lines += ["", "### Matriz de confusión", "", "Filas = categoría real; columnas = predicción. Orden: " + ", ".join(LABELS) + ".", "", "| Real / predicha | " + " | ".join(LABELS) + " |", "|---|" + "---:|" * len(LABELS)]
    for label, row in zip(LABELS, model["confusion_matrix"]):
        lines.append(f"| {label} | " + " | ".join(str(value) for value in row) + " |")
    policy = report["test"]["review_policy"]
    accepted_accuracy = f"{policy['accepted_accuracy']:.1%}" if policy["accepted_accuracy"] is not None else "no definida (ningún caso supera el criterio)"
    lines += [
        "", "## Política de revisión, medida por separado", "",
        f"En validación se buscó máxima cobertura con exactitud de al menos {MIN_ACCEPTED_ACCURACY:.0%} en un mínimo de {MIN_ACCEPTED_CASES} mensajes que superaran el umbral.",
        f"En prueba, cobertura: **{policy['coverage']:.1%}** ({policy['accepted_count']} mensajes); revisión marcada: **{policy['review_count']}**; exactitud entre los que superan el criterio: **{accepted_accuracy}**.",
        "El subconjunto de prueba no alcanza el objetivo de exactitud de validación." if policy["accepted_accuracy"] is not None and policy["accepted_accuracy"] < MIN_ACCEPTED_ACCURACY else "La política se informa sin modificar el umbral con los resultados de prueba.",
        "El Macro-F1 anterior incluye todos los mensajes, incluso los marcados para revisión. No se ocultan los casos difíciles para mejorar esa métrica.",
        "El objetivo de validación no garantiza la misma exactitud en prueba ni en producción. Los puntajes no se calibraron como probabilidades de acierto.",
        "", "## Límites", "",
        "El texto proviene de 60 familias redactadas para la simulación. Hay lenguaje compartido entre familias; esta separación es más exigente que mezclar variantes, pero no representa conversaciones reales ni una evaluación temporal.",
        "La prueba contiene solo dos familias por categoría. No se estiman intervalos de confianza; las variantes de una familia no son observaciones independientes.",
        "El modelo siempre ordena las cinco categorías conocidas. Un puntaje alto no garantiza detectar un tema externo, una negación o varias intenciones. La revisión por puntaje es una ayuda limitada.",
        "Los términos destacados son aportes positivos al puntaje lineal de la clase elegida; no explican causalidad ni representan toda la comparación entre clases.",
        "La aplicación no crea tickets ni asigna equipos de forma automática. No mide tiempos de resolución, satisfacción o reducción de trabajo real.",
        "", "## Reproducibilidad", "", f"Semilla: {SEED}. SHA-256: `{report['dataset_sha256']}`.", f"Versiones: `{report['versions']}`.",
    ]
    (ARTIFACT_DIR / "evaluation.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    source = DATA_DIR / "tickets.csv"
    if not source.exists():
        raise SystemExit("Run python -m app.data first.")
    data = pd.read_csv(source)
    validate_tickets(data)
    train, validation, test = split_by_family(data)
    fallback = str(train.category.value_counts().idxmax())
    candidates, models = [], []
    for regularization_c in [1.0, 4.0]:
        model = build_model(regularization_c)
        model.fit(train.message, train.category)
        metrics = classification_metrics(validation.category, model.predict(validation.message))
        candidates.append({"c": regularization_c, "macro_f1": metrics["macro_f1"]})
        models.append(model)
    best_index = max(range(len(candidates)), key=lambda index: (candidates[index]["macro_f1"], -candidates[index]["c"]))
    model = models[best_index]
    classes = model.named_steps["classifier"].classes_
    validation_probabilities = model.predict_proba(validation.message)
    validation_known = model.named_steps["vectorizer"].transform(validation.message).getnnz(axis=1) > 0
    threshold = choose_review_threshold(validation.category, validation_probabilities, classes, validation_known)

    # Freeze both the model and review threshold before reading test results.
    test_probabilities = model.predict_proba(test.message)
    predictions = classes[test_probabilities.argmax(axis=1)]
    test_known = model.named_steps["vectorizer"].transform(test.message).getnnz(axis=1) > 0
    baseline_predictions = [rule_prediction(message, fallback)["category"] for message in test.message]
    dataset_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    model_version = f"text-v1-{dataset_hash[:8]}"
    report = {
        "synthetic_data": True, "seed": SEED, "dataset_sha256": dataset_hash, "model_version": model_version,
        "labels": LABELS, "categories": CATEGORIES, "selected_c": candidates[best_index]["c"],
        "review_threshold": threshold, "target_accepted_accuracy": MIN_ACCEPTED_ACCURACY, "minimum_accepted_cases": MIN_ACCEPTED_CASES,
        "baseline_fallback": fallback, "vocabulary_size": len(model.named_steps["vectorizer"].vocabulary_),
        "versions": {"python": platform.python_version(), **{name: version(name) for name in ["scikit-learn", "pandas", "numpy", "fastapi"]}},
        "splits": {name: describe_split(part) for name, part in [("train", train), ("validation", validation), ("test", test)]},
        "validation": {"candidates": candidates, "review_policy": review_metrics(validation.category, validation_probabilities, classes, threshold, validation_known)},
        "test": {"model": classification_metrics(test.category, predictions), "baseline": classification_metrics(test.category, baseline_predictions), "review_policy": review_metrics(test.category, test_probabilities, classes, threshold, test_known)},
    }
    ARTIFACT_DIR.mkdir(exist_ok=True)
    joblib.dump({"model": model, "review_threshold": threshold, "baseline_fallback": fallback, "model_version": model_version, "labels": LABELS}, ARTIFACT_DIR / "model.joblib")
    (ARTIFACT_DIR / "metrics.json").write_text(json.dumps(report, indent=2, allow_nan=False, ensure_ascii=False) + "\n", encoding="utf-8")
    for name, part in [("train", train), ("validation", validation), ("test", test)]:
        part.to_csv(DATA_DIR / f"{name}.csv", index=False)
    results = test[["ticket_id", "family_id", "message", "category"]].copy()
    results["model_prediction"] = predictions
    results["baseline_prediction"] = baseline_predictions
    results["score"] = test_probabilities.max(axis=1)
    results["needs_review"] = (results.score < threshold) | ~test_known
    results.to_csv(ARTIFACT_DIR / "test_predictions.csv", index=False)
    write_report(report)
    print(f"Selected C={report['selected_c']}. Test Macro-F1: {report['test']['model']['macro_f1']:.3f}")
    print(f"Keyword baseline Macro-F1: {report['test']['baseline']['macro_f1']:.3f}. Review threshold: {threshold:.3f}")


if __name__ == "__main__":
    main()
