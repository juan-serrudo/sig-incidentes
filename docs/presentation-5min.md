# Guía de Presentación y Defensa Técnica (5 Minutos)

**Proyecto:** Clasificación Inteligente de Incidentes Tecnológicos UOIT  
**Postulante:** Juan Serrudo  
**Programa:** Maestría en Ingeniería de Software Avanzada  
**Tiempo Límite:** Exactamente 5:00 minutos  
**Formato:** 16:9 · Estilo Tecnología Académica Moderna / Minimal Tech  

---

## Estructura Temporal de la Defensa

| Intervalo | Diapositiva | Bloque Temático |
|---|---|---|
| **0:00 – 0:45** | Diapositiva 1 | Problema y Solución |
| **0:45 – 1:30** | Diapositiva 2 | Dataset y Validación (Prevención de Fuga) |
| **1:30 – 2:00** | Diapositiva 3 | Comparación Experimental y Selección |
| **2:00 – 2:40** | Diapositiva 4 | Demo en Vivo: Caso A (Válido) |
| **2:40 – 3:20** | Diapositiva 4 | Demo en Vivo: Caso B (Difícil / Ambiguo) |
| **3:20 – 3:45** | Diapositiva 4 | Demo en Vivo: Caso C (Entrada Inválida HTTP 422) |
| **3:45 – 4:30** | Diapositiva 5 | Conclusiones y Limitaciones |
| **4:30 – 5:00** | Diapositiva 5 | Repositorio y Cierre |

---

## Contenido de las Cinco Diapositivas (16:9)

---

### Diapositiva 1: Problema y Solución

**Título:** Clasificación inteligente de incidentes tecnológicos  
**Subtítulo:** Sistema asistido de triaje operativo para la UOIT mediante NLP supervisado  

- **Problema:**  
  La clasificación inicial de incidentes tecnológicos requiere interpretar rápidamente el título y la descripción disponibles al momento de su registro, antes de disponer de diagnóstico o resolución.
- **Solución:**  
  Sistema funcional que recibe el incidente y propone una categoría técnica resolutora para apoyar la toma de decisiones del operador de guardia.
- **Flujo de Inferencia:**  
  `Título + Descripción` $\rightarrow$ `Clasificador ML` $\rightarrow$ `Categoría Sugerida (Top-3)` $\rightarrow$ `Revisión Humana`
- **Cinco Categorías de Infraestructura:**  
  1. *Aplicaciones y servicios*  
  2. *Bases de datos*  
  3. *Redes y conectividad*  
  4. *Infraestructura y almacenamiento*  
  5. *Seguridad y accesos*  

---

### Diapositiva 2: Dataset y Validación

**Título:** Dataset y Estrategia de Validación  
**Subtítulo:** Prevención estricta de fuga de información (*Data Leakage*)  

- **Estructura del Dataset Sintético (Confidencialidad Operativa UOIT):**  
  - **720 incidentes sintéticos** organizados en **40 familias técnicas** (`event_group_id`).
  - **5 categorías** balanceadas ($20\%$ c/u, 144 casos por categoría, 18 variantes por familia).
- **Partición Disjunta por Familias:**  
  - **Train:** 450 incidentes / 25 familias ($62.5\%$).
  - **Validation:** 90 incidentes / 5 familias ($12.5\%$).
  - **Test:** 180 incidentes / 10 familias ($25.0\%$).
- **Regla Metodológica Clave:**  
  *“Las familias permanecen completas en una única partición para evitar fuga de información por memorización de plantillas.”*
- **Aislamiento en Entrada:**  
  - *Entrada permitida:* Exclusivamente `title` e `initial_description`.
  - *Campos prohibidos:* Solución, responsable final, causa raíz o texto de cierre (bloqueados formalmente).

---

### Diapositiva 3: Comparación Experimental

**Título:** Comparación Experimental de Enfoques  
**Subtítulo:** Evaluación en Validación vs. Evaluación Final en Test Congelado  

- **Tres Enfoques Evaluados:**  
  1. *Referencia Heurística:* Reglas deterministas de palabras clave técnicas UOIT.
  2. *Línea Base:* Dual TF-IDF (palabras 1-2 + caracteres sub-palabra 3-5) + Regresión Logística ($C=1.0$).
  3. *Modelo Propuesto:* MiniLM multilingüe preentrenado (embeddings densos 384d congelados) + Regresión Logística ($C=1.0$).
