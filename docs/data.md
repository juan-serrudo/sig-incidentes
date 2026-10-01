# Contexto y datos

## Unidad de observación

Una fila representa **el mensaje inicial de una solicitud de soporte con una categoría principal**. El momento de clasificación es anterior a la resolución y a una asignación humana final.

La aplicación recibe solo `message`. No recibe categoría correcta, nombre del equipo resolutor, respuesta del técnico o estado final: esos campos revelarían información posterior.

## Definición de categorías

| Código | Categoría | Regla de interpretación |
|---|---|---|
| `access` | Accesos y permisos | Autenticación, credenciales y autorización de la cuenta. |
| `network` | Red y conectividad | Disponibilidad y funcionamiento de la conexión. |
| `hardware` | Equipos y periféricos | Componentes físicos y dispositivos. |
| `software` | Aplicaciones | Instalación, ejecución y funciones de programas. |
| `email` | Correo electrónico | Transporte, organización y configuración de mensajes. |

La categoría se decide por el problema principal, no por una palabra aislada. «Internet funciona, pero mi usuario no está autorizado» corresponde a acceso; mencionar internet no convierte automáticamente la solicitud en un problema de red.

Algunos casos reales pueden pertenecer a más de una categoría. Este ejemplo no modela etiquetas múltiples: conviene aclarar el problema principal o dividir solicitudes. Una contraseña de correo podría ser acceso, mientras que un mensaje que rebota sería correo, según esta taxonomía.

## Generación sintética

`templates.py` contiene 12 familias por categoría, 60 en total. Cada familia tiene dos paráfrasis de un mismo tipo de problema. El generador agrega saludos y cierres tomados de listas compartidas entre categorías.

La cantidad de variantes por familia es distinta: 24 para accesos, 20 para red, 16 para equipos, 18 para aplicaciones y 14 para correo. Hay 1.104 mensajes. La semilla 42 fija las elecciones y permite repetir el conjunto.

Los saludos y cierres no se diseñaron como indicadores de categoría. Aun así, un modelo pequeño puede aprender asociaciones accidentales del generador. Variar saludos no equivale a recolectar nuevos problemas independientes.

## Diccionario del CSV

| Campo | Uso |
|---|---|
| `ticket_id` | Identificador ficticio, por ejemplo `REQ-0001`. Solo auditoría. |
| `family_id` | Grupo de paráfrasis y variantes. Determina la partición. |
| `message` | Única entrada textual del modelo. |
| `category` | Etiqueta correcta definida al crear la familia. |
| `split` | Solo en archivos particionados: entrenamiento, validación o prueba. |

Ni `ticket_id`, ni `family_id`, ni `split` entran al vectorizador. El código de familia contiene la categoría y sería una fuga directa si se usara como entrada.

## Particiones por familia

| Categoría | Entrenamiento | Validación | Prueba | Total |
|---|---:|---:|---:|---:|
| Accesos y permisos | 192 | 48 | 48 | 288 |
| Red y conectividad | 160 | 40 | 40 | 240 |
| Equipos y periféricos | 128 | 32 | 32 | 192 |
| Aplicaciones | 144 | 36 | 36 | 216 |
| Correo electrónico | 112 | 28 | 28 | 168 |
| **Total** | **736** | **184** | **184** | **1.104** |

En cada categoría se reservan 8 familias para entrenar, 2 para validar y 2 para probar. Son 40, 10 y 10 familias respectivamente. Una familia nunca aparece en dos particiones.

Si se dividieran mensajes al azar, una variante podría estar en entrenamiento y otra casi idéntica en prueba. Separar familias reduce esa ventaja. No elimina todo parecido entre temas ni simula una evaluación temporal con solicitudes reales.

## Normalización y validación

La validación exige de 20 a 2.000 caracteres y al menos 10 letras. Se colapsan espacios repetidos. Se rechazan campos adicionales y valores que no sean texto.

Para detectar duplicados se pasa a minúsculas, se eliminan diacríticos y se normalizan puntuación y espacios. Dos mensajes que solo difieran en mayúsculas o signos se consideran duplicados. Las categorías deben ser conocidas y una familia no puede tener etiquetas contradictorias.

El vectorizador aplica su propio procesamiento documentado: minúsculas, normalización de acentos y extracción de palabras y pares de palabras. No se utiliza stemming ni una lista genérica de palabras vacías; términos como «no» pueden ser relevantes, aunque el modelo no comprende todas las negaciones.

## Qué falta para datos reales

Se necesitarían mensajes autorizados, una guía de etiquetado, revisión de desacuerdos, diversidad de redacción y tratamiento de duplicados e incidentes relacionados. Además habría que separar por conversación o incidente y reservar fechas futuras cuando se desee medir generalización temporal.

La simulación no representa nombres reales, conversaciones largas, abreviaturas variadas, archivos adjuntos, idiomas mezclados ni todas las formas de describir problemas. Las variantes de una familia están relacionadas; no son 1.104 casos independientes.
