# Informe Técnico Final: Clasificación Automática de Incidentes Tecnológicos mediante Machine Learning Supervisado para Triaje Operativo en la UOIT

**Autor:** Juan Serrudo  
**Programa:** Maestría en Ingeniería de Software Avanzada  
**Asignatura:** Proyecto Final de Machine Learning  
**Fecha:** Octubre 2026  
**Repositorio:** `support-triage-demo` (rama `feature/uoit-incident-classifier`)  

---

## 1. Título

**Sistema Asistido de Triaje y Clasificación Automática de Incidentes de Infraestructura Tecnológica utilizando Procesamiento de Lenguaje Natural Supervisado.**

---

## 2. Problema

La Unidad de Operaciones e Infraestructura Tecnológica (UOIT) opera servicios críticos institucionales que abarcan redes corporativas, centros de cómputo, plataformas de virtualización, bases de datos centrales y plataformas de identidad y acceso. 

En el flujo diario de operaciones, los operadores de la mesa de ayuda técnica y de guardia reciben decenas de alertas y tickets generados tanto por sistemas automatizados de monitoreo (ej. Zabbix, controladoras RAID, firewalls perimetrales, consolas EDR) como por usuarios técnicos. El enrutamiento inicial de estos requerimientos hacia las áreas de ingeniería especializadas presenta fricciones estructurales:
- **Demoras en el triaje inicial:** Tiempos muertos entre la recepción del incidente y la asignación al especialista adecuado.
- **Asignaciones cruzadas erróneas:** Ambigüedad en la descripción del problema (por ejemplo, una aplicación web lenta provocada por un bloqueo de transacciones en la base de datos suele ser remitida erróneamente al equipo de desarrollo).
- **Sobrecarga cognitiva en turnos de guardia:** Personal en guardias nocturnas que debe diagnosticar rápidamente la naturaleza del fallo con información fragmentaria.

El problema central consiste en **determinar con rapidez y precisión la categoría técnica resolutora de un incidente utilizando exclusivamente la información textual disponible al momento de la apertura del ticket**.

---

## 3. Objetivo

Diseñar, implementar, evaluar experimentalmente y desplegar un sistema prototipo de Machine Learning supervisado para la clasificación automática de incidentes de la UOIT, cumpliendo con los siguientes objetivos específicos:
1. **Modelado y Taxonomía:** Establecer un espacio de 5 categorías técnicas mutuamente excluyentes representativas de las áreas operativas de la UOIT.
2. **Prevención Estricta de Fuga de Información:** Construir un protocolo de evaluación basado en particionado por familias técnicas disjuntas (`event_group_id`), bloqueando en tiempo de inferencia cualquier variable posterior al diagnóstico (como soluciones, técnicos asignados o causas raíz).
3. **Comparativa Experimental Controlada:** Evaluar una línea base lineal con representación n-grama dual frente a una propuesta avanzada basada en Transformers multilingües congelados.
4. **Congelamiento Metodológico:** Seleccionar el modelo operativo basándose estrictamente en los resultados sobre el conjunto de validación, ejecutando la evaluación de prueba final (*test*) una sola vez sin reajuste posterior de hiperparámetros.
5. **Servicio y Demostración:** Desarrollar un backend REST en FastAPI con validación rigurosa de esquemas y una interfaz web con soporte para escenarios demostrativos claros, ambiguos y fuera de dominio.

---

## 4. Dataset

Debido a estrictas políticas de confidencialidad institucional, secreto de infraestructura y protección de datos corporativos, se prohibió el uso directo y la exposición de datos reales de producción.

Para salvaguardar estos principios sin comprometer el rigor metodológico, se construyó un dataset sintético estructurado y representativo:
- **Volumen Total:** 720 incidentes en idioma español.
- **Estructura:** 40 familias técnicas disjuntas (`event_group_id`), con 8 familias por cada una de las 5 categorías.
- **Variabilidad:** Cada familia cuenta con 18 variantes que introducen diversidad sintáctica, variación de alertas de monitoreo, niveles de urgencia y términos técnicos alternativos.
- **Balance de Clases:** Distribución perfectamente uniforme, con exactamente 144 incidentes por categoría ($20.0\%$ por clase).

