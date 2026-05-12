# Especificación Formal — Sistema de Préstamo de Libros

> **Autor:** Santiago Silva Guarnizo - Nicolas Castillo Galeano
> **Fecha:** 05/05/2026
> **Versión:** 1.0
> **Brief de origen:** Correo de Diana Restrepo, Coordinadora de Biblioteca

> Lo que está entre corchetes `[...]` es lo que tú debes escribir.

---

## 1. Propósito del sistema

Se trata de un sistema de prestamos de libros para una biblioteca universitaria mediante API. esta api debe permitir consultar catalogo y su disponibilidad, solicitud de prestamos, registros de devolucion, visualizacion de prestamos vigentes y notificaciones de prestamos vencidos.

---

## 2. Alcance

**Incluido en esta versión:**

- Gestión de catálogo de libros
- Consulta de disponibilidad de libros
- Registro de préstamos de libros a estudiantes
- Registro de devoluciones de libros
- Control de préstamos activos por estudiante
- Renovación de préstamos con validación de disponibilidad
- Cálculo automático de multas (2.000 por día de retraso)
- Historial de prestamos

**Explícitamente fuera del alcance:**

- Prestamo por parte de profesores investigadores
- Bases de datos (todo en memoria de momento)
- Servicio de autenticación
- Sistema de pago de multas
---

## 3. Modelo de datos

### Entidad: Libro

| Campo | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| `id` | `string` | sí | identificador único de inventario |
| `titulo` | `string` | sí | título del libro |
| `autor` | `string` | sí | autor del libro |
| `ubicacion` | `string` | sí | ubicación física en biblioteca |

---

### Entidad: Ejemplar

| Campo | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| `id` | `string` | sí | identificador único del ejemplar |
| `libro_id` | `string` | sí | referencia al libro |
| `estado` | `string` | sí | disponible / prestado |

---

### Entidad: Estudiante

| Campo | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| `id` | `string` | sí | código único del estudiante |
| `nombre` | `string` | sí | nombre del estudiante |
| `programa` | `string` | sí | programa académico |
| `semestre` | `number` | sí | semestre actual |
| `tipo` | `string` | sí | pregrado / posgrado |
| `multas_pendientes` | `number` | sí | total de multas sin pagar |

---

### Entidad: Préstamo

| Campo | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| `id` | `string` | sí | identificador del préstamo |
| `estudiante_id` | `string` | sí | referencia al estudiante |
| `ejemplar_id` | `string` | sí | referencia al ejemplar |
| `fecha_prestamo` | `date` | sí | fecha de inicio del préstamo |
| `fecha_devolucion_esperada` | `date` | sí | fecha límite de devolución |
| `fecha_devolucion_real` | `date` | no | fecha real de devolución |
| `estado` | `string` | sí | activo / devuelto / vencido |
| `renovado` | `boolean` | sí | indica si fue renovado |

---

### Entidad: Multa

| Campo | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| `id` | `string` | sí | identificador de la multa |
| `estudiante_id` | `string` | sí | estudiante sancionado |
| `prestamo_id` | `string` | sí | préstamo asociado |
| `monto` | `number` | sí | valor total de la multa |
| `dias_retraso` | `number` | sí | días de retraso |
| `pagada` | `boolean` | sí | estado de pago de la multa |
### Diagrama de relaciones

```

Libro 1 --- N Ejemplar
Estudiante 1 --- N Prestamo
Ejemplar 1 --- N Prestamo (a lo largo del tiempo)
Prestamo 0..1 --- 1 Multa

```

---

## 4. Endpoints REST

| Método | Ruta | Propósito | Body / Query | Respuesta éxito | Códigos error posibles |
|---|---|---|---|---|---|
| `GET` | `/libros` | Listar catálogo | filtros opcionales | `200` lista libros | - |
| `GET` | `/libros/:id` | Detalle libro | - | `200` libro | `404` |
| `GET` | `/libros/disponibles` | Libros disponibles | - | `200` lista | - |
| `POST` | `/prestamos` | Crear préstamo | `{estudiante_id, ejemplar_id}` | `201` préstamo | `400`, `404`, `409` |
| `POST` | `/prestamos/:id/devolver` | Registrar devolución | fecha opcional | `200` préstamo actualizado | `404`, `409` |
| `POST` | `/prestamos/:id/renovar` | Renovar préstamo | - | `200` préstamo | `404`, `409` |
| `GET` | `/estudiantes/:id/prestamos` | Préstamos activos | - | `200` lista | `404` |
| `GET` | `/estudiantes/:id/historial` | Historial completo | - | `200` lista | `404` |
| `GET` | `/prestamos/vencidos` | Listar vencidos | - | `200` lista | - |

---

## 5. Reglas de negocio

### RN1 — Límite de préstamos por estudiante

- **Trigger:** al recibir `POST /prestamos`.
- **Condición:**
  - Estudiante de pregrado: máximo 3 préstamos con `estado = "activo"`.
  - Estudiante de posgrado: máximo 5 préstamos con `estado = "activo"`.
- **Acción si cumple:** permitir la creación del préstamo.
- **Acción si no cumple:** retornar `409 Conflict` con `{error: "limite_prestamos_alcanzado"}`.

---

### RN2 — Bloqueo por multas pendientes

- **Trigger:** al recibir `POST /prestamos`.
- **Condición:** el estudiante tiene `multas_pendientes > 0`.
- **Acción si cumple:** bloquear el préstamo.
- **Acción si no cumple:** permitir continuar.
- **Acción si no cumple:** retornar `409 Conflict` con `{error: "multas_pendientes"}`.

---

### RN3 — Bloqueo por préstamos vencidos

