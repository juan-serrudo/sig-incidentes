# Resultados del experimento

Clasificación de solicitudes iniciales en cinco categorías. Datos sintéticos en español; las cifras no prueban utilidad en una mesa de ayuda real.

## Datos separados por familia

| Partición | Mensajes | Familias |
|---|---:|---:|
| train | 736 | 40 |
| validation | 184 | 10 |
| test | 184 | 10 |

Las dos paráfrasis y todas las variantes de una familia permanecen en la misma partición. Se comprueban duplicados normalizados. El vocabulario se aprende solo con entrenamiento.

## Selección en validación

| C | Macro-F1 |
|---|---:|
| 1.0 | 0.7480 |
| 4.0 | 0.7562 |

C elegido: **4.0**. Umbral de revisión: **0.359218**.

## Prueba sobre todos los mensajes

| Métrica | Reglas por palabras | TF-IDF + regresión logística |
|---|---:|---:|
| Macro-F1 | 0.8778 | 0.7014 |
| F1 ponderado | 0.8803 | 0.7012 |
| Exactitud | 0.8859 | 0.7065 |

Las reglas superan al modelo en Macro-F1. Este experimento no justifica sustituirlas por el modelo; conviene ampliar la diversidad de datos y reservar una prueba nueva antes de otra comparación.

### Desempeño del modelo por categoría

| Categoría | Precisión | Recall | F1 | Casos |
|---|---:|---:|---:|---:|
| Accesos y permisos | 0.780 | 0.812 | 0.796 | 48 |
| Red y conectividad | 0.710 | 0.550 | 0.620 | 40 |
| Equipos y periféricos | 0.533 | 0.500 | 0.516 | 32 |
| Aplicaciones | 0.634 | 0.722 | 0.675 | 36 |
| Correo electrónico | 0.844 | 0.964 | 0.900 | 28 |

### Matriz de confusión

Filas = categoría real; columnas = predicción. Orden: access, network, hardware, software, email.

| Real / predicha | access | network | hardware | software | email |
|---|---:|---:|---:|---:|---:|
| access | 39 | 3 | 0 | 6 | 0 |
| network | 7 | 22 | 11 | 0 | 0 |
| hardware | 2 | 6 | 16 | 8 | 0 |
| software | 2 | 0 | 3 | 26 | 5 |
| email | 0 | 0 | 0 | 1 | 27 |

## Política de revisión, medida por separado

En validación se buscó máxima cobertura con exactitud de al menos 90% en un mínimo de 20 mensajes que superaran el umbral.
En prueba, cobertura: **63.6%** (117 mensajes); revisión marcada: **67**; exactitud entre los que superan el criterio: **88.9%**.
El subconjunto de prueba no alcanza el objetivo de exactitud de validación.
El Macro-F1 anterior incluye todos los mensajes, incluso los marcados para revisión. No se ocultan los casos difíciles para mejorar esa métrica.
El objetivo de validación no garantiza la misma exactitud en prueba ni en producción. Los puntajes no se calibraron como probabilidades de acierto.

## Límites

El texto proviene de 60 familias redactadas para la simulación. Hay lenguaje compartido entre familias; esta separación es más exigente que mezclar variantes, pero no representa conversaciones reales ni una evaluación temporal.
La prueba contiene solo dos familias por categoría. No se estiman intervalos de confianza; las variantes de una familia no son observaciones independientes.
El modelo siempre ordena las cinco categorías conocidas. Un puntaje alto no garantiza detectar un tema externo, una negación o varias intenciones. La revisión por puntaje es una ayuda limitada.
Los términos destacados son aportes positivos al puntaje lineal de la clase elegida; no explican causalidad ni representan toda la comparación entre clases.
La aplicación no crea tickets ni asigna equipos de forma automática. No mide tiempos de resolución, satisfacción o reducción de trabajo real.

## Reproducibilidad

Semilla: 42. SHA-256: `f1a93dc8ab3c6939ab5e8c0945b25ae4e916f934891c3139c666fc099248ad45`.
Versiones: `{'python': '3.12.14', 'scikit-learn': '1.9.1', 'pandas': '2.3.3', 'numpy': '2.2.6', 'fastapi': '0.115.14'}`.
