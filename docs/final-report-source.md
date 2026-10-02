# Informe Técnico Final: Clasificación Inteligente de Incidentes Tecnológicos mediante Machine Learning Supervisado para Triaje Operativo en la UOIT

**Autor:** Juan Serrudo  
**Programa:** Maestría en Ingeniería de Software Avanzada  
**Asignatura:** Proyecto Final de Machine Learning  
**Fecha:** Octubre 2026  
**Repositorio Oficial:** `https://github.com/juan-serrudo/sig-incidentes` (rama `feature/uoit-incident-classifier`)  

---

## 1. Título

**Sistema Asistido de Triaje y Clasificación Automática de Incidentes de Infraestructura Tecnológica utilizando Procesamiento de Lenguaje Natural Supervisado.**

---

## 2. Resumen

En las operaciones de soporte e infraestructura de tecnologías de información, la correcta derivación de incidentes hacia los equipos especialistas es un factor determinante para reducir el tiempo medio de resolución (MTTR). Este trabajo presenta el diseño, evaluación experimental y despliegue de un sistema de Machine Learning supervisado para clasificar tickets de incidentes de la Unidad de Operaciones e Infraestructura Tecnológica (UOIT) en cinco categorías técnicas resolutoras. Empleando un dataset sintético determinista de 720 incidentes estructurados en 40 familias disjuntas para evitar fuga de información (*data leakage*), se compararon tres aproximaciones: una referencia heurística basada en reglas de palabras clave, una línea base lineal con representación dual TF-IDF (palabras y sub-palabras a nivel de caracteres) y una propuesta avanzada basada en embeddings densos congelados de un Transformer multilingüe (`MiniLM-L12-v2`). Siguiendo un estricto protocolo de congelamiento metodológico, la línea base lineal fue seleccionada como modelo operativo exclusivamente a partir de su desempeño en validación (Macro-F1 de 0.9423 frente a 0.7822). En la evaluación final sobre el conjunto de test congelado, la heurística alcanzó un Macro-F1 de 0.8793, la línea base 0.7719 y el Transformer 0.6592, logrando la línea base una exactitud Top-3 del 100.0%. El sistema se encuentra desacoplado en una API REST con FastAPI y una interfaz web interactiva que ofrece soporte al operador de guardia sin sustituir su criterio humano.

---

## 3. Problema

La Unidad de Operaciones e Infraestructura Tecnológica (UOIT) administra plataformas críticas institucionales que comprenden conectividad WAN/LAN, centros de cómputo, hipervisores de virtualización, clústeres de bases de datos relacionales y plataformas de identidad. Diariamente, la mesa de ayuda técnica y el personal de guardia reciben alertas generadas por sistemas de monitoreo automatizado (Zabbix, consolas EDR, controladoras RAID) y solicitudes de usuarios técnicos.

El enrutamiento manual de estos requerimientos hacia las áreas especialistas introduce fricciones operativas:
- **Demoras en el triaje inicial:** Tiempos muertos entre la recepción del ticket y su asignación efectiva.
- **Asignaciones cruzadas erróneas:** Ambigüedad en los síntomas preliminares (por ejemplo, una aplicación web que reporta error 500 por bloqueos en el motor relacional suele derivarse erróneamente al equipo de desarrollo).
- **Sobrecarga cognitiva en guardias:** Dificultad para diagnosticar rápidamente con información parcial en turnos nocturnos o de contingencia.

El problema consiste en predecir con rapidez y rigor técnico la categoría resolutora adecuada a partir exclusivamente de los datos preliminares del ticket.

---

## 4. Objetivo

Diseñar, implementar, evaluar experimentalmente y desplegar un sistema prototipo de Machine Learning supervisado que:
1. Clasifique incidentes tecnológicos entre cinco áreas operativas de la UOIT.
2. Utilice exclusivamente la información disponible al momento del registro inicial (`title` e `initial_description`).
3. Evalúe comparativamente una línea base lineal frente a una propuesta neuronal con Transformers bajo congelamiento metodológico.
4. Provea un servicio de inferencia REST en FastAPI con validación rigurosa de contratos y una interfaz web con soporte para escenarios demostrativos claros, ambiguos e inválidos.

---

## 5. Alcance

El proyecto abarca el modelado, validación cruzada agrupada, evaluación en conjunto de prueba independiente y despliegue local demostrativo. Se restringe a la asistencia al operador humano en el momento del triaje (soporte a la decisión). No incluye la auto-resolución ni el cierre automatizado de incidentes en plataformas ITSM de producción.

