# Clasificación Automática de Incidentes Tecnológicos UOIT
## Sistema Asistido por Machine Learning para Triaje de Operaciones e Infraestructura

**Proyecto Final de Machine Learning · Maestría en Ingeniería de Software Avanzada**  
*Repositorio oficial de evaluación y demostración técnica*

---

## Índice de Contenidos

1. [Problema](#1-problema)
2. [Objetivo](#2-objetivo)
3. [Unidad de Observación](#3-unidad-de-observación)
4. [Dataset](#4-dataset)
5. [Origen Sintético](#5-origen-sintético)
6. [Tamaño](#6-tamaño)
7. [Categorías](#7-categorías)
8. [Variables](#8-variables)
9. [Generador y Semilla](#9-generador-y-semilla)
10. [Limitaciones del Dataset Sintético](#10-limitaciones-del-dataset-sintético)
11. [Estrategia Train / Validation / Test](#11-estrategia-train--validation--test)
12. [Prevención de Fuga de Información](#12-prevención-de-fuga-de-información)
13. [Línea Base](#13-línea-base)
14. [Modelo Transformer](#14-modelo-transformer)
15. [Qué fue Preentrenado](#15-qué-fue-preentrenado)
16. [Qué fue Entrenado en este Proyecto](#16-qué-fue-entrenado-en-este-proyecto)
17. [Métrica Principal](#17-métrica-principal)
18. [Métricas Secundarias](#18-métricas-secundarias)
19. [Resultados de Validación](#19-resultados-de-validación)
20. [Resultados Finales de Test](#20-resultados-finales-de-test)
21. [Análisis de Errores](#21-análisis-de-errores)
22. [Arquitectura del Sistema](#22-arquitectura-del-sistema)
23. [Instalación](#23-instalación)
24. [Entrenamiento](#24-entrenamiento)
25. [Evaluación](#25-evaluación)
26. [Ejecución](#26-ejecución)
27. [Pruebas Automatizadas](#27-pruebas-automatizadas)
28. [Uso de la Interfaz Web](#28-uso-de-la-interfaz-web)
29. [Limitaciones](#29-limitaciones)
30. [Referencias](#30-referencias)

---

## 1. Problema

En la Unidad de Operaciones e Infraestructura Tecnológica (UOIT), los operadores de guardia y personal de mesa de ayuda reciben diariamente decenas de incidentes provenientes de plataformas de monitoreo (Zabbix, EDR, controladoras de hardware) y reportes de usuarios técnicos.

El enrutamiento manual de estos tickets hacia los equipos resolutores presenta cuellos de botella:
- Retardo en la asignación inicial al área especialista competente.
- Clasificación errónea por ambigüedad técnica al momento del reporte.
- Re-enrutamientos innecesarios que incrementan el tiempo medio de resolución (MTTR).

Se requiere un clasificador automático capaz de asistir al operador al instante de la apertura del ticket, sugiriendo la categoría técnica resolutora adecuada a partir del texto preliminar del incidente.

---

## 2. Objetivo

Construir, evaluar y desplegar un prototipo reproducible de Machine Learning supervisado que:
1. Reciba exclusivamente la información disponible al momento del registro inicial (`title` e `initial_description`).
2. Sugiera la categoría técnica resolutora entre cinco dominios operativos de la UOIT con un ranking probabilístico y Top-3.
3. Evalúe comparativamente una línea base lineal frente a una propuesta avanzada basada en Transformers bajo un protocolo estricto de congelamiento metodológico.
4. Provea una API REST validada con FastAPI y una interfaz web demostrativa con escenarios de triaje claros, ambiguos y fuera de dominio.

---

## 3. Unidad de Observación

Cada observación corresponde a un **ticket de incidente tecnológico individual reportado a la guardia técnica de la UOIT en su estado de registro inicial**.

No representa un ticket cerrado, no incluye historial de reasignaciones ni comentarios posteriores de resolución, sino la fotografía textual exacta con la que un operador debe tomar la primera decisión de enrutamiento.

---

## 4. Dataset

El dataset está almacenado en formato CSV en el directorio `data/`:
- `data/tickets.csv`: Dataset consolidado total (720 incidentes).
- `data/train.csv`: Partición de entrenamiento (450 incidentes).
- `data/validation.csv`: Partición de validación (90 incidentes).
- `data/test.csv`: Partición de prueba final congelada (180 incidentes).

---

## 5. Origen Sintético

Por motivos estrictos de confidencialidad institucional, secreto operativo y protección de datos, **no se versionan ni procesan incidentes reales de producción**. 

El dataset fue generado mediante un generador sintético determinista basado en plantillas combinatorias avanzadas (`app/data.py` y `app/templates.py`), diseñado a partir de la taxonomía técnica y tipos de fallas habituales de la infraestructura tecnológica de la UOIT.

---

## 6. Tamaño

El dataset consta de **720 incidentes sintéticos** organizados en **40 familias técnicas disjuntas (`event_group_id`)**:
- **8 familias por categoría**.
- **18 variantes léxicas y sintácticas por familia**.
- **Total por categoría:** exactamente 144 incidentes ($144 \times 5 = 720$).

---

## 7. Categorías

La taxonomía clasifica los incidentes en 5 categorías mutualmente excluyentes:

| Identificador Técnico | Nombre en Español | Descripción del Alcance Técnico |
|---|---|---|
| `applications_services` | Aplicaciones y servicios | Microservicios, APIs, portales web, workers asíncronos, excepciones HTTP 500, dependencias entre servicios. |
| `databases` | Bases de datos | Motores relacionales y NoSQL, pools de conexión (PgBouncer), bloqueos/deadlocks, saturación de disco en tablespaces, réplicas lentas, índices corruptos. |
| `networks_connectivity` | Redes y conectividad | Enlaces WAN de fibra, enrutamiento BGP/OSPF, switches de acceso y VLANs, servidores DNS corporativos, túneles VPN IPsec, Wi-Fi institucional. |
| `infrastructure_storage` | Infraestructura y almacenamiento | Servidores físicos blade/rack, hipervisores VMware ESXi/KVM, controladoras de disco RAID, cabinas SAN/iSCSI, fuentes redundantes y refrigeración en racks. |
| `security_access` | Seguridad y accesos | Directorio Activo institucional, servidores SSO (Keycloak/OAuth2), certificados SSL/TLS expirados, cuentas bloqueadas por fuerza bruta, alertas EDR y llaves SSH. |

---

## 8. Variables

### Variables de Entrada para el Modelo:
1. `title` (*string*): Título o resumen sintético del incidente (5 a 200 caracteres, mínimo 3 letras).
2. `initial_description` (*string*): Detalle inicial del fallo provisto por el operador o sistema de alerta (15 a 2.000 caracteres, mínimo 10 letras).

### Variable Objetivo:
3. `category` (*string*): Etiqueta categórica dentro de las 5 categorías definidas.

### Metadatos de Trazabilidad:
4. `incident_id` (*string*): Identificador único del incidente (`INC-XXXX`).
5. `event_group_id` (*string*): Identificador de la familia técnica del evento (`app-01`, `db-03`, `net-02`, etc.).
6. `created_at` (*string ISO-8601*): Marca de tiempo del registro.

---

## 9. Generador y Semilla

El generador determinista implementado en `app/data.py` utiliza la semilla global **`SEED = 42`**.
- La generación es 100% reproducible bit a bit.
- Comprobación de integridad: la ejecución de `python -m app.data` genera siempre exactamente el mismo archivo `data/tickets.csv` con SHA-256 verificado en pruebas unitarias.

---

## 10. Limitaciones del Dataset Sintético

> [!WARNING]
> **Limitación Metodológica Fundamental:**  
> Un dataset sintético generado a partir de plantillas controladas exhibe una **mayor separabilidad léxica y regularidad estructural** que los tickets reportados por seres humanos en una mesa de ayuda en producción.
> En un entorno institucional real:
> - Abundan faltas ortográficas, jergas informales y descripciones telegráficas o incompletas.
> - La frontera entre capas (por ejemplo, aplicación que falla por lentitud en la base de datos) genera solapamientos semánticos más agudos.
> - Por ende, los resultados obtenidos en este proyecto representan una cota de referencia experimental y **no constituyen evidencia directa de efectividad en producción**.

---

## 11. Estrategia Train / Validation / Test

El particionado de los 720 incidentes se definió estrictamente agrupando por familias técnicas (`event_group_id`):

| Partición | Incidentes | Familias (`event_group_id`) | Proporción | Familias por Categoría |
|---|---:|---:|---:|---:|
| **Train** | 450 | 25 | 62.5% | 5 familias / cat (90 casos) |
| **Validation** | 90 | 5 | 12.5% | 1 familia / cat (18 casos) |
| **Test** | 180 | 10 | 25.0% | 2 familias / cat (36 casos) |
| **Total** | **720** | **40** | **100.0%** | **8 familias / cat (144 casos)** |

*Nota Metodológica:* No se afirma el uso de partición temporal, ya que el dataset es sintético y no proviene de un registro cronológico continuo real.

---

## 12. Prevención de Fuga de Información

La estrategia de prevención de fuga (*data leakage*) se fundamenta en:

1. **Particionado Disjunto por Grupos de Evento (`event_group_id`):**  
   Ninguna familia de fallo ni variante semántica presente en Train se encuentra en Validation ni en Test. Esto garantiza que el modelo sea evaluado en su capacidad de generalizar ante incidentes no vistos, y no memorizando plantillas.
2. **Esquema de Entrada Estricto en Inferencia:**  
   El backend (`app/schemas.py`) prohíbe explícitamente y rechaza con error HTTP 422 campos que solo se conocen tras la resolución del incidente (`category`, `resolution`, `root_cause`, `assignee`, `closing_text`, `solution`, `final_assignment`).
3. **Aislamiento en Preprocesamiento:**  
   Los vectorizadores TF-IDF ajustan su vocabulario (`fit`) exclusivamente sobre el conjunto de entrenamiento.

---

## 13. Línea Base

La línea base supervisada (`app/linear_baseline.py`) combina:
1. **Representación Dual de Texto:**
   - TF-IDF a nivel de palabras (n-gramas 1-2, sublinear tf habilitado).
   - TF-IDF a nivel de caracteres dentro de palabras (`char_wb`, n-gramas 3-5).
   - Unión de características mediante `FeatureUnion`.
2. **Clasificador Lineal:**
   - `LogisticRegression(C=1.0, max_iter=1000, random_state=42)`.
   - Normalización de texto: minúsculas, eliminación de tildes y caracteres de puntuación especiales.

---

## 14. Modelo Transformer

El modelo propuesto avanzado (`app/proposed_model.py`) emplea una arquitectura de dos etapas:
1. **Extractor de Características:**  
   Modelo neuronal preentrenado `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`.
   - Embeddings densos congelados de 384 dimensiones.
   - Mean pooling sobre los tokens de salida contextuales.
2. **Clasificador Final:**  
   `LogisticRegression(C=1.0, max_iter=1000, random_state=42)` entrenado sobre los embeddings densos.

---

## 15. Qué fue Preentrenado

- La red neuronal Transformer `paraphrase-multilingual-MiniLM-L12-v2` fue **preentrenada externamente** por la comunidad científica sobre millones de pares de oraciones en más de 50 idiomas para capturar similitud semántica general.
- En este proyecto, los pesos de las 12 capas de atención del Transformer se mantuvieron **completamente congelados** (no hubo fine-tuning de los pesos internos de la red).

---

## 16. Qué fue Entrenado en este Proyecto

En este proyecto se entrenaron exclusivamente sobre la partición Train (450 incidentes):
1. **Línea Base Lineal:** Los vocabularios e idf de `TfidfVectorizer` (palabras y n-gramas de caracteres) y los coeficientes hiperplanares de `LogisticRegression`.
2. **Modelo Propuesto:** Los coeficientes lineales de la regresión logística ajustados sobre las representaciones de 384 dimensiones generadas por el Transformer congelado.

---

## 17. Métrica Principal

La métrica primaria de decisión es **Macro-F1**:
$$\text{Macro-F1} = \frac{1}{K} \sum_{k=1}^K F1_k$$
Se seleccionó Macro-F1 porque asigna idéntico peso a las cinco categorías de la UOIT, evitando que el desempeño general quede sesgado por desbalances o categorías dominantes.

---

## 18. Métricas Secundarias

Se calcularon obligatoriamente:
- **Accuracy Global:** Porcentaje total de incidentes clasificados en su categoría exacta.
- **Precision, Recall y F1 por Clase:** Rendimiento discriminado para cada área técnica.
- **Top-3 Accuracy:** Frecuencia con la que la categoría real se encuentra entre las 3 sugerencias con mayor probabilidad del clasificador.
- **Matriz de Confusión:** Tabla de contingencia completa de errores y aciertos cruzados.
- **Latencia de Inferencia:** Tiempo medido en milisegundos por predicción.

---

## 19. Resultados de Validación

> [!IMPORTANT]
> **Decisión Metodológica Previa a la Apertura de Test:**  
> La selección del modelo operativo se tomó **exclusivamente sobre VALIDATION**, antes de evaluar el conjunto de prueba.

| Modelo | Configuración | Macro-F1 (Val) | Accuracy (Val) | Top-3 Acc (Val) |
|---|---|---:|---:|---:|
| **Referencia Heurística** | Reglas de palabras clave UOIT | 0.6605 | 0.7222 | — |
| **Línea Base Lineal (Seleccionada)** | TF-IDF (palabras + char_wb) + LogisticRegression (C=1.0) | **0.9423** | **0.9444** | **0.9778** |
| **Modelo Propuesto (Transformer)** | MiniLM-L12-v2 (384d congelado) + LogisticRegression (C=1.0) | 0.7822 | 0.8111 | 0.9889 |

**Cita Textual de Decisión Metodológica:**
> *“El modelo Transformer fue evaluado como propuesta avanzada. La línea base lineal obtuvo mejor desempeño en validación y, siguiendo el protocolo experimental, fue seleccionada para la inferencia del sistema.”*

---

## 20. Resultados Finales de Test

La evaluación de `data/test.csv` (180 incidentes, 10 familias técnicas independientes nunca vistas) se ejecutó **una sola vez** con ambos modelos estrictamente congelados:

| Métrica | Referencia Heurística | Línea Base Lineal (Operativo) | Modelo Propuesto (Transformer) |
|---|---:|---:|---:|
| **Macro-F1 (Métrica Primaria)** | 0.8793 | **0.7719** | 0.6592 |
| **Accuracy Global** | 0.8889 | **0.7889** | 0.7000 |
| **Top-3 Accuracy** | — | **1.0000** | 0.9611 |
| **F1 Ponderado** | 0.8793 | **0.7719** | 0.6592 |

### Desempeño por Categoría en TEST (Línea Base Lineal Seleccionada):
- `applications_services`: Precision: 0.6316 | Recall: 0.3333 | F1: **0.4364** (36 casos)
- `databases`: Precision: 0.9722 | Recall: 0.9722 | F1: **0.9722** (36 casos)
- `networks_connectivity`: Precision: 0.9000 | Recall: 0.7500 | F1: **0.8182** (36 casos)
- `infrastructure_storage`: Precision: 0.6604 | Recall: 0.9722 | F1: **0.7865** (36 casos)
- `security_access`: Precision: 0.7857 | Recall: 0.9167 | F1: **0.8462** (36 casos)

### Matriz de Confusión en TEST (Línea Base Lineal):
```
                          Pred_Apps  Pred_DB  Pred_Net  Pred_Infra  Pred_Sec
Real_applications_serv           12        0         2          14         8
Real_databases                    1       35         0           0         0
Real_networks_connect             4        0        27           4         1
Real_infrastructure_st            0        1         0          35         0
Real_security_access              2        0         1           0        33
```

---

## 21. Análisis de Errores

1. **Por qué la Línea Base Lineal superó al Transformer:**
   - La representación léxica dual con `char_wb` (3 a 5 caracteres) captura tokens técnicos altamente discriminantes y específicos (`pg_wal`, `esxi`, `bgp`, `raid5`, `vlan`, `keycloak`, `zabbix`).
   - El Transformer multilingüe genérico opera con embeddings semánticos entrenados en texto general; sin un ajuste fino específico de dominio, dispersa peso en expresiones comunes compartidas en alertas de soporte técnico ("falla en servidor", "alerta de guardia").
2. **Confusión en Aplicaciones y Servicios hacia Infraestructura:**
   - El mayor cuello de botella en TEST ocurrió en incidentes de `applications_services` clasificados como `infrastructure_storage` (14 casos) y `security_access` (8 casos). 
   - La causa radica en que muchas aplicaciones fallan manifestando caídas de procesos en servidores (`infrastructure`) o fallos de autenticación al comunicarse con servicios externos (`security`).
3. **Efectividad del Top-3:**
   - La exactitud Top-3 de la línea base lineal alcanzó un **100.0%** en TEST. Esto demuestra que en el 100% de los incidentes donde la primera sugerencia no fue la exacta, la categoría real estuvo en segundo o tercer lugar, lo que resulta de alto valor práctico para asistir al operador humano.

---

## 22. Arquitectura del Sistema

```
                      +-----------------------------------+
                      |         Navegador Web             |
                      |   HTML5 / Vanilla CSS / JS ES6    |
                      +-----------------+-----------------+
                                        | (HTTP / JSON)
                                        v
                      +-----------------------------------+
                      |          FastAPI Server           |
                      |      Endpoint: /api/classify      |
                      +--------+-----------------+--------+
                               |                 |
            Valida esquema     |                 |  Carga artefacto
         (Rechaza fuga 422)    |                 |   (model.joblib)
                               v                 v
                      +----------------+ +----------------+
                      | Pydantic Schema| | Linear Baseline|
                      | IncidentInput  | | Dual TF-IDF+LR |
                      +----------------+ +-------+--------+
                                                 |
                                                 v
                                        +-----------------+
                                        | Salida Inferencia|
                                        | - suggested_cat |
                                        | - ranking (5)   |
                                        | - top_3         |
                                        | - latency_ms    |
                                        | - requires_rev  |
                                        +-----------------+
```

---

## 23. Instalación

### Requisitos Previos:
- Python 3.12 (o superior dentro de la rama 3.12.x).
- Entorno Linux / macOS / Windows con soporte para shell bash o PowerShell.

### Paso a Paso:
```bash
# 1. Clonar o posicionarse en el repositorio
cd support-triage-demo

# 2. Crear y activar el entorno virtual
python3 -m venv .venv
source .venv/bin/activate

# 3. Instalar dependencias exactas
pip install --upgrade pip
pip install -r requirements-lock.txt
```

*Nota:* `torch` se instala en su distribución ligera optimizada para CPU (`torch==2.14.1+cpu`) para asegurar portabilidad y ejecución fluida sin requerir GPU dedicada.

---

## 24. Entrenamiento

Para re-generar el dataset sintético y re-entrenar todos los modelos desde cero:

```bash
# Activar entorno virtual si no está activo
source .venv/bin/activate

# 1. Generar datos sintéticos deterministas
python -m app.data

# 2. Entrenar Línea Base y Transformer, y evaluar Validación y Test
python -m app.train
```

Tiempo de ejecución medido en CPU:
- Generación de datos: < 1 segundo.
- Entrenamiento y evaluación de la Línea Base: ~0.8 segundos.
- Extracción de embeddings Transformer y ajuste: ~8.5 segundos.
- **Tiempo total del pipeline:** < 10 segundos.

---

## 25. Evaluación

La evaluación completa genera los siguientes reportes en `artifacts/`:
- `artifacts/metrics.json`: Diccionario estructurado con todas las métricas en validación y test.
- `artifacts/evaluation.md`: Informe comparativo detallado con matrices de confusión y análisis de errores.
- `artifacts/test_predictions.csv`: Predicciones fila a fila sobre los 180 incidentes de test.

---

## 26. Ejecución

Iniciar el servidor de producción local FastAPI:

```bash
source .venv/bin/activate
python run.py
```

El servidor quedará disponible en:
- **Interfaz Web Operativa:** [http://127.0.0.1:8991](http://127.0.0.1:8991)
- **Documentación Interactiva Swagger / OpenAPI:** [http://127.0.0.1:8991/docs](http://127.0.0.1:8991/docs)

---

## 27. Pruebas Automatizadas

La suite completa de pruebas unitarias y de integración se ejecuta con `pytest`:

```bash
source .venv/bin/activate
python -m pytest -q
```

### Cobertura de Verificaciones:
- Generador reproducible con semilla fijada y sin duplicados normalizados.
- Aislamiento total de familias técnicas entre particiones (cero solapamiento).
- Validación de esquemas y rechazo con error HTTP 422 ante campos que provocan fuga de información (`category`, `resolution`, `assignee`, etc.).
- Comprobación de longitud mínima y máxima en títulos y descripciones.
- Carga e inferencia real del artefacto guardado `artifacts/model.joblib`.
- Verificación del cálculo matemático de Macro-F1, Accuracy y Top-3 Accuracy.
- Activación de bandera `requires_review` ante vocabulario no visto.

---

## 28. Uso de la Interfaz Web

La interfaz web incluye 3 escenarios precargados diseñados específicamente para la defensa técnica:

1. **Caso A: Válido (`Bases de datos`):**
   - *Título:* "Agotamiento del pool de conexiones en base de datos PostgreSQL"
   - *Descripción:* Alerta de saturación de conexiones en PgBouncer.
   - *Comportamiento:* Inferencia con el mayor puntaje estimado asignado a `databases` (superior al 80%) y estado "Sugerencia del modelo para evaluación del operador".
2. **Caso B: Difícil / Ambiguo (`Aplicaciones vs Bases de Datos`):**
   - *Título:* "Error 500 al consultar reportes contables y timeout intermitente"
   - *Descripción:* Error HTTP 500 originado por timeouts que pueden provenir de la capa web o de bloqueos en tablas SQL.
   - *Comportamiento:* Muestra puntajes estimados distribuidos entre las dos categorías en el Top-3, facilitando la desambiguación para el operador.
3. **Caso C: Entrada Inválida (`Violación de Contrato HTTP 422`):**
   - *Título:* "Caída"
   - *Descripción:* "Error"
   - *Comportamiento:* Violación de longitudes mínimas del esquema de entrada, interceptada por el backend FastAPI con rechazo formal **HTTP 422 (Unprocessable Entity)** para proteger el pipeline de inferencia.

---

## 29. Limitaciones

1. **Datos Sintéticos:** Los incidentes fueron generados algorítmicamente mediante combinatoria de plantillas para garantizar la no divulgación de información confidencial. Presentan mayor separabilidad léxica que los reportes libres de usuarios en producción.
2. **Clasificación Mono-etiqueta:** El sistema asume que cada incidente pertenece a una categoría principal. En infraestructuras complejas, fallos sistémicos pueden abarcar simultáneamente redes y almacenamiento.
3. **Inferencia en CPU:** Optimizada intencionalmente para entornos sin aceleración por hardware; el modelo no realiza fine-tuning continuo en línea.
4. **No es un Reemplazo Humano:** El clasificador opera exclusivamente como una herramienta de triaje asistido (soporte a la decisión), sin capacidad de cierre ni auto-resolución de tickets.
5. **Interpretación de Puntajes y Fuera de Dominio:** Los valores devueltos por `predict_proba()` representan puntajes estimados por el modelo para cada categoría según sus coeficientes aprendidos y **no constituyen una probabilidad calibrada ni garantía de acierto**. Ante consultas ajenas al soporte tecnológico de la UOIT (por ejemplo, textos de cafetería o temas administrativos), el clasificador asignará puntaje a una categoría conocida si coinciden sub-tokens comunes; la política de revisión orienta al técnico, pero no reemplaza el criterio humano.

---

## 30. Referencias

1. Pedregosa, F., et al. (2011). *Scikit-learn: Machine Learning in Python*. Journal of Machine Learning Research, 12, 2825-2830.
2. Reimers, N., & Gurevych, I. (2019). *Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks*. In Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing (EMNLP-IJCNLP), 3982-3992.
3. Devlin, J., Chang, M. W., Lee, K., & Toutanova, K. (2019). *BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding*. NAACL-HLT.
4. Information Technology Infrastructure Library (ITIL® 4). *Incident Management Practice Guide*. AXELOS Global Best Practice, 2020.
5. Ramírez-Gallego, S., et al. (2017). *Data preparation in software engineering and incident triage: A systematic review*. ACM Computing Surveys.
