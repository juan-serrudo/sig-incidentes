# Modelo, evaluación y revisión

## Referencia por palabras clave

`baseline.py` define ocho palabras para cada categoría. El texto se normaliza y se cuentan coincidencias de palabras completas. Gana la categoría con más palabras distintas encontradas.

En empate se respeta el orden explícito de categorías de `settings.py`. Si no hay coincidencias, se usa la categoría más frecuente de entrenamiento: accesos. La interfaz informa cuándo se utiliza ese respaldo.

La regla no entiende contexto completo ni negaciones. Su vocabulario se fijó antes de calcular las métricas; no se modificó para corregir errores de prueba.

## TF-IDF y regresión logística

TF-IDF representa un mensaje mediante números asociados a palabras y pares de palabras. Considera presencia y frecuencia local junto a qué tan extendido está un término entre documentos de entrenamiento. No comprende el texto como una persona.

Se utilizan palabras individuales y pares consecutivos (`ngram_range=(1, 2)`), frecuencia mínima de dos documentos, frecuencia local suavizada con logaritmo y hasta 8.000 características. El vocabulario y sus pesos se aprenden solo en entrenamiento, dentro de un `Pipeline`.

La regresión logística compara las cinco clases. Se usa `class_weight="balanced"` para compensar las cantidades diferentes de mensajes. Esto no convierte los puntajes en probabilidades calibradas de acierto.

Se prueban `C = 1` y `C = 4`. Un C mayor supone menor regularización. Se elige por mayor Macro-F1 de validación; en empate se conserva el C menor. No se reentrena con validación después de elegir ni se reajustan parámetros mirando la prueba.

## Métricas sobre todos los mensajes

| Métrica | Interpretación |
|---|---|
| Precisión de una categoría | Entre los mensajes asignados a esa categoría, cuántos correspondían a ella. |
| Recall de una categoría | Entre los mensajes realmente de esa categoría, cuántos se recuperaron correctamente. |
| F1 de una categoría | Media armónica de su precisión y recall. |
| Macro-F1 | Promedio simple de los cinco F1. Cada categoría pesa lo mismo. |
| F1 ponderado | Promedio de los F1 ponderado por la cantidad real de casos por categoría. |
| Exactitud | Fracción total de mensajes correctamente clasificados. |
| Matriz de confusión | Conteos cruzados entre clase real y predicha; filas reales, columnas predichas. |

Macro-F1 es la métrica principal porque interesa que las categorías con menos ejemplos también funcionen. No es equivalente a exactitud ni a un porcentaje directo de mensajes correctos.

## Resultado y decisión

En la entrega, la regla obtiene Macro-F1 **0,8778** y el modelo **0,7014**. El modelo se conserva como objeto didáctico para explorar el proceso; el experimento **no respalda sustituir las reglas**.

Una hipótesis a investigar es que hay poca diversidad de problemas por categoría para aprender vocabulario que generalice a familias nuevas. No basta multiplicar saludos para resolverlo. Antes de comparar una mejora habría que ampliar los datos y reservar una prueba nueva; no ajustar frases para ganar sobre esta prueba ya inspeccionada.

## Cuándo se marca revisión

El modelo siempre produce un ranking de sus cinco clases. Para no presentar toda salida como una sugerencia igualmente utilizable, se añade un criterio separado:

1. En validación se calculan el puntaje máximo y si la categoría propuesta es correcta.
2. Se recorren los posibles umbrales de menor a mayor.
3. Se conserva el primero que consiga al menos 90% de exactitud entre un mínimo de 20 casos que lo superen. Ese primer umbral da la mayor cobertura entre los que satisfacen la condición.
4. Si ninguno cumple, se utiliza un umbral mayor que 1 y se pide revisión en todos los casos.
5. El umbral queda fijo para prueba e interfaz. Un texto sin vocabulario reconocido también activa revisión.

El 90% y los 20 casos son criterios didácticos, no requisitos universales. El umbral elegido es aproximadamente 0,3592; no significa 35,92% de probabilidad real de acertar.

Se informa **cobertura**: fracción que supera el criterio, y **exactitud del subconjunto**: aciertos únicamente entre esos casos. En prueba, 117 de 184 lo superan (63,6%) con exactitud 88,9%. **No se alcanza el objetivo de 90% buscado en validación**, y no se modifica el umbral para ocultarlo.

Las métricas principales y la matriz incluyen los 184 mensajes; no se excluyen los difíciles para elevar el Macro-F1. Superar el criterio no crea un ticket ni elimina la revisión humana.

## Explicación de términos

Para la clase propuesta, se calcula el valor TF-IDF de cada término presente multiplicado por su coeficiente en la regresión logística. Se muestran hasta cinco contribuciones positivas mayores.

Son aportes al puntaje lineal de esa clase. No representan causas, no incluyen necesariamente toda la evidencia negativa y no explican completamente la comparación con otras categorías. Un saludo podría aparecer por una asociación accidental de los datos sintéticos.

## Límites

La prueba tiene solo dos familias por categoría. No se calculan intervalos de confianza; para hacerlo habría que considerar familias completas como grupos, no suponer independencia entre variantes.

La regla de revisión no es un detector validado de temas externos. Un texto ajeno al soporte puede compartir vocabulario, recibir puntaje alto y ser mal clasificado. El modelo tampoco resuelve de forma confiable todos los mensajes con varios problemas o negaciones.

La separación por familias no es una partición temporal. Una evaluación operativa necesitaría mensajes reales representativos, grupos por incidente, fechas de llegada y un estudio del trabajo posterior a la sugerencia.

Las cifras vigentes y la matriz están en [el informe calculado](../artifacts/evaluation.md). Referencia técnica: [clasificación de documentos con características dispersas](https://scikit-learn.org/stable/auto_examples/text/plot_document_classification_20newsgroups.html).