- **Resultados en TEST Final Congelado (180 casos no vistos):**  
  - **Referencia Heurística:** Macro-F1 = **0.8793** | Accuracy = **88.89%**
  - **Línea Base Lineal:** Macro-F1 = **0.7719** | Accuracy = **78.89%** | Top-3 Accuracy = **100.0%**
  - **Modelo Propuesto (Transformer):** Macro-F1 = **0.6592** | Accuracy = **70.00%** | Top-3 Accuracy = **96.11%**
- **Recuadro de Decisión Metodológica:**  
  *“Modelo operativo seleccionado previamente en VALIDATION: Línea base — Macro-F1 0.9423 frente a 0.7822 del Transformer.”*
- **Mensaje Principal:**  
  *“Mayor complejidad no implicó mejor generalización. Los n-gramas de caracteres capturan identificadores técnicos específicos (`pg_wal`, `esxi`, `bgp`) con mayor nitidez que embeddings generales congelados.”*

---

### Diapositiva 4: Sistema Funcional y Demostración

**Título:** Arquitectura del Sistema y Demostración  
**Subtítulo:** Servicio REST FastAPI desacoplado e interfaz interactiva  

- **Arquitectura de Software:**  
  `Frontend Web` $\rightarrow$ `FastAPI REST` $\rightarrow$ `Validación Pydantic` $\rightarrow$ `Pipeline Scikit-Learn` $\rightarrow$ `Ranking + Latencia`
- **Componentes Técnicos:**  
  - API real con esquema estricto (`extra="forbid"`), OpenAPI Swagger en `/docs`.
  - Inferencia ultra-rápida en CPU (< 20 ms), explicabilidad léxica y Top-3 probabilístico.
- **Tres Casos Demostrativos:**  
  - **A. Caso Válido:** Saturación de PgBouncer $\rightarrow$ Sugiere `Bases de datos` (puntaje estimado $> 80\%$).
  - **B. Caso Ambiguo:** Error 500 y timeout $\rightarrow$ Distribución entre `Aplicaciones` y `Bases de datos` en Top-3.
  - **C. Entrada Inválida:** Violación de contrato de longitud $\rightarrow$ Interceptada con código **HTTP 422**.

---

### Diapositiva 5: Conclusiones y Limitaciones

**Título:** Conclusiones, Limitaciones y Repositorio  
**Subtítulo:** Síntesis académica del proyecto SIG-UOIT  

- **Conclusiones:**  
  - Se implementó y validó el flujo completo de Machine Learning con estricto congelamiento metodológico.
  - La línea base lineal superó al Transformer en Validation y se conservó para la operación.
  - La heurística basada en reglas obtuvo el mejor Macro-F1 en Test, confirmando que una solución sencilla puede ser muy competitiva en dominios técnicos específicos.
  - La exactitud Top-3 del 100% respalda la viabilidad del clasificador para asistencia humana.
- **Limitaciones Transparentes:**  
  - Dataset 100% sintético de 720 incidentes en 40 familias.
  - Clasificación mono-etiqueta en 5 categorías.
  - Los puntajes devueltos no son probabilidades calibradas de certeza absoluta.
  - Necesidad indispensable de validación futura con incidentes reales anonimizados en un entorno piloto.
- **Cierre Institucional:**  
  *“El sistema asiste al operador; no reemplaza su criterio técnico.”*
- **Repositorio Oficial:**  
  `https://github.com/juan-serrudo/sig-incidentes`

---

## Guion Oral Minuto a Minuto (Exactamente 5:00 Minutos)

### [0:00 – 0:45] Problema y Solución
> *"Buenos días, miembros del tribunal. Presento el proyecto: 'Clasificación Inteligente de Incidentes Tecnológicos para la Unidad de Operaciones e Infraestructura Tecnológica (UOIT)'.  
> En los centros de monitoreo y soporte, el triaje manual de tickets genera demoras en la respuesta ante caídas de servicios. Nuestro problema central fue: ¿podemos orientar al operador proponiendo la categoría técnica resolutora adecuada utilizando únicamente el texto disponible al momento de abrir el requerimiento?  
> Diseñamos un prototipo funcional supervisado que clasifica incidentes en cinco áreas: Aplicaciones, Bases de Datos, Redes, Infraestructura y Seguridad, ofreciendo un ranking de opciones y Top-3 para asistir la decisión humana."*

