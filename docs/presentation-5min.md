# Guía de Presentación y Defensa Técnica (5 Minutos)

**Proyecto:** Clasificación Automática de Incidentes Tecnológicos UOIT  
**Postulante:** Juan Serrudo  
**Programa:** Maestría en Ingeniería de Software Avanzada  
**Tiempo Límite:** Exactamente 5:00 minutos  

---

## Estructura Temporal de la Defensa

| Intervalo | Bloque Temático | Diapositiva / Enfoque |
|---|---|---|
| **0:00 – 2:00** | Problema, Datos, Modelos y Resultados | Diapositivas 1, 2 y 3 |
| **2:00 – 4:00** | Demostración en Vivo del Sistema | Diapositiva 4 / Interfaz Web |
| **4:00 – 5:00** | Conclusiones, Limitaciones y Repositorio | Diapositiva 5 |

---

## Diapositivas (5 Diapositivas Máximo)

---

### Diapositiva 1: Problema y Solución Propuesta

- **Contexto Operativo:**
  - La Unidad de Operaciones e Infraestructura Tecnológica (UOIT) recibe decenas de incidentes diarios de monitoreo y usuarios técnicos.
  - El triaje manual genera cuellos de botella, fatiga cognitiva en guardias y retrasos en la asignación al especialista resolutor.
- **La Pregunta Científica:**
  - *¿Podemos sugerir de forma instantánea la categoría técnica resolutora a partir exclusivamente del título y descripción inicial, antes del diagnóstico y cierre?*
- **Solución Implementada:**
  - Sistema de clasificación supervisada en 5 categorías técnicas.
  - Prototipo de inferencia local con ranking de probabilidades, Top-3, latencia en tiempo real y detección de casos fuera de dominio.

---

### Diapositiva 2: Dataset y Estrategia de Validación

- **Dataset Sintético Controlado (Confidencialidad Institucional):**
  - **720 incidentes** estructurados en **40 familias técnicas** (`event_group_id`).
  - Perfectamente balanceado: 5 categorías $\times$ 8 familias $\times$ 18 variantes = 144 incidentes por clase.
- **Prevención Estricta de Fuga de Información (*Data Leakage*):**
  - **Particionado disjunto por familias:** Ninguna familia técnica de entrenamiento se repite en validación ni en prueba.
  - **Train:** 450 incidentes (25 familias) | **Val:** 90 incidentes (5 familias) | **Test:** 180 incidentes (10 familias).
  - Bloqueo en tiempo de inferencia de campos de cierre (`category`, `resolution`, `assignee`, etc.).
- **Métrica Primaria:**
  - **Macro-F1:** Trata con idéntico rigor a las 5 áreas técnicas de la infraestructura.

---

### Diapositiva 3: Línea Base vs. Transformer y Resultados Finales

- **Modelos Comparados (Congelamiento Metodológico):**
  - **Línea Base Lineal:** TF-IDF dual (palabras 1-2 + caracteres sub-palabra `char_wb` 3-5) + Regresión Logística ($C=1.0$).
  - **Propuesta Avanzada:** `paraphrase-multilingual-MiniLM-L12-v2` (embeddings congelados 384d) + Regresión Logística ($C=1.0$).
- **Selección Operativa en VALIDACIÓN (Criterio Científico):**
  - Línea Base: **Macro-F1 = 0.9423** | Transformer: **Macro-F1 = 0.7822**.
  - *Decisión:* La línea base fue seleccionada para producción por su superioridad en validación.
- **Evaluación Final en TEST Congelado (180 casos no vistos):**
  - **Línea Base Lineal:** Macro-F1 = **0.7719** | Accuracy = **78.9%** | Top-3 Accuracy = **100.0%**.
  - **Transformer:** Macro-F1 = **0.6592** | Accuracy = **70.0%** | Top-3 Accuracy = **96.1%**.