---

## 6. Unidad de Observación

Cada observación corresponde a un **ticket de incidente tecnológico individual en su estado de registro inicial**, reportado a la guardia de la UOIT.

La observación contiene únicamente la fotografía textual inicial provista por el operador o sistema de alerta antes de cualquier intervención técnica. No contiene diagnósticos posteriores, comentarios de resolución, técnicos asignados ni causas raíz.

---

## 7. Dataset

El dataset consolidado se almacena en `data/tickets.csv` y consta de:
- **Volumen Total:** 720 incidentes en idioma español.
- **Estructura:** 40 familias técnicas disjuntas (`event_group_id`).
- **Balance:** Exactamente 8 familias y 144 incidentes por categoría ($20.0\%$ por clase).
- **Variabilidad:** Cada familia cuenta con 18 variantes léxicas y sintácticas generadas deterministamente.

---

## 8. Origen Sintético y Justificación

Por estrictas políticas de confidencialidad institucional, reserva técnica de infraestructura y protección de datos, **se prohibió el uso directo y la exposición pública de datos reales de producción**.

Para satisfacer los requisitos académicos con el máximo realismo operacional, se construyó un generador sintético determinista basado en plantillas técnicas combinatorias (`app/templates.py` y `app/data.py`). El generador modela la taxonomía de fallos habituales de la UOIT, introduciendo prefijos de monitoreo, núcleos de falla y sufijos de guardia técnica.

---

## 9. Taxonomía de Cinco Categorías

El espacio de salida se modela mediante cinco categorías técnicas mutuamente excluyentes:

| Identificador | Etiqueta en Interfaz | Alcance Tecnológico Principal |
|---|---|---|
| `applications_services` | Aplicaciones y servicios | Microservicios, APIs REST, portales web, workers asíncronos, errores HTTP 500 y dependencias de software. |
| `databases` | Bases de datos | Motores PostgreSQL/Oracle, pools PgBouncer, bloqueos/deadlocks, saturación de tablespaces, réplicas lentas e índices corruptos. |
| `networks_connectivity` | Redes y conectividad | Enlaces WAN de fibra, enrutamiento BGP/OSPF, switches VLAN, servidores DNS corporativos, túneles VPN IPsec y Wi-Fi institucional. |
| `infrastructure_storage` | Infraestructura y almacenamiento | Servidores físicos blade/rack, hipervisores VMware ESXi/KVM, almacenamiento SAN/iSCSI, arreglos RAID y fuentes redundantes. |
| `security_access` | Seguridad y accesos | Directorio Activo, servidores SSO (Keycloak), certificados SSL/TLS expirados, cuentas bloqueadas, alertas EDR y llaves SSH. |

---

## 10. Generación Reproducible y Semilla

El generador determinista implementado en `app/data.py` opera bajo la semilla global **`SEED = 42`**:
- La generación es 100% reproducible bit a bit.
- Comprobación de integridad: El archivo `data/tickets.csv` posee un hash SHA-256 inmutable verificado en pruebas unitarias (`f65c66ec431f95112ab686f94ea067c712f61104e542adc8596f515c3555e0b7`).

---

## 11. Variables Utilizadas

### Variables de Entrada para el Modelo:
1. `title` (*string*): Título o resumen sintético del incidente (5 a 200 caracteres, mínimo 3 letras).
2. `initial_description` (*string*): Detalle inicial del fallo provisto en el reporte (15 a 2.000 caracteres, mínimo 10 letras).

### Variable Objetivo:
3. `category` (*string*): Etiqueta supervisada perteneciente a las cinco categorías técnicas.

### Metadatos de Auditoría:
4. `incident_id` (*string*): Identificador unívoco del ticket (`INC-2026-XXXX`).
5. `event_group_id` (*string*): Identificador de la familia técnica del evento (`app-01`, `db-03`, `net-02`, etc.).
6. `created_at` (*string ISO-8601*): Marca de tiempo del registro.

---

## 12. Prevención de Fuga de Información (*Data Leakage*)