### [0:45 – 1:30] Dataset y Validación
> *"Por motivos estrictos de reserva operativa de la infraestructura, no se utilizaron tickets de producción. Construimos un dataset sintético determinista de 720 incidentes agrupados en 40 familias técnicas disjuntas.  
> Para evitar fuga de información (*data leakage*), el particionado se realizó agrupando por familias técnicas completas: 450 casos en entrenamiento, 90 en validación y 180 en prueba final. Ninguna familia ni variante presente en entrenamiento se repite en validación ni en prueba.  
> Además, el esquema de entrada solo admite título y descripción preliminar; cualquier dato posterior, como técnicos asignados o soluciones, queda terminantemente bloqueado."*

### [1:30 – 2:00] Comparación y Resultado Principal
> *"Comparamos tres enfoques: una referencia heurística de palabras clave, una línea base lineal con TF-IDF dual de palabras y sub-palabras, y un Transformer multilingüe MiniLM con embeddings congelados.  
> Aplicamos un protocolo de congelamiento riguroso: en validación, la línea base superó al Transformer con un Macro-F1 de 0.9423 frente a 0.7822, por lo que fue elegida como modelo operativo.  
> Al evaluar el conjunto de test congelado, la heurística obtuvo 0.8793, la línea base 0.7719 y el Transformer 0.6592. El hallazgo clave es que una mayor complejidad no garantizó mejor generalización: los n-gramas de caracteres capturaron términos especializados como `pg_wal` o `bgp` con mayor especificidad que el modelo neuronal congelado. Asimismo, la línea base obtuvo un 100% de exactitud en el Top-3."*

### [2:00 – 2:40] Demo en Vivo: Caso Válido
> *"Pasemos a la demostración en vivo de nuestra aplicación web conectada a FastAPI.  
> Cargamos el **Caso A: Válido**.  
> El operador recibe la alerta: 'Agotamiento del pool de conexiones en base de datos PostgreSQL'.  
> Al pulsar 'Clasificar incidente', la respuesta se genera en milisegundos. El clasificador asigna el mayor puntaje estimado a `Bases de datos`. El desglose de explicabilidad resalta tokens influyentes como 'postgresql' y 'conexiones', permitiendo una asignación ágil e informada."*

### [2:40 – 3:20] Demo en Vivo: Caso Ambiguo
> *"Carguemos el **Caso B: Difícil o Ambiguo**.  
> El reporte indica: 'Error 500 al consultar reportes contables y timeout intermitente'.  
> Aquí los síntomas involucran tanto la capa web como tiempos de espera que pueden originarse en la base de datos.  
> Al clasificar, observamos que el modelo reparte los puntajes estimados entre `Aplicaciones y servicios` y `Bases de datos`. Aquí se evidencia el valor práctico del **Top-3**: el operador recibe las alternativas ordenadas, facilitando la colaboración interdisciplinaria sin sesgar la asignación."*

### [3:20 – 3:45] Demo en Vivo: Entrada Inválida (HTTP 422)
> *"Probemos ahora el **Caso C: Entrada Inválida**.  
> Si se intenta enviar una descripción telegráfica como 'Caída' o 'Error' que no cumple las longitudes mínimas, el backend FastAPI rechaza la petición respondiendo con código **HTTP 422**. La interfaz notifica con precisión la regla de validación infringida, demostrando la solidez del contrato y la prevención de fallos en el pipeline."*

### [3:45 – 4:30] Conclusiones y Limitaciones
> *"En conclusión:  
> Primero, se implementó exitosamente el pipeline completo de Machine Learning con selección formal en validación.  
> Segundo, confirmamos empíricamente que en dominios técnicos específicos, un modelo lineal con extracción sub-léxica supera a un Transformer general congelado y ofrece latencias inferiores a 20 milisegundos.  
> Como limitaciones transparentes, señalamos que se trata de un dataset sintético de 720 casos y que los puntajes representan estimaciones relativas, no probabilidades absolutas de acierto; por ende, se requiere una validación futura con incidentes reales anonimizados."*

### [4:30 – 5:00] Repositorio y Cierre
> *"Enfatizamos el principio rector del proyecto: el clasificador asiste al operador humano en el triaje inicial, pero no reemplaza su criterio técnico.  
> Todo el código, las 34 pruebas automatizadas aprobadas y los artefactos congelados están disponibles en el repositorio Git oficial. Quedo a su entera disposición para sus preguntas. Muchas gracias."*
