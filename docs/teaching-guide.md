# Guion de clase y ejercicios

## Objetivo

Comprender cómo transformar texto en una clasificación, cómo evitar evaluar paráfrasis casi idénticas a las de entrenamiento y cómo decidir si un modelo mejora una solución sencilla.

## Sesión sugerida de 90 minutos

| Tiempo | Actividad | Pregunta |
|---|---|---|
| 0–10 min | Definir las cinco categorías. | ¿Qué hacemos con una solicitud que menciona dos problemas? |
| 10–20 min | Probar mensajes en la interfaz. | ¿La palabra «internet» siempre indica un problema de red? |
| 20–35 min | Revisar frases, variantes y particiones. | ¿Una variante de la misma frase puede ir a prueba? |
| 35–50 min | Leer y ejecutar el pipeline. | ¿Dónde se aprende el vocabulario? |
| 50–65 min | Comparar Macro-F1 y matriz de confusión. | ¿Por qué las reglas ganaron en este experimento? |
| 65–75 min | Revisar puntajes, cobertura y explicación. | ¿Un puntaje alto garantiza una clasificación correcta? |
| 75–90 min | Analizar errores y proponer otra evaluación. | ¿Qué datos nuevos necesitamos antes de recomendar un cambio? |

## Ejercicio 1: negaciones y contexto

Prueba «Internet funciona, pero mi usuario no tiene permiso para entrar». Compara la regla con el modelo y argumenta la categoría correcta. Repite con una paráfrasis propia. No asumas que usar pares de palabras resuelve todas las negaciones.

## Ejercicio 2: variaciones de una misma familia

Abre `tickets.csv` y busca una familia. Sus saludos pueden cambiar, pero el problema de fondo es el mismo. Comprueba que todos sus registros aparezcan en una sola partición.

Discute por qué 24 variantes no son equivalentes a 24 tipos de problema independientes.

## Ejercicio 3: leer un error

En `test_predictions.csv`, filtra los casos donde `category` y `model_prediction` difieren. Elige uno y compara `baseline_prediction`. Distingue entre información insuficiente, vocabulario nuevo y posible confusión entre categorías. Una explicación del error es una hipótesis, no una demostración causal.

## Ejercicio 4: conservar la línea base

La regla obtuvo mejor Macro-F1 que el modelo. Redacta una recomendación de dos frases para la mesa de ayuda. Debe reconocer el resultado y proponer cómo reunir evidencia nueva, sin declarar al modelo superior por ser aprendizaje automático.

## Ejercicio 5: cobertura y revisión

Compara la exactitud sobre todos los mensajes con la exactitud sobre los que superan el umbral. Después revisa cuántos quedaron fuera. Explica por qué reportar solo el segundo porcentaje daría una visión incompleta.

## Ejercicio 6: tema ajeno

Escribe una consulta sobre cocina o viajes. El clasificador todavía devolverá una categoría conocida. Revisa si activa el aviso y por qué eso no constituye una evaluación suficiente de detección de temas externos.

## Adaptar el ejemplo

La estructura puede servir para clasificar incidentes, solicitudes administrativas, descripciones de gasto o documentos por tema. Antes de cambiar palabras o modelos, completa:

```text
Contexto y decisión que se quiere apoyar:
Unidad de observación:
Mensaje o documento disponible al inicio:
Categorías y reglas para distinguirlas:
Tratamiento de solicitudes ambiguas o con varias etiquetas:
Origen de datos y proceso de etiquetado:
Grupos que deben permanecer juntos:
Necesidad de separación temporal:
Línea base:
Métrica principal:
Costo de cada confusión:
Criterio de revisión y cobertura:
Prueba nueva reservada:
```

Para mejorar este caso, prioriza diversidad de problemas y revisión de etiquetas. Si se añaden datos o se cambia el modelo después de inspeccionar la prueba, reserva familias nuevas para una evaluación final independiente.