El diseño metodológico previene de forma estructural cualquier fuga de información:
1. **Partición Agrupada por Familias (`Group Split`):** La división de datos se realiza sobre `event_group_id`. Ninguna familia técnica de entrenamiento está presente en validación ni en prueba. Esto evalúa la generalización ante fallos no vistos y descarta la memorización de plantillas.
2. **Esquema Restrictivo en Inferencia:** El esquema Pydantic (`app/schemas.py`) define `extra="forbid"`, rechazando con error **HTTP 422** cualquier campo que revele información posterior al registro (`category`, `resolution`, `root_cause`, `assignee`, `closing_text`, `solution`, `final_assignment`).
3. **Aislamiento en Preprocesamiento:** Los transformadores TF-IDF ajustan su vocabulario (`fit`) exclusivamente sobre la partición de entrenamiento.

---

## 13. División Train / Validation / Test

El particionado de los 720 incidentes respeta la integridad de las 40 familias técnicas:

| Partición | Incidentes | Familias (`event_group_id`) | Proporción | Familias por Categoría |
|---|---:|---:|---:|---:|
| **Train** | 450 | 25 | 62.5% | 5 familias / cat (90 casos) |
| **Validation** | 90 | 5 | 12.5% | 1 familia / cat (18 casos) |
| **Test** | 180 | 10 | 25.0% | 2 familias / cat (36 casos) |
| **Total** | **720** | **40** | **100.0%** | **8 familias / cat (144 casos)** |

---

## 14. Referencia Heurística

Implementada en `app/baseline.py`, utiliza reglas deterministas de conteo de palabras clave técnicas representativas de cada área de la UOIT. El texto se normaliza y gana la categoría con más coincidencias distintas; si no hay coincidencias, se asigna `applications_services` como respaldo. Provee una cota interpretable de comparación.

---

## 15. Línea Base Lineal

Implementada en `app/linear_baseline.py`, integra:
1. **TF-IDF de Palabras:** N-gramas $(1, 2)$, frecuencia mínima de documento `min_df=2`, hasta 5.000 características y frecuencia sublineal (`sublinear_tf=True`).
2. **TF-IDF de Caracteres en Bordes de Palabras (`char_wb`):** N-gramas $(3, 5)$, `min_df=3`, hasta 5.000 características y `sublinear_tf=True`. Captura sub-tokens técnicos especializados (`pg_wal`, `esxi`, `bgp`, `raid5`, `vlan`, `keycloak`).
3. **Unión de Características (`FeatureUnion`):** Matriz dispersa de alta dimensionalidad.
4. **Clasificador:** `LogisticRegression(C=1.0, class_weight="balanced", max_iter=1000, random_state=42)`.

---

## 16. Modelo Transformer

