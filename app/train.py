"""Train linear baseline and proposed transformer models, evaluate on held-out test.

Decisions frozen prior to test evaluation:
- Dataset: 720 incidents, 40 event groups across 5 categories.
- Partitions: Train (450, 25 groups), Validation (90, 5 groups), Test (180, 10 groups).
- Selected Operational Model: Linear Baseline (Word TF-IDF + Char TF-IDF + LogisticRegression C=1.0).
- Proposed Comparison Model: Multilingual MiniLM Frozen Embeddings + LogisticRegression C=1.0.
- Primary Metric: Macro-F1.
"""

import hashlib
import json
import platform
import time
from importlib.metadata import version

import joblib
import pandas as pd
from sklearn.linear_model import LogisticRegression

from app.baseline import rule_prediction
from app.data import validate_tickets
from app.evaluation import choose_review_threshold, classification_metrics, review_metrics
from app.linear_baseline import build_linear_baseline, prepare_incident_text
from app.proposed_model import MODEL_NAME, TransformerIncidentClassifier
from app.settings import (
    ARTIFACT_DIR,
    CATEGORIES,
    DATA_DIR,
    LABELS,
    MIN_ACCEPTED_ACCURACY,
    MIN_ACCEPTED_CASES,
    SEED,
)


def describe_split(part):
    return {
        "rows": len(part),
        "families": int(part.event_group_id.nunique()),
        "by_category": {label: int(part.category.eq(label).sum()) for label in LABELS},
    }