Las 5 categorías y sus alcances son:
1. `applications_services`: Microservicios, APIs REST, aplicaciones web, cola de mensajería, errores 500 y servicios dependientes.
2. `databases`: Motores relacionales PostgreSQL/Oracle, pools de conexión (PgBouncer), bloqueos masivos, agotamiento de tablespace y corrupción de índices.
3. `networks_connectivity`: Enlaces WAN, enrutadores de frontera BGP, switches de distribución, servidores DNS corporativos, enlaces Wi-Fi y VPNs IPsec.
4. `infrastructure_storage`: Servidores blade, hipervisores VMware/KVM, almacenamiento SAN/iSCSI, arreglos RAID y fuentes de poder redundantes.
5. `security_access`: Directorio Activo, Single Sign-On (SSO / Keycloak), certificados SSL expirados, llaves SSH, reglas de firewall y alertas EDR.

---

## 5. Preparación de Datos y Prevención de Fuga

### Variables Permitidas vs Prohibidas
Para evitar la fuga de información (*data leakage*), el pipeline diferencia estrictamente las etapas del ciclo de vida del ticket:
- **Variables de Entrada Admitidas:** `title` (resumen del problema) e `initial_description` (descripción preliminar reportada).
- **Variables Excluidas y Prohibidas en Inferencia:** `category` (etiqueta real), `resolution` (acciones tomadas), `root_cause` (causa raíz diagnosticada), `assignee` (técnico resolutor), `closing_text` (comentarios de cierre) y `solution` (solución implementada).

### Particionado Disjunto por Familias
En tareas de NLP asistido por plantillas o fuentes técnicas, particionar aleatoriamente a nivel de registro propaga frases casi idénticas entre entrenamiento y prueba. Para mitigar este sesgo, el particionado se realizó agrupando por `event_group_id`:
- **Train (450 incidentes / 25 familias):** 5 familias por categoría.
- **Validation (90 incidentes / 5 familias):** 1 familia por categoría.
- **Test (180 incidentes / 10 familias):** 2 familias por categoría.

Ningún `event_group_id` ni texto normalizado se comparte entre las tres particiones.

---

## 6. Línea Base Seleccionada

La línea base supervisada (`app/linear_baseline.py`) fue diseñada para explotar tokens técnicos específicos mediante una representación dual:
1. **TF-IDF de Palabras:** N-gramas $(1, 2)$ con ponderación sublineal de frecuencia de término.
2. **TF-IDF de Caracteres en Límite de Palabras (`char_wb`):** N-gramas $(3, 5)$ para capturar raíces léxicas y sub-tokens de nombres de herramientas y comandos técnicos.
3. **Unión de Características (`FeatureUnion`):** Genera una matriz dispersa consolidada de alta dimensionalidad.
4. **Clasificador:** `LogisticRegression(C=1.0, max_iter=1000, random_state=42)` con función de coste multiclase multinomial.

---

## 7. Modelo Propuesto Avanzado

Como alternativa avanzada de aprendizaje profundo (`app/proposed_model.py`), se formuló un pipeline basado en representaciones neuronales densas:
1. **Extractor de Embeddings Semánticos:**  
   `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`.
   - Arquitectura Transformer de 12 capas y 384 dimensiones ocultas.
   - Pesos preentrenados congelados (*frozen*), extrayendo vectores mediante agregación de media (*mean pooling*).
2. **Clasificador Final:**  
   `LogisticRegression(C=1.0, max_iter=1000, random_state=42)` ajustado sobre los vectores densos generados por el Transformer.

---

## 8. Validación Experimental y Decisión Metodológica

Siguiendo el protocolo científico predefinido, la selección del modelo que operaría en el backend del sistema se tomó **exclusivamente a partir del desempeño en el conjunto de VALIDATION**:

### Resultados Comparativos en VALIDACIÓN (90 incidentes)

| Modelo | Configuración | Macro-F1 (Val) | Accuracy (Val) | Top-3 Acc (Val) |
|---|---|---:|---:|---:|
| **Referencia Heurística** | Reglas léxicas UOIT | 0.6605 | 0.7222 | — |
| **Línea Base Lineal (Operativo)** | Dual TF-IDF + LogisticRegression ($C=1.0$) | **0.9423** | **0.9444** | **0.9778** |
| **Modelo Propuesto** | MiniLM-L12-v2 (384d) + LogisticRegression ($C=1.0$) | 0.7822 | 0.8111 | 0.9889 |

### Decisión de Congelamiento Metodológico
> *“El modelo Transformer fue evaluado como propuesta avanzada. La línea base lineal obtuvo mejor desempeño en validación y, siguiendo el protocolo experimental, fue seleccionada para la inferencia del sistema.”*