- **Hallazgo Clave:** Los n-gramas de caracteres capturan con precisión quirúrgica identificadores técnicos (`pg_wal`, `esxi`, `bgp`, `raid5`), superando al Transformer semántico genérico sin fine-tuning.

---

### Diapositiva 4: Arquitectura del Sistema y Demostración

- **Arquitectura de Micro-demostración:**
  - Backend REST ligero en **FastAPI** con validación estricta Pydantic y serialización joblib.
  - Frontend interactivo Vanilla (HTML5/CSS3/JS) con latencia < 2 ms por inferencia en CPU.
- **Tres Escenarios Demostrativos:**
  1. *Caso Claro:* Falla en PgBouncer $\rightarrow$ `databases` (Confianza > 85%).
  2. *Caso Ambiguo:* Error 500 y timeout $\rightarrow$ Distribución dividida entre `applications_services` y `databases`.
  3. *Caso Fuera de Dominio:* Solicitud de cafetería $\rightarrow$ Detección de vocabulario desconocido y recomendación de revisión técnica.

---

### Diapositiva 5: Conclusiones, Limitaciones y Repositorio

- **Conclusiones:**
  - El rigor metodológico demostró que un modelo lineal especializado puede superar a modelos neuronales pesados en dominios técnicos específicos.
  - La exactitud Top-3 del 100% en test valida la utilidad del sistema como asistente de triaje al operador humano.
- **Limitaciones Transparentes:**
  - Dataset sintético: Presenta mayor separabilidad léxica que incidentes reales con texto informal.
  - Modelo mono-etiqueta: No captura incidentes de cascada multi-sistema.
  - No se afirma eficacia institucional real sin una fase piloto previa.
- **Entregables:** Repositorio reproducible, 34 pruebas automáticas aprobadas, documentación completa en español e informe técnico fuente.

---

## Guion Oral Minuto a Minuto (Exactamente 5 Minutos)

### Bloque 1: Problema, Datos, Modelos y Resultados (0:00 – 2:00)

**[0:00 – 0:30] Saludo y Planteamiento del Problema**  
> *"Buenos días, miembros del tribunal. Presento el proyecto final de Machine Learning: 'Clasificación Automática de Incidentes Tecnológicos para la Unidad de Operaciones e Infraestructura Tecnológica (UOIT)'.  
> En los centros de operaciones, el triaje manual de tickets genera cuellos de botella y demoras en la respuesta ante caídas críticas. Nuestro objetivo es responder a la pregunta: ¿Podemos sugerir de manera instantánea la categoría técnica resolutora de un incidente utilizando únicamente el título y la descripción inicial con la que se reporta?  
> Formulamos un problema de clasificación supervisada en 5 categorías: Aplicaciones, Bases de Datos, Redes, Infraestructura y Seguridad."*

**[0:30 – 1:15] Dataset, Prevención de Fuga y Metodología**  
> *"Por estricta reserva institucional, no utilizamos incidentes de producción. Generamos un dataset sintético determinista de 720 incidentes distribuidos uniformemente en 40 familias técnicas disjuntas.  
> Para evitar fuga de información (*data leakage*), el particionado se realizó agrupando por grupos de evento (`event_group_id`): 450 casos en entrenamiento, 90 en validación y 180 en prueba final. Ninguna familia ni texto similar de entrenamiento aparece en validación ni en test.  
> Además, el esquema de entrada rechaza formalmente cualquier dato posterior al registro, como diagnósticos o resoluciones."*

**[1:15 – 2:00] Comparativa de Modelos y Resultados**  
> *"Comparamos una línea base lineal con TF-IDF dual de palabras y n-gramas de caracteres contra un modelo propuesto basado en el Transformer multilingual MiniLM con embeddings congelados de 384 dimensiones.  
> Aplicamos un estricto congelamiento metodológico: en validación, la línea base lineal obtuvo un Macro-F1 de 0.9423 frente a 0.7822 del Transformer. Siguiendo el protocolo, seleccionamos la línea base para el sistema operativo.  
> Al evaluar el conjunto de test congelado una sola vez, la línea base confirmó su solidez alcanzando un Macro-F1 de 0.7719 y un Accuracy del 78.9%, frente al 0.6592 del Transformer. La razón técnica es clara: los n-gramas de caracteres capturan términos de infraestructura como `pg_wal`, `esxi` o `bgp` con mayor especificidad que un Transformer genérico no adaptado al dominio. Además, la línea base logró un 100% de exactitud en el Top-3."*

