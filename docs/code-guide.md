# Leer el código desde cero

## Vocabulario inicial

- **Variable:** un nombre que guarda un valor, como `message`.
- **Función:** instrucciones agrupadas para realizar una tarea.
- **Etiqueta:** categoría correcta de un ejemplo de entrenamiento.
- **Vectorizador:** transforma texto en números que puede utilizar el modelo.
- **Pipeline:** une transformaciones y modelo para repetir el mismo proceso al entrenar y predecir.
- **API:** permite que la pantalla solicite una clasificación al servidor.

En Python los comentarios comienzan con `#` y la sangría organiza los bloques. Conserva los espacios al modificar el código.

## Recorrido del ejemplo

```text
Familias de frases → mensajes sintéticos → separación por familia
    → aprender vocabulario y modelo con entrenamiento
    → elegir C y umbral con validación
    → evaluar la prueba y guardar resultados

Texto del formulario → validar → transformar con vocabulario guardado
    → ranking de categorías → criterio de revisión → respuesta en pantalla
```

## Configuración, frases y datos

`settings.py` contiene las categorías, rutas y criterios. `templates.py` contiene las frases originales del simulador. `data.py` genera variantes y separa familias completas en entrenamiento, validación y prueba.

`text.py` normaliza palabras para la regla y la detección de duplicados. `schemas.py` define la entrada válida: un mensaje, sin categoría ni resolución.

## La línea base

`baseline.py` contiene palabras agrupadas por categoría. `rule_prediction()` devuelve la categoría, coincidencias y si fue necesario utilizar el respaldo. Esto permite explicar qué hizo la regla cuando no encontró vocabulario.

## Entrenar

En `train.py`, `build_model()` crea TF-IDF y regresión logística. La instrucción principal es:

```python
model.fit(train.message, train.category)
```

El primer argumento contiene mensajes; el segundo, categorías correctas. Al ejecutar `fit`, se aprende tanto el vocabulario como los coeficientes del clasificador.

Para clasificar mensajes nuevos:

```python
predictions = model.predict(test.message)
```

Para obtener puntajes para las cinco categorías:

```python
probabilities = model.predict_proba(test.message)
```

El orden de columnas se consulta en `classifier.classes_`. No se debe asumir que coincide con un orden escrito a mano en la pantalla.

`evaluation.py` calcula métricas y elige el criterio de revisión. El test se consulta después de fijar el modelo y el umbral. `train.py` guarda datos particionados, modelo, informe y predicciones individuales.

## Predecir y explicar

`inference.py` recibe el pipeline ya entrenado. Ordena las categorías por puntaje, aplica el umbral y calcula contribuciones de términos presentes. No vuelve a aprender vocabulario con el texto nuevo.

`main.py` carga el artefacto al iniciar y expone `/api/classify`. FastAPI usa `TicketInput` para rechazar entradas incompletas o incorrectas. Solo se carga el archivo local del proyecto; no se deben abrir modelos `joblib` de origen desconocido, porque su deserialización puede ejecutar código.

## La interfaz

- `index.html` define formulario, ranking, tablas y secciones.
- `styles.css` define colores y distribución según el tamaño de pantalla.
- `app.js` recoge el texto y utiliza `fetch()` para consultar la API.

Las barras muestran puntajes devueltos por el modelo. Las métricas se leen del informe, no se inventan en JavaScript. Los textos se insertan con `textContent`, sin ejecutar HTML que alguien escriba en el formulario.

Si el mensaje cambia mientras llega una respuesta, esa respuesta antigua se descarta. Cambiar el texto también oculta el resultado previo.

## Qué modificar primero

1. Probar paráfrasis del mismo problema y observar estabilidad.
2. Comparar reglas y modelo en un error de la prueba, sin modificar todavía el entrenamiento.
3. Añadir familias nuevas con etiqueta revisada y reservar parte de ellas para una prueba nueva.
4. Solo después comparar otra representación o modelo.

Agregar variantes de un mismo saludo aumenta filas, pero no necesariamente aumenta la diversidad que el modelo necesita.