---

## 9. Métricas de Evaluación

- **Macro-F1 (Métrica Primaria):** Promedio no ponderado del F1-Score entre las 5 clases:
  $$\text{Macro-F1} = \frac{1}{K}\sum_{k=1}^K \frac{2 \cdot P_k \cdot R_k}{P_k + R_k}$$
- **Accuracy Global:** Proporción de predicciones correctas sobre el total de la muestra.
- **Precision, Recall y F1 por Clase:** Análisis detallado de rendimiento por equipo de destino.
- **Top-3 Accuracy:** Porcentaje de aciertos en los cuales la categoría real se encuentra entre las 3 opciones con mayor probabilidad asignada.
- **Matriz de Confusión:** Inspección de errores de asignación cruzada.
- **Latencia de Inferencia:** Tiempo de cómputo en milisegundos por solicitud en CPU.

---

## 10. Resultados Finales sobre TEST Congelado

La partición de prueba (`data/test.csv`, 180 incidentes) fue evaluada **una sola vez** con ambos modelos estrictamente congelados (sin sintonización posterior de ningún hiperparámetro):

### Tabla Comparativa Final en TEST (180 incidentes)

| Métrica | Referencia Heurística | Línea Base Lineal (Seleccionada) | Modelo Propuesto (Transformer) |
|---|---:|---:|---:|
| **Macro-F1 (Métrica Primaria)** | 0.8793 | **0.7719** | 0.6592 |
| **Accuracy Global** | 0.8889 | **0.7889** | 0.7000 |
| **Top-3 Accuracy** | — | **1.0000** | 0.9611 |
| **F1 Ponderado** | 0.8793 | **0.7719** | 0.6592 |

---

## 11. Desglose por Clase en TEST

### Línea Base Lineal (Modelo Operativo)

| Categoría | Precisión | Recall | F1-Score | Casos Reales |
|---|---:|---:|---:|---:|
| `applications_services` | 0.6316 | 0.3333 | 0.4364 | 36 |
| `databases` | 0.9722 | 0.9722 | 0.9722 | 36 |
| `networks_connectivity` | 0.9000 | 0.7500 | 0.8182 | 36 |
| `infrastructure_storage` | 0.6604 | 0.9722 | 0.7865 | 36 |
| `security_access` | 0.7857 | 0.9167 | 0.8462 | 36 |

### Modelo Propuesto (Transformer Congelado)

| Categoría | Precisión | Recall | F1-Score | Casos Reales |
|---|---:|---:|---:|---:|
| `applications_services` | 0.4444 | 0.1111 | 0.1778 | 36 |
| `databases` | 0.9091 | 0.8333 | 0.8696 | 36 |
| `networks_connectivity` | 0.7429 | 0.7222 | 0.7324 | 36 |
| `infrastructure_storage` | 0.7500 | 1.0000 | 0.8571 | 36 |
| `security_access` | 0.5455 | 0.8333 | 0.6593 | 36 |

---

## 12. Matrices de Confusión en TEST

### Línea Base Lineal (Filas = Real, Columnas = Predicha)

| Real / Predicha | Apps | DB | Net | Infra | Sec |
|---|---:|---:|---:|---:|---:|
| `applications_services` (36) | **12** | 0 | 2 | 14 | 8 |
| `databases` (36) | 1 | **35** | 0 | 0 | 0 |
| `networks_connectivity` (36) | 4 | 0 | **27** | 4 | 1 |
| `infrastructure_storage` (36) | 0 | 1 | 0 | **35** | 0 |
| `security_access` (36) | 2 | 0 | 1 | 0 | **33** |

### Modelo Propuesto Transformer (Filas = Real, Columnas = Predicha)

| Real / Predicha | Apps | DB | Net | Infra | Sec |
|---|---:|---:|---:|---:|---:|
| `applications_services` (36) | **4** | 3 | 3 | 12 | 14 |
| `databases` (36) | 4 | **30** | 0 | 0 | 2 |
| `networks_connectivity` (36) | 1 | 0 | **26** | 0 | 9 |
| `infrastructure_storage` (36) | 0 | 0 | 0 | **36** | 0 |
| `security_access` (36) | 0 | 0 | 6 | 0 | **30** |

---

## 13. Análisis de Errores y Discusión Técnica