Implementado en `app/proposed_model.py`, utiliza una arquitectura de dos etapas:
1. **Extractor de Características:** Red neuronal preentrenada `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (12 capas, embeddings densos de 384 dimensiones mediante *mean pooling* normalizado).
2. **Clasificador Final:** `LogisticRegression(C=1.0, class_weight="balanced", max_iter=1000, random_state=42)` entrenado sobre los embeddings densos.

---

## 17. Qué Componente es Preentrenado

- La red Transformer multilingüe `MiniLM-L12-v2` fue **preentrenada externamente** sobre grandes corpus textuales para capturar relaciones semánticas generales en más de 50 idiomas.
- En este proyecto, los pesos internos de las 12 capas de atención se mantuvieron **completamente congelados** (*frozen*), operando estrictamente como extractor de representaciones vectoriales densas.

---

## 18. Qué Componente fue Entrenado en este Proyecto

Sobre la partición Train (450 incidentes) se entrenaron exclusivamente:
1. **En la Línea Base:** El vocabulario y ponderaciones IDF del vectorizador dual (`FeatureUnion`) y los coeficientes hiperplanares del clasificador `LogisticRegression`.
2. **En el Modelo Propuesto:** Los coeficientes lineales de la regresión logística ajustados sobre las representaciones de 384 dimensiones generadas por el Transformer congelado.

---

## 19. Métrica Principal: Macro-F1

La métrica primaria de decisión es **Macro-F1**:
$$\text{Macro-F1} = \frac{1}{K}\sum_{k=1}^K \frac{2 \cdot P_k \cdot R_k}{P_k + R_k}$$
Se seleccionó Macro-F1 porque pondera con idéntico rigor a las cinco categorías de la UOIT, garantizando que el rendimiento no quede enmascarado por áreas dominantes ni desbalances operativos.

---

## 20. Métricas Complementarias

- **Accuracy Global:** Porcentaje total de incidentes correctamente clasificados.
- **Precision, Recall y F1 por Clase:** Análisis detallado del desempeño discriminado por área resolutora.
- **Top-3 Accuracy:** Frecuencia con la que la categoría real se encuentra entre las 3 sugerencias con mayor puntaje estimado.
- **Matriz de Confusión:** Tabla cruzada de contingencia entre clases reales y predichas.
- **Latencia de Inferencia:** Tiempo medido en milisegundos en CPU por predicción.

---

## 21. Protocolo de Selección usando VALIDATION

> [!IMPORTANT]
> **Decisión Metodológica Previa a la Apertura de Test:**  
> La selección del modelo operativo se tomó **exclusivamente sobre VALIDATION (90 incidentes)**, antes de evaluar el conjunto de prueba.

### Resultados en Validación:

| Modelo | Configuración | Macro-F1 (Val) | Accuracy (Val) | Top-3 Acc (Val) |
|---|---|---:|---:|---:|
| **Referencia Heurística** | Reglas léxicas UOIT | 0.6605 | 0.7222 | — |
| **Línea Base Lineal (Seleccionada)** | Dual TF-IDF + LogisticRegression ($C=1.0$) | **0.9423** | **0.9444** | **0.9778** |
| **Modelo Propuesto (Transformer)** | MiniLM-L12-v2 (384d congelado) + LogisticRegression | 0.7822 | 0.8111 | 0.9889 |

**Decisión:** La línea base lineal superó al Transformer en validación (Macro-F1 0.9423 frente a 0.7822) y fue seleccionada para operar el sistema en `artifacts/model.joblib`.

---

## 22. Resultados Finales de TEST Congelado

La evaluación sobre `data/test.csv` (180 incidentes, 10 familias independientes nunca vistas) se ejecutó **una sola vez** con ambos modelos estrictamente congelados:

---

## 23. Tabla Comparativa de los Tres Enfoques en TEST

| Métrica | Referencia Heurística | Línea Base Lineal (Operativo) | Modelo Propuesto (Transformer) |
|---|---:|---:|---:|
| **Macro-F1 (Métrica Primaria)** | **0.8793** | **0.7719** | 0.6592 |
| **Accuracy Global** | **0.8889** | **0.7889** | 0.7000 |
| **Top-3 Accuracy** | — | **1.0000** | 0.9611 |
| **Weighted-F1** | **0.8793** | **0.7719** | 0.6592 |

*Nota Metodológica:* El hecho de que la heurística obtuviera el mayor Macro-F1 en Test confirma que en dominios cerrados con terminología técnica marcada, reglas simples son altamente competitivas. Siguiendo el protocolo, el resultado de Test no se utilizó para alterar la selección tomada en validación.

---

## 24. Resultados por Categoría en TEST

### Línea Base Lineal (Modelo Operativo):

| Categoría | Precisión | Recall | F1-Score | Casos Reales |
|---|---:|---:|---:|---:|
| `applications_services` | 0.6316 | 0.3333 | 0.4364 | 36 |
| `databases` | 0.9722 | 0.9722 | 0.9722 | 36 |
| `networks_connectivity` | 0.9000 | 0.7500 | 0.8182 | 36 |
| `infrastructure_storage` | 0.6604 | 0.9722 | 0.7865 | 36 |
| `security_access` | 0.7857 | 0.9167 | 0.8462 | 36 |

### Modelo Propuesto (Transformer Congelado):

| Categoría | Precisión | Recall | F1-Score | Casos Reales |
|---|---:|---:|---:|---:|
| `applications_services` | 0.4444 | 0.1111 | 0.1778 | 36 |
| `databases` | 0.9091 | 0.8333 | 0.8696 | 36 |
| `networks_connectivity` | 0.7429 | 0.7222 | 0.7324 | 36 |
| `infrastructure_storage` | 0.7500 | 1.0000 | 0.8571 | 36 |
| `security_access` | 0.5455 | 0.8333 | 0.6593 | 36 |

---

## 25. Matriz de Confusión en TEST

### Línea Base Lineal (Filas = Real, Columnas = Predicha):

| Real / Predicha | Apps | DB | Net | Infra | Sec | Total |
|---|---:|---:|---:|---:|---:|---:|
| `applications_services` | **12** | 0 | 2 | 14 | 8 | 36 |
| `databases` | 1 | **35** | 0 | 0 | 0 | 36 |
| `networks_connectivity` | 4 | 0 | **27** | 4 | 1 | 36 |
| `infrastructure_storage` | 0 | 1 | 0 | **35** | 0 | 36 |
| `security_access` | 2 | 0 | 1 | 0 | **33** | 36 |

### Modelo Propuesto Transformer (Filas = Real, Columnas = Predicha):

| Real / Predicha | Apps | DB | Net | Infra | Sec | Total |
|---|---:|---:|---:|---:|---:|---:|
| `applications_services` | **4** | 3 | 3 | 12 | 14 | 36 |
| `databases` | 4 | **30** | 0 | 0 | 2 | 36 |
| `networks_connectivity` | 1 | 0 | **26** | 0 | 9 | 36 |
| `infrastructure_storage` | 0 | 0 | 0 | **36** | 0 | 36 |
| `security_access` | 0 | 0 | 6 | 0 | **30** | 36 |

---

## 26. Análisis de Errores

1. **Superioridad Léxica de la Línea Base:** Tokens específicos de infraestructura (`pg_wal`, `esxi`, `bgp`, `raid5`, `vlan`, `keycloak`) poseen una correspondencia unívoca con su área técnica. La extracción de sub-palabras de `char_wb` (3 a 5 caracteres) permite capturar estos identificadores directamente. Por el contrario, el Transformer multilingüe preentrenado sin fine-tuning de dominio dispersa atención en vocabulario genérico de tickets ("falla en el servidor", "alerta de la guardia").
2. **Confusión en Aplicaciones y Servicios:** El mayor cuello de botella en Test ocurrió en `applications_services`, donde la línea base obtuvo un recall de $33.3\%$ al confundir 14 incidentes con `infrastructure_storage` y 8 con `security_access`. Esto se debe a que fallas de microservicios frecuentemente se reportan mencionando caídas de procesos en servidores físicos o denegaciones de autenticación.
3. **Mitigación mediante Top-3:** Pese a los desvíos en Top-1, la exactitud Top-3 de la línea base alcanzó el **100.0%** en Test, asegurando que la categoría especialista siempre estuvo presente entre las tres opciones asistidas al operador.

---

## 27. Arquitectura del Sistema

El software sigue un diseño modular y desacoplado:
- `data/`: Datasets CSV versionados e inmutables.
- `app/settings.py`: Taxonomía técnica UOIT y configuración central.
- `app/schemas.py`: Contrato de validación estricta Pydantic (`extra="forbid"`).
- `app/linear_baseline.py` y `app/proposed_model.py`: Definición de pipelines de ML.
- `app/inference.py`: Servicio de predicción en memoria, latencia en tiempo real y señales explicativas.
- `app/main.py`: Servidor FastAPI REST con ciclo de vida asíncrono.
- `frontend/`: Interfaz web interactiva en HTML5, CSS3 y JavaScript ES6.

---

## 28. Backend

Construido sobre FastAPI, expone:
- `POST /api/classify`: Recibe `title` e `initial_description`. Rechaza con HTTP 422 entradas fuera de rango o campos que generen data leakage. Retorna categoría sugerida, ranking completo, Top-3, latencia en ms y señales léxicas.
- `GET /api/categories`: Retorna las 5 áreas técnicas de la UOIT y especificaciones de longitud.
- `GET /api/metrics`: Expone el informe de métricas experimentales leídas de `artifacts/metrics.json`.
- `GET /api/health`: Estado operativo del modelo en memoria.
- `GET /docs`: Documentación interactiva Swagger OpenAPI.

---

## 29. Frontend

Interfaz responsiva sin dependencias pesadas:
- Formulario de triaje con validación en tiempo real.
- **Tres Escenarios Demostrativos:**
  - *Caso A (Válido):* Saturación de PgBouncer $\rightarrow$ `databases` (puntaje estimado $> 80\%$).
  - *Caso B (Difícil / Ambiguo):* Error 500 y timeout $\rightarrow$ Distribución entre `applications_services` y `databases` en Top-3.
  - *Caso C (Entrada Inválida):* Violación de longitud mínima $\rightarrow$ Interceptada formalmente con código **HTTP 422**.
- Visualización de ranking probabilístico ordenado, Top-3, latencia en milisegundos y señales de explicabilidad léxica.

---

## 30. Pruebas Automatizadas

Suite de **34 pruebas** en `pytest` aprobada al 100% en 4.23 segundos:
- Reproducibilidad del generador con semilla `SEED=42`.
- Aislamiento absoluto de familias técnicas entre Train, Validation y Test.
- Validación de contratos y rechazo de campos con fuga mediante error HTTP 422.
- Verificación matemática de Macro-F1, Accuracy y Top-3.
- Inferencia real sobre `data/test.csv` con concordancia estricta con `artifacts/metrics.json`.

---

## 31. Conclusiones

El experimento mostró que la representación TF-IDF basada en palabras y caracteres obtuvo mejor desempeño en validación que la representación semántica mediante embeddings congelados de un Transformer multilingüe, por lo que fue seleccionada como modelo operativo antes de evaluar el conjunto de prueba.

En la evaluación final, la referencia heurística basada en reglas obtuvo el mayor Macro-F1, seguida de la línea base lineal y del modelo Transformer. Este resultado demuestra que una mayor complejidad del modelo no garantiza una mejor generalización, especialmente en un dominio técnico pequeño y con vocabulario especializado.

Los resultados corresponden a un dataset sintético y no demuestran eficacia en la operación institucional real. Se requiere una validación posterior con incidentes reales debidamente anonimizados.

El sistema asiste al operador humano en el triaje inicial; no reemplaza su criterio técnico.

---

## 32. Limitaciones

1. **Dataset 100% Sintético:** Los 720 incidentes fueron generados algorítmicamente mediante combinatoria de plantillas controladas; presentan mayor separabilidad léxica que los reportes informales de usuarios en producción.
2. **Volumen Acotado:** El estudio se limita a 720 incidentes distribuidos en 40 familias y cinco categorías técnicas.
3. **Patrones Léxicos del Generador:** Es posible que existan asociaciones de palabras accidentales aprendidas por los modelos a partir de las plantillas base.
4. **Caída de Desempeño entre Validación y Test:** La línea base descendió de Macro-F1 0.9423 en validación a 0.7719 en test, evidenciando la dificultad de generalizar ante familias técnicas completamente no vistas.
5. **Bajo Recall en Aplicaciones:** La categoría `applications_services` registró un recall de 33.3%, confundiéndose con infraestructura (14 casos) y seguridad (8 casos).
6. **Transformer con Embeddings Congelados:** No se realizó ajuste fino (*fine-tuning*) end-to-end de las capas de atención del Transformer por restricciones de cómputo en CPU.
7. **Puntajes no Calibrados:** Los valores calculados representan estimaciones relativas del clasificador y no probabilidades calibradas de acierto absoluto; ante consultas fuera de dominio, el modelo asignará puntuación sobre las categorías conocidas.
8. **Necesidad de Supervisión Humana:** El sistema opera estrictamente como herramienta de asistencia y apoyo al triaje; no sustituye la evaluación del operador técnico de guardia.

---

## 33. Trabajo Futuro

1. **Piloto con Datos Reales:** Ejecutar una fase piloto anonimizada con tickets reales de la UOIT para evaluar el impacto en el MTTR.
2. **Ajuste Fino Supervisado del Transformer:** Entrenar adaptativamente los pesos del modelo de lenguaje sobre texto técnico de operaciones de TI mediante aceleración por hardware.
3. **Clasificación Multi-etiqueta:** Extender el modelo para asignar múltiples áreas resolutoras simultáneas en incidentes compuestos.
4. **Calibración de Probabilidades:** Aplicar escalado de Platt o regresión isotónica sobre los puntajes para calibrar probabilidades de certeza.

---

## 34. Referencias

1. Pedregosa, F., Varoquaux, G., Gramfort, A., Michel, V., Thirion, B., Grisel, O., Blondel, M., Prettenhofer, P., Weiss, R., Dubourg, V., Vanderplas, J., Passos, A., Cournapeau, D., Brucher, M., Perrot, M., & Duchesnay, É. (2011). Scikit-learn: Machine Learning in Python. *Journal of Machine Learning Research*, 12, 2825–2830.
2. Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks. In *Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing and the 9th International Joint Conference on Natural Language Processing (EMNLP-IJCNLP)*, pages 3982–3992.
3. Devlin, J., Chang, M. W., Lee, K., & Toutanova, K. (2019). BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding. In *Proceedings of the 2019 Conference of the North American Chapter of the Association for Computational Linguistics (NAACL-HLT)*, pages 4171–4186.
4. AXELOS. (2020). *ITIL® 4: Incident Management Practice Guide*. The Stationery Office, London.
5. Ramírez-Gallego, S., Krawczyk, B., García, S., Woźniak, M., & Herrera, F. (2017). A survey on data preprocessing for data stream mining: Current status and future directions. *Neurocomputing*, 239, 39–57.
