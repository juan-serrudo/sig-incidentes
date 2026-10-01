# Diseño del Dataset y Taxonomía de Incidentes Tecnológicos

**Unidad:** Unidad de Operaciones e Infraestructura Tecnológica (UOIT)  
**Proyecto:** Clasificación automática de incidentes tecnológicos mediante procesamiento de lenguaje natural  
**Documento:** Definición de Taxonomía, Criterios de Frontera y Esquema de Datos  

---

## 1. Contexto y Objetivo del Dataset

El propósito del dataset es entrenar y evaluar modelos de aprendizaje automático capaces de sugerir la categoría técnica resolutora de un incidente tecnológico inmediatamente después de su registro inicial, antes de disponer de diagnóstico definitivo, técnico asignado, solución o texto de cierre.

Para garantizar estricta confidencialidad institucional, el dataset entregable es **100% sintético, reproducible y anonimizado**, pero modelado a partir de patrones operacionales técnicos reales observados en la gestión de infraestructura y servicios de tecnologías de información.

---

## 2. Definición de la Taxonomía (Cinco Categorías)

Se adopta una taxonomía mínima, cohesiva y académicamente defendible compuesta por **cinco categorías técnicas**:

| Identificador (Código) | Etiqueta en Interfaz | Alcance Tecnológico Principal |
|---|---|---|
| `applications_services` | Aplicaciones y servicios | Servicios web institucionales, portales, APIs, microservicios, ERP, middleware de aplicaciones, tareas programadas de software y errores HTTP 5xx originados en la lógica del aplicativo. |
| `databases` | Bases de datos | Motores de bases de datos relacionales y no relacionales (PostgreSQL, MySQL, Oracle), pools de conexiones (`pgbouncer`, etc.), bloqueos de transacciones, degradación de réplicas, corrupción de índices y tablas. |
| `networks_connectivity` | Redes y conectividad | Enlaces WAN corporativos, enrutamiento BGP/OSPF, conmutadores (switches), VLANs, túneles VPN corporativos, resolución DNS institucional y calidad del enlace Wi-Fi/cableado de sedes. |
| `infrastructure_storage` | Infraestructura y almacenamiento | Servidores físicos, hipervisores de virtualización (VMware, Proxmox), contenedores/Kubernetes a nivel de nodo, volúmenes de almacenamiento SAN/NAS, arreglos RAID, trabajos de backup y recuperación de instantáneas (snapshots). |
| `security_access` | Seguridad y accesos | Políticas de firewall perimetral, expiración de certificados SSL/TLS, autenticación centralizada (LDAP, Active Directory, Keycloak), gestión de permisos y llaves SSH, y alertas de seguridad de acceso. |

---

## 3. Criterios de Frontera y Desambiguación

En entornos de operaciones tecnológicas, los incidentes frecuentemente manifiestan síntomas cruzados. Para evitar ambigüedades en el etiquetado y asegurar que el modelo aprenda patrones consistentes con la información disponible en el momento de apertura, se establecen las siguientes reglas de desambiguación:

### 3.1 Aplicación vs. Base de Datos
- **Conflicto típico:** Una aplicación web muestra "Error 500: Database Connection Timeout" o las consultas de un portal se congelan.
- **Criterio de asignación:**
  - Si el síntoma inicial describe la falla de una pantalla, interfaz de usuario o excepción interna de código ("La vista de consulta de nómina lanza NullPointerException"), se clasifica como **`applications_services`**.
  - Si el síntoma inicial reporta explícitamente indisponibilidad, saturación del pool, desincronización de réplicas o agotamiento de conexiones en el motor de base de datos ("El cluster PostgreSQL alcanzó el límite de max_connections"), se clasifica como **`databases`**.

### 3.2 Red vs. Seguridad y Accesos
- **Conflicto típico:** Un usuario u host no puede conectarse a un servidor a través de la red corporativa.
- **Criterio de asignación:**
  - Si la causa observable inicial es una caída de enlace físico, pérdida de paquetes en la fibra, error de gateway o fallo de resolución DNS general, se clasifica como **`networks_connectivity`**.
  - Si la causa observable inicial es un rechazo de credenciales, token revocado, certificado SSL caducado, puerto bloqueado por regla de firewall perimetral o denegación en directorio activo, se clasifica como **`security_access`**.

### 3.3 Infraestructura vs. Almacenamiento (Unificadas en `infrastructure_storage`)
- **Justificación de la unificación:**
  - En la arquitectura de la UOIT, los hipervisores de virtualización y los arreglos de almacenamiento (SAN/NAS/RAID) están estrechamente interconectados (ej. un datastore NFS o iSCSI que deja de responder afecta de forma directa al hipervisor de cómputo).
  - Unificar ambas áreas en **`infrastructure_storage`** elimina una frontera excesivamente difusa que causaría inconsistencias en un dataset de tamaño acotado, manteniendo un balance óptimo entre resolución operativa y precisión del modelo.

---

## 4. Estructura y Esquema de la Unidad de Observación

La unidad de observación es:  
> **"Cada incidente tecnológico individual, considerando únicamente su título y descripción inicial disponibles antes de su clasificación y resolución definitivas."**

### Diccionario de Datos:
1. `incident_id` (str): Identificador unívoco del incidente ficticio (ej. `INC-2026-0001`). Solo para trazabilidad.
2. `event_group_id` (str): Identificador del grupo o familia del incidente (ej. `GRP-DB-01`). Permite agrupar variantes y paráfrasis de un mismo tipo de falla para el particionado.
3. `created_at` (str): Marca de tiempo en formato ISO 8601 (ej. `2026-03-10T08:15:00Z`).
4. `title` (str): Título o resumen sintético del incidente tal como lo ingresa el operador o sistema de monitoreo.
5. `initial_description` (str): Descripción detallada inicial provista al reportar el problema.
6. `category` (str): Etiqueta correcta correspondiente a una de las cinco categorías técnicas (`applications_services`, `databases`, `networks_connectivity`, `infrastructure_storage`, `security_access`).

### Variables Estrictamente Prohibidas (Prevención de Data Leakage):
Para evitar cualquier fuga de información sobre la resolución posterior o asignación final, los siguientes campos **NUNCA** forman parte de la entrada al modelo ni del esquema de inferencia:
- `resolution`
- `root_cause`
- `assignee`
- `closing_text`
- `solution`
- `final_assignment`

---

## 5. Estrategia de Partición y Prevención de Fuga

1. **Partición por Grupos (`Group Split`):**
   - La división entre `train.csv`, `validation.csv` y `test.csv` se realiza **estrictamente sobre `event_group_id`**.
   - Todas las variantes lingüísticas de una familia permanecen en una única partición.
   - De esta manera, el conjunto de prueba evalúa la capacidad de generalizar a familias técnicas completas no vistas en entrenamiento, eliminando la fuga por memorización de paráfrasis casi idénticas.
2. **Uso de Particiones:**
   - `train`: Ajuste de parámetros del modelo y vocabulario.
   - `validation`: Selección de hiperparámetros de regularización, comparación de arquitecturas y calibración de umbrales de revisión.
   - `test`: Evaluación final congelada ejecutada una sola vez.