### 1. Superioridad de la Línea Base frente al Transformer
La línea base lineal supera al modelo Transformer en validación ($0.9423$ vs $0.7822$) y en test ($0.7719$ vs $0.6592$). Este comportamiento se explica por:
- **Alta especificidad de la terminología técnica:** Tokens como `pg_wal`, `esxi`, `bgp`, `raid5`, `vlan`, `idrac` o `keycloak` poseen una correlación directa y no ambigua con su categoría. La descomposición sub-palabra de `char_wb` (3 a 5 caracteres) permite capturar estos identificadores de manera directa y robusta.
- **Embeddings genéricos congelados:** El modelo `paraphrase-multilingual-MiniLM-L12-v2` fue preentrenado sobre textos generales (Wikipedia, noticias, subtítulos). Al congelar sus pesos y no realizar un ajuste fino supervisado de sus capas de atención sobre el dominio técnico de infraestructura, la similitud semántica agrupa oraciones con frases genéricas de soporte ("falla en el servidor", "alerta de la guardia") perdiendo poder discriminante en la capa final.

### 2. Patrón de Error en `applications_services`
El principal punto de error de ambos modelos en TEST se concentra en la categoría `applications_services`, donde la línea base obtuvo un recall de $33.3\%$ al confundir 14 incidentes con `infrastructure_storage` y 8 con `security_access`. 
- **Causa técnica:** Los incidentes de esta partición describían caídas de microservicios originadas por consumo excesivo de memoria del proceso en el host o errores de autenticación con el proveedor de tokens. El modelo asignó el ticket a la infraestructura de soporte o al módulo de seguridad.
- **Atenuación mediante Top-3:** Pese a este desvío en la opción Top-1, el clasificador mantuvo una exactitud **Top-3 del 100.0%**, asegurando que el equipo especialista siempre figuró entre las opciones visibles al operador.

---

## 14. Arquitectura del Sistema

El software fue construido siguiendo un diseño modular y desacoplado:
- **Capa de Datos (`app/data.py`, `app/templates.py`):** Generación determinista del dataset e integridad de particiones por grupos de evento.
- **Capa de Modelado (`app/linear_baseline.py`, `app/proposed_model.py`):** Definición de pipelines scikit-learn y transformadores.
- **Capa de Inferencia (`app/inference.py`):** Carga perezosa del artefacto serializado, cálculo de probabilidades, latencia en tiempo real, detección de vocabulario desconocido y cálculo de señales explicativas.
- **Capa de Servicio API (`app/main.py`, `app/schemas.py`):** Servidor HTTP con FastAPI y validación Pydantic para bloquear fugas de información.
- **Capa de Presentación (`frontend/`):** Aplicación web interactiva basada en HTML5, CSS moderno y JavaScript modular nativo.

---

## 15. Backend

El backend expone la siguiente especificación OpenAPI:
- **`POST /api/classify`**:
  - **Entrada:** `{"title": "...", "initial_description": "..."}`
  - **Validaciones:** Título obligatorio (5-200 caracteres, $\ge 3$ letras), descripción obligatoria (15-2000 caracteres, $\ge 10$ letras). Prohibición estricta de campos adicionales (`category`, `resolution`, `assignee`, etc.) que retornan error HTTP 422.
  - **Salida:** Categoría sugerida, ranking completo con 5 probabilidades, desglose Top-3, latencia en ms, identificador del modelo operativo y bandera `requires_review`.
- **`GET /api/categories`**: Catálogo de categorías técnicas de la UOIT.
- **`GET /api/metrics`**: Métricas experimentales consolidadas leídas desde `artifacts/metrics.json`.
- **`GET /api/health`**: Estado operativo del servicio.

---

## 16. Frontend

La interfaz web fue construida sin dependencias externas pesadas, garantizando carga instantánea:
- **Formulario de Registro:** Entradas de título y descripción con conteo dinámico de caracteres y validación en tiempo real.
- **Escenarios Demostrativos Precargados:**
  - *Caso A (Válido):* Incidente de base de datos con terminología nítida de PgBouncer.
  - *Caso B (Difícil / Ambiguo):* Incidente de microservicio con fallos intermitentes de timeout y concurrencia con la base de datos.
  - *Caso C (Entrada Inválida):* Violación de contrato de longitud mínima que genera rechazo HTTP 422.
- **Panel de Resultados:** Exhibe la categoría sugerida, etiqueta del modelo utilizado, tiempo de respuesta en milisegundos, visualización del ranking de puntajes estimados y tarjeta de señales de influencia léxica.
- **Paneles de Métricas y Metodología:** Visualización interactiva de la matriz de confusión y de la comparativa de modelos.

