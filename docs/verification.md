# Verificación y Validación de la Entrega Técnica

## 1. Experimento de Machine Learning Congelado

- **Dataset Total:** 720 incidentes sintéticos deterministas divididos en 40 familias técnicas disjuntas (`event_group_id`).
- **Particiones:**
  - *Train:* 450 incidentes (25 familias, 5 por categoría).
  - *Validation:* 90 incidentes (5 familias, 1 por categoría).
  - *Test:* 180 incidentes (10 familias, 2 por categoría).
- **Aislamiento:** Cero solapamiento léxico ni de familias entre las tres particiones.
- **Modelos Evaluados:**
  - Heurística de palabras clave UOIT.
  - Línea Base Lineal: TF-IDF dual (palabras + caracteres sub-palabra) + Regresión Logística ($C=1.0$).
  - Modelo Avanzado Propuesto: Sentence-Transformers (`MiniLM-L12-v2` congelado de 384 dimensiones) + Regresión Logística ($C=1.0$).
- **Selección Operativa en Validación:**
  - Macro-F1 Validación: Línea Base = **0.9423** vs Transformer = **0.7822**.
  - Decisión: La Línea Base fue seleccionada formalmente como el modelo operativo para producción.
- **Evaluación Final en Test Congelado:**
  - Macro-F1 Test: Línea Base = **0.7719** vs Transformer = **0.6592** vs Heurística = **0.8793**.
  - Top-3 Accuracy Test: Línea Base = **100.0%**.
  - Matriz de confusión e informe completo preservados en `artifacts/evaluation.md`.

---

## 2. Suite de Pruebas Automatizadas

La suite automatizada se ejecuta mediante `pytest`:

```bash
python -m pytest -q
```

**Resultado verificado: 34 pruebas exitosas (100% de aprobación).**

### Cobertura de Verificaciones:
1. **Datos y Particiones (`tests/test_data.py`):**
   - Reproducibilidad determinista bit a bit (`SEED = 42`).
   - Verificación de 720 incidentes en 40 familias.
   - Aislamiento absoluto de familias y textos normalizados entre Train, Validation y Test.
   - Rechazo de duplicados normalizados, etiquetas desconocidas y etiquetas contradictorias dentro de una misma familia.
2. **Modelos y Métricas (`tests/test_model.py`):**
   - Comportamiento de reglas léxicas y activación de fallback.
   - Cálculo exacto de métricas multiclase (Macro-F1, Accuracy y exactitud Top-3).
   - Calibración de umbral de revisión en validación buscando maximizar cobertura con $\ge 90\%$ de exactitud.
   - Activación de revisión ante vocabulario desconocido (`unknown_vocabulary`).
   - **Prueba de integridad de artefactos:** Inferencia real sobre `data/test.csv` cargando `artifacts/model.joblib` y comprobando concordancia exacta con `artifacts/metrics.json`.
   - Confirmación de que el modelo operativo seleccionado corresponde a la Línea Base por criterio de validación.
3. **Servicio y API (`tests/test_api.py`):**
   - Respuesta 200, estructura de ranking de 5 clases y medición de latencia en `/api/classify`.
   - **Rechazo estricto con error HTTP 422** ante 17 combinaciones de payloads inválidos y campos que generan fuga de información (`category`, `resolution`, `assignee`, etc.).
   - Respuesta controlada HTTP 503 ante ausencia del modelo.
   - Disponibilidad de estáticos, Swagger docs (`/docs`), `/api/categories` y `/api/health`.

---

## 3. Verificación de la Demostración

La interfaz web incluye tres escenarios diseñados para la defensa técnica:
1. **Caso A (Válido):** Incidente claro de saturación de conexiones en PgBouncer $\rightarrow$ Clasificado en `databases` con alto puntaje relativo y etiqueta de sugerencia confiable.
2. **Caso B (Difícil / Ambiguo):** Error 500 y timeout en reportes web $\rightarrow$ Distribución de probabilidades dividida entre `applications_services` y `databases`, evidenciando el valor del ranking Top-3.
3. **Caso C (Entrada Inválida):** Entrada que viola las restricciones mínimas de longitud o esquema $\rightarrow$ Rechazo inmediato con error HTTP 422, demostrando el control estricto de contratos.