- **Trigger:** al recibir `POST /prestamos`.
- **Condición:** el estudiante tiene al menos un préstamo con `estado = "vencido"`.
- **Acción si cumple:** bloquear el préstamo.
- **Acción si no cumple:** permitir continuar.
- **Acción si no cumple:** retornar `409 Conflict` con `{error: "prestamos_vencidos"}`.

---

### RN4 — Disponibilidad de ejemplar

- **Trigger:** al recibir `POST /prestamos`.
- **Condición:** el `ejemplar.estado` debe ser `"disponible"`.
- **Acción si cumple:** asignar el ejemplar al préstamo.
- **Acción si no cumple:** rechazar la operación.
- **Acción si no cumple:** retornar `409 Conflict` con `{error: "ejemplar_no_disponible"}`.

---

### RN5 — Duración del préstamo

- **Trigger:** al crear un préstamo.
- **Condición:**
  - Si `libro.alta_demanda = true` → 3 días.
  - Si no → 15 días.
- **Acción si cumple:** asignar `fecha_devolucion_esperada`.
- **Acción si no cumple:** no aplica.

---

### RN6 — Renovación de préstamo

- **Trigger:** al recibir `POST /prestamos/:id/renovar`.
- **Condición:**
  - El préstamo debe estar en estado `"activo"`.
  - No debe existir solicitud o restricción de otro estudiante sobre el libro.
- **Acción si cumple:** extender plazo (15 o 3 días según tipo).
- **Acción si no cumple:** no renovar.
- **Acción si no cumple:** retornar `409 Conflict` con `{error: "no_se_puede_renovar"}`.

---

### RN7 — Control de un solo ejemplar prestado

- **Trigger:** al recibir `POST /prestamos`.
- **Condición:** el `ejemplar.estado` debe ser `"disponible"`.
- **Acción si cumple:** marcar como `"prestado"`.
- **Acción si no cumple:** rechazar préstamo.
- **Acción si no cumple:** retornar `409 Conflict`.

---

### RN8 — Cálculo de multas por retraso

- **Trigger:** al registrar devolución (`POST /prestamos/:id/devolver`).
- **Condición:** `fecha_devolucion_real > fecha_devolucion_esperada`.
- **Acción si cumple:** calcular multa = `2000 * días_retraso`.
- **Acción si no cumple:** multa = 0.
- **Acción si no cumple:** continuar sin sanción.

---

### RN9 — Historial de préstamos

- **Trigger:** al consultar `GET /estudiantes/:id/historial`.
- **Condición:** estudiante existente.
- **Acción si cumple:** retornar todos los préstamos (activos y pasados).
- **Acción si no cumple:** retornar `404 Not Found`.

## 6. Decisiones tomadas (lo que el correo no dice)

## 6. Decisiones tomadas (lo que el correo no dice)

### D1 — Separación entre Libro y Ejemplar
- **Contexto:** el correo menciona libros con varios ejemplares, pero no define estructura.
- **Decisión:** modelar `Libro` y `Ejemplar` como entidades separadas.
- **Justificación:** permite controlar disponibilidad real por unidad física y no solo por título.

---

### D2 — Estados de préstamo
- **Contexto:** no se define el ciclo de vida del préstamo.
- **Decisión:** usar estados `activo`, `devuelto`, `vencido`.
- **Justificación:** simplifica el control de reglas de negocio y consultas.

---

### D3 — Manejo de multas
- **Contexto:** no se especifica sistema de pagos.
- **Decisión:** manejar solo registro de deuda en `multas_pendientes`.
- **Justificación:** la versión actual no incluye integración financiera.

---

### D4 — Cálculo de tiempo (días)
- **Contexto:** no se define si los días son hábiles o calendario.
- **Decisión:** usar días calendario.
- **Justificación:** simplifica implementación y evita ambigüedad.

---

### D5 — Renovaciones y “solicitudes de otros usuarios”
- **Contexto:** el correo menciona solicitudes de otros estudiantes pero no define cómo existen.
- **Decisión:** simularlo como validación lógica (flag o estado futuro de solicitud).
- **Justificación:** evita agregar un módulo adicional de reservas en esta fase.

---

### D6 — Identificación de estudiantes
- **Contexto:** se da código único pero no sistema de autenticación.
- **Decisión:** usar `id` como identificador único sin login.
- **Justificación:** esta versión es solo API interna, no sistema de seguridad.

---

### D7 — Notificaciones de vencimiento
- **Contexto:** se pide “avisar sobre préstamos vencidos”.
- **Decisión:** solo endpoint de consulta de vencidos, sin envío automático.
- **Justificación:** no hay integración con correo o push en esta versión.

---

### D8 — Persistencia en memoria
- **Contexto:** se menciona uso temporal antes de base de datos.
- **Decisión:** almacenar todo en estructuras en memoria (listas/diccionarios).
- **Justificación:** requisito explícito del alcance inicial del proyecto.

---


## 7. Códigos HTTP usados

| Código | Significado | Cuándo se usa |
|---|---|---|
| 200 | OK | GET exitosos |
| 201 | Created | POST exitosos que crean recursos |
| 400 | Bad Request | Body malformado o validación fallida |
| 404 | Not Found | Recurso no existe |
| 409 | Conflict | Reglas de negocio violadas (límite alcanzado, duplicado, etc.) |
| 500 | Internal Server Error | Error no controlado del servidor |


---

## 8. Restricciones técnicas

- **Stack:** [Python + FastAPI ]
- **Persistencia:** datos en memoria. No usar base de datos.
- **Sin autenticación** en esta versión.
- **Sin frontend** en esta versión. Solo API REST.