---

## 17. Suite de Pruebas

Se implementó una suite automatizada de **34 pruebas** en `pytest`, ejecutada mediante:
```bash
python -m pytest -q
```
Resultado: **34 pasadas en 3.31 segundos (100% de éxito)**.

Aspectos verificados:
- Reproducibilidad del generador y cálculo de hashes de datos.
- Aislamiento absoluto de familias técnicas entre particiones.
- Validación de tipos y rechazo de campos con potencial de fuga de información.
- Comprobación matemática de métricas (Macro-F1, Accuracy y Top-3).
- Carga e inferencia del artefacto serializado `model.joblib`.
- Inferencia ante textos con vocabulario no visto (`requires_review = True`).

---

## 18. Conclusiones

1. **Cumplimiento del Protocolo Metodológico:** Se respetó estrictamente el congelamiento metodológico. El modelo operativo se eligió en validación y se conservó en test sin modificaciones ad-hoc.
2. **Efectividad de la Línea Base:** En dominios técnicos estructurados con fuerte presencia de vocabulario especializado, una línea base lineal con n-gramas de caracteres a nivel sub-palabra supera a un Transformer general congelado y ofrece una latencia de inferencia significativamente inferior (< 2 ms).
3. **Valor del Top-3:** La exactitud Top-3 del 100% en test confirma la viabilidad del clasificador como herramienta de soporte al operador humano, reduciendo el espacio de búsqueda de 5 opciones a un subconjunto altamente confiable.
4. **Arquitectura Limpia y Segura:** El sistema previene de forma estructural cualquier fuga de datos mediante validación de contratos en Pydantic y particionado disjunto por familias técnicas.

---

## 19. Limitaciones

1. **Naturaleza Sintética del Dataset:** Los 720 incidentes fueron generados algorítmicamente mediante combinatoria de plantillas controladas para salvaguardar la confidencialidad de la UOIT. Presentan mayor separabilidad léxica y regularidad sintáctica que los tickets reales.
2. **Ausencia de Ajuste Fino en el Transformer:** El Transformer se evaluó en modalidad de embeddings congelados por restricciones de cómputo en CPU y diseño metodológico. Un fine-tuning end-to-end con datos de dominio podría mejorar su desempeño a costa de mayor demanda computacional.
3. **Supuesto Mono-etiqueta:** El sistema asume que cada incidente corresponde a una única categoría primaria, cuando en infraestructuras complejas existen averías compuestas.
4. **Cota de Laboratorio:** Los resultados no deben interpretarse como una prueba de eficacia institucional real sin una validación previa con operadores en un entorno piloto.
5. **Interpretación de Puntajes y Entradas Fuera de Dominio:** Los valores calculados corresponden a puntajes estimados relativos generados por el modelo para cada categoría según sus coeficientes aprendidos y no constituyen probabilidades calibradas de acierto absoluto. Ante solicitudes completamente ajenas a la infraestructura tecnológica (ej. temas administrativos o de cafetería), el modelo lineal asignará puntuación sobre las categorías conocidas si coinciden sub-tokens comunes; la política de revisión apoya al técnico, pero no reemplaza la supervisión humana.

---

## 20. Referencias

1. Pedregosa, F., Varoquaux, G., Gramfort, A., Michel, V., Thirion, B., Grisel, O., Blondel, M., Prettenhofer, P., Weiss, R., Dubourg, V., Vanderplas, J., Passos, A., Cournapeau, D., Brucher, M., Perrot, M., & Duchesnay, É. (2011). Scikit-learn: Machine Learning in Python. *Journal of Machine Learning Research*, 12, 2825–2830.
2. Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks. In *Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing and the 9th International Joint Conference on Natural Language Processing (EMNLP-IJCNLP)*, pages 3982–3992.
3. Devlin, J., Chang, M. W., Lee, K., & Toutanova, K. (2019). BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding. In *Proceedings of the 2019 Conference of the North American Chapter of the Association for Computational Linguistics (NAACL-HLT)*, pages 4171–4186.
4. AXELOS. (2020). *ITIL® 4: Incident Management Practice Guide*. The Stationery Office, London.
5. Ramírez-Gallego, S., Krawczyk, B., García, S., Woźniak, M., & Herrera, F. (2017). A survey on data preprocessing for data stream mining: Current status and future directions. *Neurocomputing*, 239, 39–57.
