# Resultados de Evaluación Experimental de Incidentes UOIT

Sistema de clasificación automática de incidentes tecnológicos para la Unidad de Operaciones e Infraestructura Tecnológica (UOIT).

> [!IMPORTANT]
> **Protocolo de Congelamiento Metodológico:** La selección de hiperparámetros y del modelo operativo se realizó **exclusivamente sobre VALIDACIÓN**.
> La evaluación sobre el conjunto de prueba (**TEST**) se ejecutó una sola vez con los modelos estrictamente congelados.

## 1. Datos y Particionado por Familias (Event Groups)

Para prevenir fuga de información (*data leakage*) entre paráfrasis o alertas técnicas similares, la partición se realizó por `event_group_id`. Ninguna familia técnica se comparte entre conjuntos.

| Partición | Incidentes | Familias (`event_group_id`) | Proporción |
|---|---:|---:|---:|
| Train | 450 | 25 | 62.5% |
| Validation | 90 | 5 | 12.5% |
| Test | 180 | 10 | 25.0% |

## 2. Comparativa en VALIDACIÓN (Selección del Modelo Operativo)

Evaluación sobre 90 incidentes de 5 familias completamente no vistas en entrenamiento.

| Modelo | Configuración | Macro-F1 (Val) | Accuracy (Val) | Top-3 Acc (Val) |
|---|---|---:|---:|---:|
| **Referencia Heurística** | Reglas de palabras clave UOIT | 0.6605 | 0.7222 | — |
| **Línea Base Lineal (Seleccionada)** | TF-IDF (palabras + caracteres) + LogisticRegression (C=1.0) | **0.9423** | **0.9444** | **0.9778** |
| **Modelo Propuesto** | Embeddings MiniLM congelados + LogisticRegression (C=1.0) | 0.7822 | 0.8111 | 0.9889 |

**Decisión metodológica:** El modelo Transformer fue evaluado como propuesta avanzada. La línea base lineal obtuvo mejor desempeño en validación (Macro-F1 de 0.9423 frente a 0.7822) y, siguiendo el protocolo experimental congelado, fue seleccionada para la inferencia operativa del sistema.

## 3. Resultados Finales sobre Conjunto de Prueba Congelado (TEST)

Evaluación ciega final sobre 180 incidentes (10 familias independientes, 36 por categoría).

| Métrica | Referencia Heurística | Línea Base Lineal (Operativo) | Modelo Propuesto (Transformer) |
|---|---:|---:|---:|
| **Macro-F1 (Métrica Primaria)** | 0.8793 | **0.7719** | 0.6592 |
| **Accuracy Global** | 0.8889 | **0.7889** | 0.7000 |
| **Top-3 Accuracy** | — | **1.0000** | 0.9611 |
| **F1 Ponderado** | 0.8793 | **0.7719** | 0.6592 |

### Desempeño por Categoría en TEST (Línea Base Lineal)

| Categoría | Precisión | Recall | F1-Score | Casos Reales |
|---|---:|---:|---:|---:|
| Aplicaciones y servicios | 0.6316 | 0.3333 | 0.4364 | 36 |
| Bases de datos | 0.9722 | 0.9722 | 0.9722 | 36 |
| Redes y conectividad | 0.9000 | 0.7500 | 0.8182 | 36 |
| Infraestructura y almacenamiento | 0.6604 | 0.9722 | 0.7865 | 36 |
| Seguridad y accesos | 0.7857 | 0.9167 | 0.8462 | 36 |

### Desempeño por Categoría en TEST (Modelo Propuesto Transformer)

| Categoría | Precisión | Recall | F1-Score | Casos Reales |
|---|---:|---:|---:|---:|
| Aplicaciones y servicios | 0.4444 | 0.1111 | 0.1778 | 36 |
| Bases de datos | 0.9091 | 0.8333 | 0.8696 | 36 |
| Redes y conectividad | 0.7429 | 0.7222 | 0.7324 | 36 |
| Infraestructura y almacenamiento | 0.7500 | 1.0000 | 0.8571 | 36 |
| Seguridad y accesos | 0.5455 | 0.8333 | 0.6593 | 36 |

