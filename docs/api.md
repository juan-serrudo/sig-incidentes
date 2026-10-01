# API local

## Rutas

| Método | Ruta | Función |
|---|---|---|
| GET | `/` | Interfaz del clasificador. |
| GET | `/api/health` | Disponibilidad del modelo. |
| GET | `/api/categories` | Categorías y límites del texto. |
| GET | `/api/metrics` | Métricas del experimento guardado. |
| POST | `/api/classify` | Clasificar un mensaje inicial. |
| GET | `/docs` | Documentación interactiva de FastAPI. |

Frontend y backend se sirven desde el mismo origen. No se necesita un servidor separado de frontend ni Node para ejecutar el ejemplo.

## Entrada

```json
{
  "message": "Mi cuenta está bloqueada y no puedo iniciar sesión. Necesito recuperar el acceso al portal de trabajo."
}
```

Se admiten entre 20 y 2.000 caracteres y al menos 10 letras. Se normalizan espacios repetidos. La API rechaza campos adicionales como `category` o `resolution`.

Para probar sin programar, abre http://127.0.0.1:8991/docs, expande `POST /api/classify`, pulsa **Try it out**, pega el JSON y pulsa **Execute**.

En una terminal de macOS o Linux:

```bash
curl -X POST http://127.0.0.1:8991/api/classify \
  -H 'Content-Type: application/json' \
  -d '{"message":"Mi usuario está bloqueado y no puedo iniciar sesión en el portal de trabajo."}'
```

## Respuesta

| Campo | Significado |
|---|---|
| `category`, `category_name` | Categoría con mayor puntaje; siempre pertenece a las cinco conocidas. |
| `score` | Puntaje máximo del modelo, no calibrado como probabilidad de acertar. |
| `ranking` | Las cinco categorías ordenadas con sus puntajes. |
| `needs_review` | Si se activa el aviso por umbral o vocabulario no reconocido. |
| `review_reason` | `unknown_vocabulary`, `below_threshold` o `above_threshold`. |
| `review_threshold` | Umbral fijo elegido en validación; >1 significa revisión de todos los mensajes. |
| `signals` | Hasta cinco términos con contribución positiva a la clase propuesta. |
| `baseline` | Categoría de la regla, palabras encontradas y uso de respaldo. |
| `model_version` | Identificador del modelo y huella del conjunto de datos. |
| `synthetic_data` | Siempre verdadero en este ejemplo. |

`needs_review = false` no significa asignar automáticamente. Todos los resultados son propuestas para examinar. Un mensaje ajeno al dominio podría no activar el aviso.

Las respuestas verificadas de los seis escenarios están en [example_predictions.json](../artifacts/example_predictions.json).

## Errores

- **422:** mensaje inválido, demasiado corto o largo, vacío, no textual o con campos adicionales.
- **503:** falta el modelo o su informe. Genera datos, entrena y reinicia.
- **Error al iniciar:** modelo, informe o categorías no corresponden. Vuelve a entrenar para mantener la consistencia.

Las consultas no se almacenan y no envían información a servicios de modelos externos.
