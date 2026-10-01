# Soporte en orden

Ejemplo educativo completo de **clasificación de solicitudes de soporte en español**. Incluye datos sintéticos, entrenamiento, comparación con reglas, evaluación, backend y una interfaz para escribir mensajes.

El código, los nombres de funciones y los comentarios están en inglés. La interfaz y la documentación están en español. No contiene nombres de personas ni solicitudes reales.

## La pregunta del proyecto

**Al recibir una solicitud inicial, ¿qué categoría de soporte conviene sugerir para que una persona la revise?**

El ejemplo distingue cinco categorías: accesos y permisos, red y conectividad, equipos y periféricos, aplicaciones y correo electrónico. Cada mensaje tiene una categoría principal.

La aplicación propone alternativas. No crea tickets, no asigna equipos, no determina prioridades y no envía mensajes.

## Qué incluye

- 1.104 mensajes ficticios en español, agrupados en 60 familias de frases.
- Separación de entrenamiento, validación y prueba por familia: las paráfrasis y variantes permanecen juntas.
- Línea base por palabras clave con un respaldo explícito para mensajes sin coincidencias.
- Modelo `TF-IDF + LogisticRegression`, con dos configuraciones comparadas por Macro-F1 de validación.
- Macro-F1, F1 ponderado, exactitud, métricas por categoría y matriz de confusión.
- Criterio de revisión elegido en validación; cobertura y exactitud del subconjunto informadas por separado.
- Interfaz con seis ejemplos, ranking de categorías, comparación con reglas y términos que contribuyeron al puntaje.
- FastAPI, HTML/CSS/JavaScript, documentación Markdown y 28 pruebas automáticas.

## Resultado que conviene discutir en clase

**En este experimento las reglas superan al modelo:** Macro-F1 de 0,878 frente a 0,701 sobre la prueba sintética. Se conserva ese resultado, sin cambiar el experimento para hacerlo parecer mejor.

El ejemplo enseña a construir y evaluar un modelo, pero sus resultados **no justifican reemplazar la regla sencilla**. La documentación explica cómo investigar errores y qué información adicional necesitaríamos para otra comparación.

## Empezar desde cero

### 1. Preparar Python y la carpeta

