# Especificación de la API REST Local

El backend del sistema está construido sobre **FastAPI** y expone una interfaz REST ligera para la inferencia, inspección de categorías y auditoría de métricas del modelo.

Frontend y backend se sirven desde el mismo proceso en `http://127.0.0.1:8991`.

---

## 1. Endpoints Disponibles

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/` | Interfaz gráfica demostrativa (`frontend/index.html`). |
| `GET` | `/api/health` | Estado del servicio y disponibilidad del modelo operativo. |
| `GET` | `/api/categories` | Catálogo de las 5 categorías técnicas de la UOIT y reglas de longitud. |
| `GET` | `/api/metrics` | Métricas consolidadas del experimento leídas de `artifacts/metrics.json`. |
| `POST` | `/api/classify` | Endpoint principal de clasificación de incidentes tecnológicos. |
| `GET` | `/docs` | Documentación interactiva Swagger / OpenAPI. |

---

## 2. Endpoint de Inferencia: `POST /api/classify`

### 2.1 Esquema de Entrada (`IncidentInput`)

El endpoint exige un objeto JSON con los datos textuales preliminares del ticket:

```json
{
  "title": "Agotamiento del pool de conexiones en base de datos PostgreSQL",
  "initial_description": "Alerta de monitoreo Zabbix: El cluster PostgreSQL alcanzo el limite de max_connections y las aplicaciones no pueden abrir nuevas sesiones. Se solicita intervencion de la guardia tecnica."
}
```

### 2.2 Reglas de Validación y Prevención de Fuga (*Data Leakage*)

- **`title` (string obligatorio):**
  - Longitud permitida: entre 5 y 200 caracteres.
  - Debe contener al menos 3 caracteres alfabéticos.
- **`initial_description` (string obligatorio):**
  - Longitud permitida: entre 15 y 2.000 caracteres.
  - Debe contener al menos 10 caracteres alfabéticos.
- **Prohibición de campos adicionales (`extra = "forbid"`):**
  - Cualquier campo posterior a la apertura del ticket (`category`, `resolution`, `root_cause`, `assignee`, `closing_text`, `solution`, etc.) es **estrictamente rechazado con código de error HTTP 422**.

### 2.3 Ejemplo de Invocación con cURL

```bash
curl -X POST http://127.0.0.1:8991/api/classify \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Agotamiento del pool de conexiones en base de datos PostgreSQL",
    "initial_description": "Alerta de monitoreo Zabbix: El cluster PostgreSQL alcanzo el limite max_connections y no se pueden abrir sesiones."
  }'
```

### 2.4 Esquema de Respuesta Exitosa (HTTP 200)

```json
{
  "suggested_category": "databases",
  "category": "databases",
  "category_name": "Bases de datos",
  "score": 0.8234,
  "ranking": [
    { "category": "databases", "name": "Bases de datos", "score": 0.8234 },
    { "category": "applications_services", "name": "Aplicaciones y servicios", "score": 0.0501 },
    { "category": "networks_connectivity", "name": "Redes y conectividad", "score": 0.0488 },
    { "category": "security_access", "name": "Seguridad y accesos", "score": 0.0405 },
    { "category": "infrastructure_storage", "name": "Infraestructura y almacenamiento", "score": 0.0371 }
  ],
  "top_3": [
    { "category": "databases", "name": "Bases de datos", "score": 0.8234 },
    { "category": "applications_services", "name": "Aplicaciones y servicios", "score": 0.0501 },
    { "category": "networks_connectivity", "name": "Redes y conectividad", "score": 0.0488 }
  ],
  "requires_review": false,
  "needs_review": false,
  "review_reason": "above_threshold",
  "review_threshold": 0.2209,
  "signals": [
    { "term": "base de", "contribution": 0.1099 },
    { "term": "datos", "contribution": 0.1082 },
    { "term": "postgresql", "contribution": 0.0581 }
  ],
  "baseline": {
    "category": "databases",
    "matches": { "databases": ["postgresql", "datos", "pool"] },
    "used_fallback": false
  },
  "model": "TF-IDF (Palabras + Caracteres) + Regresión Logística (C=1.0)",
  "model_version": "uoit-v1-f65c66ec",
  "latency_ms": 1.25,
  "synthetic_data": true
}
```

### 2.5 Campos de la Respuesta

- `suggested_category`: Identificador técnico de la categoría con mayor puntaje estimado.
- `category_name`: Nombre en español de la categoría recomendada.
- `score`: Puntaje estimado por el modelo para la categoría sugerida (no representa garantía absoluta de acierto).
- `ranking`: Lista ordenada de las 5 categorías con sus puntajes estimados.
- `top_3`: Las tres categorías más probables según el clasificador.
- `requires_review`: Bandera booleana que alerta al operador si la sugerencia amerita revisión humana.
- `review_reason`: Motivo de la revisión (`unknown_vocabulary`, `below_threshold` o `above_threshold`).
- `signals`: Términos léxicos que tuvieron mayor aporte positivo al logit de la categoría ganadora.
- `latency_ms`: Tiempo de ejecución medido en milisegundos en CPU.

---

## 3. Manejo de Errores

- **HTTP 422 (Unprocessable Entity):** Título demasiado corto/largo, descripción insuficiente, datos no textuales o inclusión de campos prohibidos que provocarían fuga de datos.
- **HTTP 503 (Service Unavailable):** El artefacto del modelo no se encuentra en memoria.
