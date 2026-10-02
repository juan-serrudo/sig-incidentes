# Metodología de Clasificación y Evaluación Experimental

## 1. Referencia Heurística por Palabras Clave

El módulo `app/baseline.py` implementa una regla determinista basada en términos técnicos representativos de la infraestructura de la UOIT:
- Define listas de términos clave para cada una de las cinco categorías operativas (`applications_services`, `databases`, `networks_connectivity`, `infrastructure_storage`, `security_access`).
- Normaliza el texto de entrada (eliminando mayúsculas, diacríticos y puntuación mediante `app/text.py`) y contabiliza coincidencias exactas de términos completos.
- Asigna la categoría con mayor número de coincidencias distintas. En caso de empate se respeta el orden taxonómico definido en `app/settings.py`. Si ningún término coincide, se asigna la categoría de respaldo (`applications_services`).
- Esta heurística sirve como cota inferior interpretable, careciendo de comprensión semántica profunda o análisis composicional.

## 2. Línea Base Lineal (Dual TF-IDF + Regresión Logística)

La línea base supervisada (`app/linear_baseline.py`) combina:
1. **Representación Dual de Texto:**
   - **TF-IDF a nivel de palabras:** N-gramas $(1, 2)$, frecuencia mínima de documento (`min_df=2`), límite de 5.000 características y escalado sublineal de frecuencia de término (`sublinear_tf=True`).
   - **TF-IDF a nivel de caracteres en límites de palabras (`char_wb`):** N-gramas $(3, 5)$, `min_df=3`, hasta 5.000 características y `sublinear_tf=True`. Esta extracción captura raíces léxicas y sub-tokens de herramientas especializadas (`pg_wal`, `esxi`, `bgp`, `raid5`, `vlan`, `keycloak`).
   - Ambas matrices se consolidan mediante `FeatureUnion`.
2. **Clasificador Lineal:**
   - `LogisticRegression(C=1.0, class_weight="balanced", max_iter=1000, random_state=42)`.
   - Se entrena dentro de un `Pipeline` de scikit-learn, garantizando que el vocabulario y la ponderación IDF se aprendan exclusivamente sobre la partición de entrenamiento (*Train*).

## 3. Modelo Propuesto Avanzado (Transformer Multilingüe)

El clasificador avanzado (`app/proposed_model.py`) adopta una estrategia de dos etapas:
1. **Extractor de Características Semánticas:**
   - Red neuronal preentrenada `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (12 capas, 384 dimensiones densas).
   - Los pesos de las capas de atención permanecen **completamente congelados** (*frozen*), extrayendo vectores mediante agregación de media (*mean pooling*) normalizados.
2. **Clasificador Supervisado:**
   - `LogisticRegression(C=1.0, class_weight="balanced", max_iter=1000, random_state=42)` ajustado sobre los embeddings densos.

## 4. Métricas de Evaluación

| Métrica | Definición e Interpretación |
|---|---|
| **Precisión por Categoría** | Fracción de incidentes asignados a la categoría que realmente pertenecían a ella. |
| **Recall por Categoría** | Fracción de incidentes reales de esa categoría que fueron correctamente clasificados. |
| **F1 por Categoría** | Media armónica entre precisión y recall para un área técnica específica. |
| **Macro-F1 (Métrica Primaria)** | Promedio aritmético no ponderado del F1-Score de las cinco clases. Trata a todas las áreas con igual importancia. |
| **Accuracy Global** | Proporción global de predicciones correctas sobre el total de incidentes evaluados. |
| **Top-3 Accuracy** | Frecuencia con la que la categoría real se encuentra dentro de las tres primeras sugerencias del modelo. |
| **Matriz de Confusión** | Tabla de contingencia completa (filas = clases reales, columnas = clases predichas). |

## 5. Protocolo de Selección y Congelamiento Metodológico

- **Decisión en Validación:** La selección del modelo operativo se tomó **exclusivamente sobre el conjunto de VALIDATION (90 incidentes, 5 familias técnicas no vistas)**.
  - La Línea Base Lineal obtuvo un Macro-F1 de **0.9423** frente a **0.7822** del Transformer.
  - Siguiendo el protocolo experimental, la Línea Base Lineal fue seleccionada para operar la inferencia del sistema y guardada en `artifacts/model.joblib`.
- **Evaluación Final en Test:** El conjunto de prueba (**TEST**, 180 incidentes, 10 familias disjuntas) se evaluó **una sola vez** con los modelos estrictamente congelados:
  - Línea Base: Macro-F1 = **0.7719**, Accuracy = **78.9%**, Top-3 Accuracy = **100.0%**.
  - Transformer: Macro-F1 = **0.6592**, Accuracy = **70.0%**, Top-3 Accuracy = **96.1%**.
  - Heurística: Macro-F1 = **0.8793**, Accuracy = **88.9%**.
- **No se reajustaron parámetros ni se realizaron modificaciones al modelo basándose en Test.**

## 6. Política de Revisión Humana Asistida

Para evitar tratar todas las salidas como certezas absolutas, se implementa una política de triaje asistido:
1. En validación se analiza la distribución de puntajes estimados y aciertos.
2. Se selecciona el umbral más bajo que garantice al menos 90% de exactitud sobre un mínimo de 20 casos aceptados.
3. El umbral calibrado resultante es `review_threshold = 0.2209`.
4. En inferencia, se activa la advertencia `requires_review = True` si:
   - El texto contiene vocabulario completamente no reconocido por el vectorizador (`unknown_vocabulary`).
   - El puntaje estimado máximo no supera el umbral de calibración (`below_threshold`).
5. Los puntajes devueltos por `predict_proba()` representan **puntajes estimados por el modelo para cada categoría** y **no constituyen una garantía calibrada de acierto**.

## 7. Explicabilidad Léxica

Para la categoría con mayor puntaje, el sistema identifica los términos o n-gramas presentes que aportaron peso positivo al logit correspondiente ($w_j \cdot x_j > 0$), mostrando hasta cinco señales destacadas para asistir el criterio del operador humano.

## 8. Limitaciones Metodológicas

- **Dataset Sintético:** Los 720 incidentes generados mediante plantillas controladas exhiben mayor separabilidad léxica que los reportes libres de usuarios técnicos reales.
- **Modelo Mono-etiqueta:** Asume una única categoría principal por ticket, sin capturar incidentes de cascada multi-sistema.
- **Entorno Experimental:** Los resultados representan una cota de referencia de laboratorio y requieren validación en un piloto con incidentes de producción.