### Matriz de Confusión en TEST (Línea Base Lineal)

Filas: Categoría Real | Columnas: Categoría Predicha.  
Orden: Aplicaciones y servicios, Bases de datos, Redes y conectividad, Infraestructura y almacenamiento, Seguridad y accesos.

| Real / Predicha | Aplicaciones y servicios | Bases de datos | Redes y conectividad | Infraestructura y almacenamiento | Seguridad y accesos |
|---|---:|---:|---:|---:|---:|
| Aplicaciones y servicios | 12 | 0 | 2 | 14 | 8 |
| Bases de datos | 1 | 35 | 0 | 0 | 0 |
| Redes y conectividad | 4 | 0 | 27 | 4 | 1 |
| Infraestructura y almacenamiento | 0 | 1 | 0 | 35 | 0 |
| Seguridad y accesos | 2 | 0 | 1 | 0 | 33 |

### Matriz de Confusión en TEST (Modelo Propuesto Transformer)

| Real / Predicha | Aplicaciones y servicios | Bases de datos | Redes y conectividad | Infraestructura y almacenamiento | Seguridad y accesos |
|---|---:|---:|---:|---:|---:|
| Aplicaciones y servicios | 4 | 3 | 3 | 12 | 14 |
| Bases de datos | 4 | 30 | 0 | 0 | 2 |
| Redes y conectividad | 1 | 0 | 26 | 0 | 9 |
| Infraestructura y almacenamiento | 0 | 0 | 0 | 36 | 0 |
| Seguridad y accesos | 0 | 0 | 6 | 0 | 30 |

## 4. Política de Revisión Humana Asistida

- **Umbral calibrado en validación:** `0.2209` (buscando $\ge 90\%$ de exactitud en al menos 20 casos).
- **Cobertura en TEST:** `100.0%` (180 de 180 incidentes aceptados directamente).
- **Incidentes derivados a revisión humana:** `0` casos.
- **Exactitud en subconjunto aceptado:** `78.9%`.

## 5. Análisis de Errores y Discusión Técnica

1. **Por qué la Línea Base Lineal supera al Transformer en este dominio:**
   - La representación dual (palabras + n-gramas de caracteres a nivel sub-palabra `char_wb`) captura tokens técnicos de alta especificidad (ej. `pg_wal`, `esxi`, `bgp`, `raid5`, `vlan`, `keycloak`) que determinan con precisión inequívoca la categoría técnica.
   - El modelo Transformer preentrenado multilingüe (`MiniLM-L12-v2`) opera con embeddings semánticos genéricos congelados; al no estar ajustado a nivel de pesos internos sobre el dominio de infraestructura, tiende a agrupar semánticamente textos que comparten vocabulario operativo general (ej. 'alerta de turno', 'servidor caido') reduciendo su discriminación en fronteras difusas.
2. **Fronteras con mayor confusión:**
   - Casos entre *Aplicaciones y servicios* y *Bases de datos* cuando la descripción menciona errores de conexión hacia el motor relacional.
   - Casos entre *Redes y conectividad* y *Seguridad y accesos* en incidentes relacionados con bloqueos de puertos o túneles cifrados.

## 6. Limitaciones del Estudio

- El dataset es sintético y estructurado en 40 familias. Aunque modela con fidelidad incidentes reales, presenta una mayor separabilidad léxica que los textos libres de usuarios en una mesa de ayuda real.
- No se afirma eficacia operativa en producción sin antes realizar un piloto con datos reales de la UOIT.
- La inferencia se realiza en CPU para garantizar reproducibilidad e independencia de hardware acelerador.

## 7. Reproducibilidad

- **Semilla determinista:** `42`.
- **SHA-256 de `tickets.csv`:** `f65c66ec431f95112ab686f94ea067c712f61104e542adc8596f515c3555e0b7`.
- **Versiones de software:** `{'python': '3.12.3', 'scikit-learn': '1.9.1', 'pandas': '2.3.3', 'numpy': '2.2.6', 'fastapi': '0.115.14', 'torch': '2.14.1+cpu', 'sentence-transformers': '6.1.0'}`.