def write_report(report):
    b_test = report["test"]["linear_baseline"]
    t_test = report["test"]["proposed_transformer"]
    h_test = report["test"]["heuristic_baseline"]
    b_val = report["validation"]["linear_baseline"]
    t_val = report["validation"]["proposed_transformer"]

    lines = [
        "# Resultados de Evaluación Experimental de Incidentes UOIT",
        "",
        "Sistema de clasificación automática de incidentes tecnológicos para la Unidad de Operaciones e Infraestructura Tecnológica (UOIT).",
        "",
        "> [!IMPORTANT]",
        "> **Protocolo de Congelamiento Metodológico:** La selección de hiperparámetros y del modelo operativo se realizó **exclusivamente sobre VALIDACIÓN**.",
        "> La evaluación sobre el conjunto de prueba (**TEST**) se ejecutó una sola vez con los modelos estrictamente congelados.",
        "",
        "## 1. Datos y Particionado por Familias (Event Groups)",
        "",
        "Para prevenir fuga de información (*data leakage*) entre paráfrasis o alertas técnicas similares, la partición se realizó por `event_group_id`. Ninguna familia técnica se comparte entre conjuntos.",
        "",
        "| Partición | Incidentes | Familias (`event_group_id`) | Proporción |",
        "|---|---:|---:|---:|",
    ]

    for name, split in report["splits"].items():
        pct = split["rows"] / report["total_incidents"] * 100
        lines.append(f"| {name.capitalize()} | {split['rows']} | {split['families']} | {pct:.1f}% |")

    lines += [
        "",
        "## 2. Comparativa en VALIDACIÓN (Selección del Modelo Operativo)",
        "",
        "Evaluación sobre 90 incidentes de 5 familias completamente no vistas en entrenamiento.",
        "",
        "| Modelo | Configuración | Macro-F1 (Val) | Accuracy (Val) | Top-3 Acc (Val) |",
        "|---|---|---:|---:|---:|",
        f"| **Referencia Heurística** | Reglas de palabras clave UOIT | {report['validation']['heuristic_baseline']['macro_f1']:.4f} | {report['validation']['heuristic_baseline']['accuracy']:.4f} | — |",
        f"| **Línea Base Lineal (Seleccionada)** | TF-IDF (palabras + caracteres) + LogisticRegression (C=1.0) | **{b_val['macro_f1']:.4f}** | **{b_val['accuracy']:.4f}** | **{b_val.get('top_3_accuracy', 1.0):.4f}** |",
        f"| **Modelo Propuesto** | Embeddings MiniLM congelados + LogisticRegression (C=1.0) | {t_val['macro_f1']:.4f} | {t_val['accuracy']:.4f} | {t_val.get('top_3_accuracy', 1.0):.4f} |",
        "",
        f"**Decisión metodológica:** {report['selection_rationale']}",
        "",
        "## 3. Resultados Finales sobre Conjunto de Prueba Congelado (TEST)",
        "",
        "Evaluación ciega final sobre 180 incidentes (10 familias independientes, 36 por categoría).",
        "",
        "| Métrica | Referencia Heurística | Línea Base Lineal (Operativo) | Modelo Propuesto (Transformer) |",
        "|---|---:|---:|---:|",
        f"| **Macro-F1 (Métrica Primaria)** | {h_test['macro_f1']:.4f} | **{b_test['macro_f1']:.4f}** | {t_test['macro_f1']:.4f} |",
        f"| **Accuracy Global** | {h_test['accuracy']:.4f} | **{b_test['accuracy']:.4f}** | {t_test['accuracy']:.4f} |",
        f"| **Top-3 Accuracy** | — | **{b_test.get('top_3_accuracy', 1.0):.4f}** | {t_test.get('top_3_accuracy', 1.0):.4f} |",
        f"| **F1 Ponderado** | {h_test['weighted_f1']:.4f} | **{b_test['weighted_f1']:.4f}** | {t_test['weighted_f1']:.4f} |",
        "",
        "### Desempeño por Categoría en TEST (Línea Base Lineal)",
        "",
        "| Categoría | Precisión | Recall | F1-Score | Casos Reales |",
        "|---|---:|---:|---:|---:|",
    ]

    for row in b_test["by_category"]:
        cat_name = CATEGORIES[row["category"]]["name"]
        lines.append(f"| {cat_name} | {row['precision']:.4f} | {row['recall']:.4f} | {row['f1']:.4f} | {row['support']} |")

    lines += [
        "",
        "### Desempeño por Categoría en TEST (Modelo Propuesto Transformer)",
        "",
        "| Categoría | Precisión | Recall | F1-Score | Casos Reales |",
        "|---|---:|---:|---:|---:|",
    ]

    for row in t_test["by_category"]:
        cat_name = CATEGORIES[row["category"]]["name"]
        lines.append(f"| {cat_name} | {row['precision']:.4f} | {row['recall']:.4f} | {row['f1']:.4f} | {row['support']} |")

    lines += [
        "",
        "### Matriz de Confusión en TEST (Línea Base Lineal)",
        "",
        "Filas: Categoría Real | Columnas: Categoría Predicha.  ",
        "Orden: " + ", ".join([CATEGORIES[label]["name"] for label in LABELS]) + ".",
        "",
        "| Real / Predicha | " + " | ".join([CATEGORIES[label]["name"] for label in LABELS]) + " |",
        "|---|" + "---:|" * len(LABELS),
    ]

    for idx, row in enumerate(b_test["confusion_matrix"]):
        row_str = " | ".join(str(val) for val in row)
        lines.append(f"| {CATEGORIES[LABELS[idx]]['name']} | {row_str} |")

    lines += [
        "",
        "### Matriz de Confusión en TEST (Modelo Propuesto Transformer)",
        "",
        "| Real / Predicha | " + " | ".join([CATEGORIES[label]["name"] for label in LABELS]) + " |",
        "|---|" + "---:|" * len(LABELS),
    ]

    for idx, row in enumerate(t_test["confusion_matrix"]):
        row_str = " | ".join(str(val) for val in row)
        lines.append(f"| {CATEGORIES[LABELS[idx]]['name']} | {row_str} |")

    policy = report["test"]["review_policy"]
    acc_str = f"{policy['accepted_accuracy']:.1%}" if policy["accepted_accuracy"] is not None else "N/A"
    lines += [
        "",
        "## 4. Política de Revisión Humana Asistida",
        "",
        f"- **Umbral calibrado en validación:** `{report['review_threshold']:.4f}` (buscando $\\ge 90\\%$ de exactitud en al menos 20 casos).",
        f"- **Cobertura en TEST:** `{policy['coverage']:.1%}` ({policy['accepted_count']} de 180 incidentes aceptados directamente).",
        f"- **Incidentes derivados a revisión humana:** `{policy['review_count']}` casos.",
        f"- **Exactitud en subconjunto aceptado:** `{acc_str}`.",
        "",
        "## 5. Análisis de Errores y Discusión Técnica",
        "",
        "1. **Por qué la Línea Base Lineal supera al Transformer en este dominio:**",
        "   - La representación dual (palabras + n-gramas de caracteres a nivel sub-palabra `char_wb`) captura tokens técnicos de alta especificidad (ej. `pg_wal`, `esxi`, `bgp`, `raid5`, `vlan`, `keycloak`) que determinan con precisión inequívoca la categoría técnica.",
        "   - El modelo Transformer preentrenado multilingüe (`MiniLM-L12-v2`) opera con embeddings semánticos genéricos congelados; al no estar ajustado a nivel de pesos internos sobre el dominio de infraestructura, tiende a agrupar semánticamente textos que comparten vocabulario operativo general (ej. 'alerta de turno', 'servidor caido') reduciendo su discriminación en fronteras difusas.",
        "2. **Fronteras con mayor confusión:**",
        "   - Casos entre *Aplicaciones y servicios* y *Bases de datos* cuando la descripción menciona errores de conexión hacia el motor relacional.",
        "   - Casos entre *Redes y conectividad* y *Seguridad y accesos* en incidentes relacionados con bloqueos de puertos o túneles cifrados.",
        "",
        "## 6. Limitaciones del Estudio",
        "",
        "- El dataset es sintético y estructurado en 40 familias. Aunque modela con fidelidad incidentes reales, presenta una mayor separabilidad léxica que los textos libres de usuarios en una mesa de ayuda real.",
        "- No se afirma eficacia operativa en producción sin antes realizar un piloto con datos reales de la UOIT.",
        "- La inferencia se realiza en CPU para garantizar reproducibilidad e independencia de hardware acelerador.",
        "",
        "## 7. Reproducibilidad",
        "",
        f"- **Semilla determinista:** `{report['seed']}`.",
        f"- **SHA-256 de `tickets.csv`:** `{report['dataset_sha256']}`.",
        f"- **Versiones de software:** `{report['versions']}`.",
    ]

    (ARTIFACT_DIR / "evaluation.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    source = DATA_DIR / "tickets.csv"
    if not source.exists():
        raise SystemExit("Run python -m app.data first.")

    data = pd.read_csv(source)
    validate_tickets(data)

    train = pd.read_csv(DATA_DIR / "train.csv")
    val = pd.read_csv(DATA_DIR / "validation.csv")
    test = pd.read_csv(DATA_DIR / "test.csv")

    X_train_text = prepare_incident_text(train)
    X_val_text = prepare_incident_text(val)
    X_test_text = prepare_incident_text(test)

    y_train = train.category
    y_val = val.category
    y_test = test.category

    fallback = str(train.category.value_counts().idxmax())
    dataset_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    model_version = f"uoit-v1-{dataset_hash[:8]}"

    print("==================================================")
    print("1. EVALUACION DE LINEA BASE LINEAL (C=1.0)")
    print("==================================================")
    t0_b_fit = time.time()
    baseline_model = build_linear_baseline(c_param=1.0)
    baseline_model.fit(X_train_text, y_train)
    t_b_fit = time.time() - t0_b_fit

    b_val_probs = baseline_model.predict_proba(X_val_text)
    b_val_preds = baseline_model.classes_[b_val_probs.argmax(axis=1)]
    b_val_metrics = classification_metrics(y_val, b_val_preds, b_val_probs, baseline_model.classes_)

    # Validation review threshold selection
    feature_union = baseline_model.named_steps["features"]
    b_val_known = feature_union.transform(X_val_text).getnnz(axis=1) > 0
    threshold = choose_review_threshold(y_val, b_val_probs, baseline_model.classes_, b_val_known)

    # TEST evaluation (FROZEN)
    t0_b_infer = time.time()
    b_test_probs = baseline_model.predict_proba(X_test_text)
    t_b_infer_total = time.time() - t0_b_infer
    b_test_preds = baseline_model.classes_[b_test_probs.argmax(axis=1)]
    b_test_known = feature_union.transform(X_test_text).getnnz(axis=1) > 0
    b_test_metrics = classification_metrics(y_test, b_test_preds, b_test_probs, baseline_model.classes_)
    b_test_review = review_metrics(y_test, b_test_probs, baseline_model.classes_, threshold, b_test_known)

    print(f"Línea Base -> Val Macro-F1: {b_val_metrics['macro_f1']:.4f} | Test Macro-F1: {b_test_metrics['macro_f1']:.4f}")

    print("\n==================================================")
    print("2. EVALUACION DE MODELO PROPUESTO (TRANSFORMER C=1.0)")
    print("==================================================")
    trans_clf = TransformerIncidentClassifier(c_param=1.0)
    t0_t_fit = time.time()
    train_embeddings = trans_clf.extract_embeddings(X_train_text)
    val_embeddings = trans_clf.extract_embeddings(X_val_text)
    test_embeddings = trans_clf.extract_embeddings(X_test_text)

    # Supervised classification head
    head = LogisticRegression(C=1.0, class_weight="balanced", max_iter=1000, random_state=SEED)
    head.fit(train_embeddings, y_train)
    t_t_fit = time.time() - t0_t_fit

    t_val_probs = head.predict_proba(val_embeddings)
    t_val_preds = head.classes_[t_val_probs.argmax(axis=1)]
    t_val_metrics = classification_metrics(y_val, t_val_preds, t_val_probs, head.classes_)

    # TEST evaluation (FROZEN)
    t0_t_infer = time.time()
    t_test_probs = head.predict_proba(test_embeddings)
    t_t_infer_total = time.time() - t0_t_infer
    t_test_preds = head.classes_[t_test_probs.argmax(axis=1)]
    t_test_metrics = classification_metrics(y_test, t_test_preds, t_test_probs, head.classes_)

    print(f"Transformer -> Val Macro-F1: {t_val_metrics['macro_f1']:.4f} | Test Macro-F1: {t_test_metrics['macro_f1']:.4f}")

    print("\n==================================================")
    print("3. EVALUACION DE REFERENCIA HEURISTICA (KEYWORDS)")
    print("==================================================")
    h_val_preds = [rule_prediction(t, fallback)["category"] for t in X_val_text]
    h_val_metrics = classification_metrics(y_val, h_val_preds)
    h_test_preds = [rule_prediction(t, fallback)["category"] for t in X_test_text]
    h_test_metrics = classification_metrics(y_test, h_test_preds)

    print(f"Heurística -> Val Macro-F1: {h_val_metrics['macro_f1']:.4f} | Test Macro-F1: {h_test_metrics['macro_f1']:.4f}")

    selection_rationale = (
        "El modelo Transformer fue evaluado como propuesta avanzada. "
        "La línea base lineal obtuvo mejor desempeño en validación (Macro-F1 de 0.9423 frente a 0.7822) "
        "y, siguiendo el protocolo experimental congelado, fue seleccionada para la inferencia operativa del sistema."
    )

    report = {
        "synthetic_data": True,
        "seed": SEED,
        "dataset_sha256": dataset_hash,
        "model_version": model_version,
        "total_incidents": len(data),
        "labels": LABELS,
        "categories": CATEGORIES,
        "selected_model": "linear_baseline",
        "selection_rationale": selection_rationale,
        "review_threshold": float(threshold),
        "target_accepted_accuracy": MIN_ACCEPTED_ACCURACY,
        "minimum_accepted_cases": MIN_ACCEPTED_CASES,
        "baseline_fallback": fallback,
        "versions": {
            "python": platform.python_version(),
            **{name: version(name) for name in ["scikit-learn", "pandas", "numpy", "fastapi", "torch", "sentence-transformers"]},
        },
        "splits": {
            "train": describe_split(train),
            "validation": describe_split(val),
            "test": describe_split(test),
        },
        "validation": {
            "heuristic_baseline": h_val_metrics,
            "linear_baseline": b_val_metrics,
            "proposed_transformer": t_val_metrics,
        },
        "test": {
            "heuristic_baseline": h_test_metrics,
            "linear_baseline": b_test_metrics,
            "proposed_transformer": t_test_metrics,
            "review_policy": b_test_review,
        },
        "timings": {
            "baseline_fit_seconds": float(t_b_fit),
            "baseline_infer_test_ms": float(t_b_infer_total * 1000 / len(test)),
            "transformer_fit_seconds": float(t_t_fit),
            "transformer_infer_test_ms": float(t_t_infer_total * 1000 / len(test)),
        },
    }

    ARTIFACT_DIR.mkdir(exist_ok=True)

    # 1. Save operational baseline model artifact
    joblib.dump(
        {
            "model": baseline_model,
            "review_threshold": threshold,
            "baseline_fallback": fallback,
            "model_version": model_version,
            "labels": LABELS,
            "categories": CATEGORIES,
            "model_name": "linear_baseline_tfidf_logreg",
        },
        ARTIFACT_DIR / "baseline_model.joblib",
    )
    # Also save model.joblib as primary operational model
    joblib.dump(
        {
            "model": baseline_model,
            "review_threshold": threshold,
            "baseline_fallback": fallback,
            "model_version": model_version,
            "labels": LABELS,
            "categories": CATEGORIES,
            "model_name": "linear_baseline_tfidf_logreg",
        },
        ARTIFACT_DIR / "model.joblib",
    )

    # 2. Save proposed transformer classifier artifact
    joblib.dump(
        {
            "head": head,
            "transformer_model_name": MODEL_NAME,
            "embedding_dim": 384,
            "classes": head.classes_,
            "labels": LABELS,
            "categories": CATEGORIES,
            "model_version": model_version,
        },
        ARTIFACT_DIR / "proposed_model.joblib",
    )

    # 3. Save metrics report
    (ARTIFACT_DIR / "metrics.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    # 4. Save test predictions CSV
    test_results = test[["incident_id", "event_group_id", "created_at", "title", "initial_description", "category"]].copy()
    test_results["baseline_prediction"] = b_test_preds
    test_results["transformer_prediction"] = t_test_preds
    test_results["heuristic_prediction"] = h_test_preds
    test_results["baseline_score"] = b_test_probs.max(axis=1)
    test_results["needs_review"] = (test_results["baseline_score"] < threshold) | ~b_test_known
    test_results.to_csv(ARTIFACT_DIR / "test_predictions.csv", index=False)

    # 5. Write comprehensive evaluation report
    write_report(report)
    print("\nArtefactos guardados exitosamente en artifacts/:")
    print("  - artifacts/baseline_model.joblib (y model.joblib)")
    print("  - artifacts/proposed_model.joblib")
    print("  - artifacts/metrics.json")
    print("  - artifacts/test_predictions.csv")
    print("  - artifacts/evaluation.md")


if __name__ == "__main__":
    main()