Se utilizó **Python 3.12**. Puedes instalarlo desde [python.org](https://www.python.org/downloads/). Descomprime el ZIP y abre una terminal dentro de `support-triage-demo`, la carpeta que contiene este archivo y `run.py`.

Una terminal permite ejecutar instrucciones escritas. Copia una línea a la vez y espera a que termine.

### 2. Instalar las dependencias

En macOS o Linux, desde la carpeta que contiene el proyecto:

```bash
cd support-triage-demo
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-lock.txt
```

En Windows PowerShell:

```powershell
cd support-triage-demo
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
```

Si ya abriste la terminal dentro de `support-triage-demo`, omite la primera línea. `.venv` mantiene las librerías separadas de otros proyectos. `requirements-lock.txt` fija las versiones probadas; `requirements.txt` enumera dependencias directas y rangos permitidos.

Solo la instalación necesita Internet. Después, el ejemplo funciona localmente sin claves de API, servicios de lenguaje externos ni descarga de modelos grandes.

### 3. Iniciar

macOS o Linux, con el entorno activado:

```bash
python run.py
```

Windows:

```powershell
.\.venv\Scripts\python.exe run.py
```

Abre **http://127.0.0.1:8991**. Mantén la terminal abierta. Para detener el servidor, pulsa `Ctrl+C`.

El puerto es distinto de los ejemplos anteriores. El paquete incluye el modelo entrenado y los CSV; si faltan, el comando los genera antes de iniciar.

### 4. Probar la interfaz

1. Carga **Acceso bloqueado** y pulsa **Analizar solicitud**.
2. Compara la sugerencia del modelo con la regla por palabras clave.
3. Despliega **Términos que influyeron en la sugerencia**.
4. Prueba **Sin conexión**, **Correo pendiente** y **Teclado**.
5. Prueba **Mensaje ambiguo** y **Otro tema**. Evalúa si el aviso de revisión resulta suficiente; el modelo no tiene una clase «otro».
6. Abre **Resultados** para revisar errores y **Datos y método** para comprender el experimento.

Los puntajes son relativos a las cinco clases conocidas; no son probabilidades calibradas de estar en lo correcto. Cambiar el texto oculta la respuesta anterior hasta volver a analizar.

## Repetir el experimento

Detén el servidor y ejecuta:

```bash
python -m app.data
python -m app.train
python -m pytest -q
python run.py
```

En Windows reemplaza `python` por `.\.venv\Scripts\python.exe`.

Para regenerar, entrenar e iniciar en un paso:

```bash
python run.py --rebuild
```

Regenerar reemplaza los datos y artefactos del ejemplo. Copia antes la carpeta si deseas conservar modificaciones. Para entrenar sobre un CSV editado, utiliza solo `python -m app.train`: el origen es `data/tickets.csv`, y las particiones se reconstruyen a partir de las familias.

## Organización

```text
support-triage-demo/
├── README.md
├── run.py                      # Inicia la aplicación local
├── requirements.txt
├── requirements-lock.txt
├── app/
│   ├── settings.py             # Categorías, rutas y criterios
│   ├── templates.py            # Familias de frases ficticias
│   ├── text.py                 # Normalización de texto
│   ├── schemas.py              # Validación del mensaje
│   ├── data.py                 # Generación y separación por familia
│   ├── baseline.py             # Reglas por palabras clave
│   ├── evaluation.py           # Métricas y criterio de revisión
│   ├── train.py                # Entrenamiento y exportación
│   ├── inference.py            # Predicción y términos destacados
│   └── main.py                 # API y archivos del frontend
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── data/
│   ├── tickets.csv             # Conjunto sintético completo
│   ├── train.csv
│   ├── validation.csv
│   └── test.csv
├── artifacts/
│   ├── model.joblib            # Pipeline y umbral guardados
│   ├── metrics.json            # Cifras que consulta la interfaz
│   ├── evaluation.md           # Informe del experimento
│   ├── test_predictions.csv    # Aciertos y errores por mensaje
│   └── example_predictions.json
├── tests/
└── docs/
```

## Guías

- [Contexto y diccionario de datos](docs/data.md).
- [Modelo, validación y métricas](docs/methodology.md).
- [Leer el código desde cero](docs/code-guide.md).
- [API y ejemplos de uso](docs/api.md).
- [Guion de clase y ejercicios](docs/teaching-guide.md).
- [Resultados calculados](artifacts/evaluation.md).
- [Comprobaciones realizadas](docs/verification.md).

## Problemas habituales

| Situación | Qué hacer |
|---|---|
| No encuentra Python | Instala Python 3.12; en macOS prueba `python3`, en Windows `py -3.12`. |
| Falta una librería | Usa el Python de `.venv` e instala `requirements-lock.txt`. |
| Puerto ocupado | Ejecuta `python run.py --port 8992` y abre ese puerto. |
| El navegador no conecta | Comprueba que el servidor esté encendido y la dirección coincida. |
| Modelo no disponible | Genera datos, entrena y reinicia el servidor. |
| HTTP 422 | Revisa la longitud y el contenido del mensaje; no envíes campos adicionales. |
| Modifiqué los datos | Ejecuta entrenamiento y reinicia; el servidor carga el modelo una vez al arrancar. |
| Categoría equivocada | Revisa las alternativas y documenta el error. No toda clasificación incorrecta es un fallo de programación. |

## Alcance

El servidor escucha solo en `127.0.0.1`. No incluye autenticación, base de datos ni integraciones operativas. Las consultas no se guardan. Los textos de ejemplo son inventados; no se debe interpretar su desempeño como eficacia real ni como capacidad general de comprensión del lenguaje.

Referencia técnica: [clasificación de documentos con características de texto en scikit-learn](https://scikit-learn.org/stable/auto_examples/text/plot_document_classification_20newsgroups.html).