---

### Bloque 2: Demostración en Vivo del Sistema (2:00 – 4:00)

**[2:00 – 2:40] Escenario A: Caso Claro de Bases de Datos**  
> *"Paso ahora a la demostración en vivo de nuestra aplicación web conectada a la API FastAPI.  
> Cargamos el **Escenario A: Caso Claro**.  
> El operador recibe la alerta: 'Agotamiento del pool de conexiones en base de datos PostgreSQL'.  
> Al pulsar 'Clasificar incidente', observamos una respuesta en menos de 2 milisegundos. El sistema sugiere con más del 85% de probabilidad la categoría `Bases de datos`. El indicador muestra 'Sugerencia de alta confianza' y el desglose de términos resalta tokens influyentes como 'postgresql' y 'conexiones'. El triaje es inequívoco."*

**[2:40 – 3:20] Escenario B: Caso Ambiguo**  
> *"Carguemos el **Escenario B: Caso Ambiguo**.  
> El título indica: 'Error 500 al consultar reportes contables y timeout intermitente'.  
> En este caso, el incidente involucra tanto la capa web como tiempos de espera que pueden originarse en la base de datos.  
> Al clasificar, observamos que el modelo distribuye probabilidades entre `Aplicaciones y servicios` y `Bases de datos`. Aquí se evidencia el valor práctico del **Top-3**: el operador humano no recibe una imposición a ciegas, sino un abanico probabilístico fundamentado que reduce drásticamente el tiempo de revisión técnica."*

**[3:20 – 4:00] Escenario C: Entrada Fuera de Dominio y Validación**  
> *"Finalmente, probemos el **Escenario C: Fuera de Dominio**.  
> Un usuario envía: 'Menú de almuerzo y opciones vegetarianas en la cafetería'.  
> El sistema analiza la entrada y, gracias a la inspección léxica implementada, detecta vocabulario desconocido respecto a las alertas técnicas de la UOIT. El sistema emite inmediatamente la alerta: 'Revisión técnica recomendada', protegiendo la operación frente a solicitudes fuera de alcance.  
> Asimismo, si un cliente intentara enviar campos no autorizados como 'resolution', el contrato Pydantic del backend rechaza la petición con error 422, impidiendo cualquier fuga de datos."*

---

### Bloque 3: Conclusiones, Limitaciones y Repositorio (4:00 – 5:00)

**[4:00 – 4:40] Conclusiones y Lecciones Aprendidas**  
> *"Para concluir:  
> Primero, el proyecto demuestra que un clasificador lineal bien fundamentado, con extracción exhaustiva de n-gramas de caracteres, es superior en precisión, explicabilidad y latencia (menos de 2 ms en CPU) a un modelo de Deep Learning genérico congelado en este dominio técnico.  
> Segundo, la obtención de un 100% de Top-3 Accuracy en test ratifica su utilidad práctica como herramienta de soporte a la decisión humana.  
> Tercero, el congelamiento metodológico y la prevención de fuga garantizaron una evaluación honesta y reproducible, sin optimismo artificial."*

**[4:40 – 5:00] Limitaciones y Cierre**  
> *"Como limitación explícita, señalamos que un dataset sintético posee mayor separabilidad léxica que incidentes reales; por ello, no afirmamos eficacia en producción sin antes realizar un piloto controlado.  
> El proyecto cuenta con 34 pruebas automáticas al 100% de aprobación, documentación completa y código disponible en el repositorio. Quedo a disposición de sus preguntas. Muchas gracias."*
