# Auditoria de Brechas de Endpoints y Reglas de Negocio

**Fecha:** 2026-05-19

**Proyecto auditado:** proyecto-v1 - API Biblioteca UCaldas

**Estado general del proyecto:** Parcialmente funcional. La API de `proyecto-v1` permite listar libros, consultar libros, crear prestamos basicos, devolver prestamos, listar prestamos vigentes y consultar prestamos por usuario. Sin embargo, el plan de pruebas de reglas de negocio exige una API mas completa basada en estudiantes, libros con alta demanda, ejemplares fisicos, multas, vencimientos, renovaciones y codigos HTTP especificos. Esas capacidades no existen aun en `proyecto-v1` o estan modeladas de forma insuficiente.

---

## Endpoints Faltantes / No Implementados

Los comandos del plan de pruebas estan escritos para una API con prefijo `/api` y entidades `estudiantes`, `libros`, `ejemplares` y `prestamos`. En `proyecto-v1` existen rutas mas simples (`/libros`, `/prestamos`, `/usuarios/{id}/prestamos`) y no existe la mayoria de la superficie esperada.

### Estudiantes

- `POST /api/estudiantes`
  - Requerido para crear estudiantes de pregrado y posgrado.
  - No existe en `proyecto-v1`; actualmente existe una tabla `usuarios`, pero no contiene `programa`, `semestre` ni `tipo`.

- `GET /api/estudiantes/{id}/historial`
  - Requerido para consultar historial de prestamos de un estudiante.
  - No existe en `proyecto-v1`; la ruta mas cercana es `GET /usuarios/{usuario_id}/prestamos`, pero usa IDs enteros y no el modelo de estudiante del plan.

### Libros

- `POST /api/libros`
  - Requerido para crear libros con `sala` y `altaDemanda`.
  - No existe en `proyecto-v1`; solo existen `GET /libros` y `GET /libros/{libro_id}`.

- `POST /api/libros/{id}/ejemplares`
  - Requerido para registrar copias fisicas indexadas de un libro.
  - No existe en `proyecto-v1`; el sistema solo maneja `cantidad_disponible` y `cantidad_total`, no ejemplares individuales.

### Prestamos

- `POST /api/prestamos`
  - Existe una funcionalidad similar como `POST /prestamos`, pero el contrato es diferente.
  - `proyecto-v1` espera `libro_id`, `usuario_id` y `dias_duracion`; el plan espera `estudianteId` y `ejemplarId`.
  - Faltan validaciones de limite por tipo de estudiante, ejemplar ya prestado, vencidos y multas.

- `PUT /api/prestamos/{id}/devolucion`
  - Requerido para registrar devolucion y calcular multa por retraso.
  - En `proyecto-v1` existe `POST /prestamos/{prestamo_id}/devolver`, pero no calcula multas ni usa el metodo/ruta del plan.

- `PUT /api/prestamos/{id}/renovar`
  - Requerido para validar renovacion y lista de espera.
  - No existe en `proyecto-v1`.

### Validacion HTTP

- Manejo global de errores de validacion como `400 Bad Request`.
  - FastAPI devuelve `422 Unprocessable Entity` por defecto en body vacio o tipos incorrectos.
  - El plan espera `400 Bad Request` para datos malformados.

---

## Reglas de Negocio Incumplidas

### RN2 - Posgrado: maximo 5 prestamos simultaneos

No esta implementada. `proyecto-v1` no distingue entre estudiantes de pregrado y posgrado. La entidad actual `Usuario` no tiene campo `tipo`, por lo que no puede aplicar un limite de 5 prestamos activos para posgrado.

### RN3 - Prestamo vencido bloquea nuevos prestamos

No esta implementada. Aunque `Prestamo` tiene estado `vencido`, el sistema no actualiza vencimientos ni bloquea nuevos prestamos si un usuario tiene prestamos vencidos. Tampoco existe endpoint administrativo o logica automatica para marcar prestamos vencidos.

### RN4 - Multa pendiente bloquea nuevos prestamos

No esta implementada. No existe tabla de multas, no existe estado de multa pendiente/pagada y la creacion de prestamos no valida deudas activas antes de prestar.

### RN5 - Ejemplar ya prestado no puede prestarse de nuevo

No esta implementada. `proyecto-v1` maneja disponibilidad agregada por libro (`cantidad_disponible`), pero no ejemplares individuales. Por eso no puede impedir que el mismo ejemplar fisico se preste dos veces.

### RN6-B - Plazo de alta demanda: 3 dias

No esta implementada. La tabla `libros` no tiene campo `alta_demanda`, y el endpoint de prestamos usa `dias_duracion` recibido en el body o el valor por defecto de 14 dias. No existe regla automatica de 3 dias para libros de alta demanda.

### RN7 - Renovacion denegada si hay lista de espera

No esta implementada. No existe endpoint de renovacion, no existe tabla de reservas/lista de espera y no hay validacion para denegar renovaciones cuando otro estudiante espera el mismo libro.

### RN8 - Calculo de multa por devolucion tardia

No esta implementada. La devolucion actual solo cambia estado a `devuelto`, registra `fecha_devolucion` y aumenta la disponibilidad. No calcula dias de retraso ni multa `N * 2000`.

---

## Observaciones QA / DevOps

- El plan de pruebas debe adaptarse a Python/FastAPI usando rutas reales o agregando rutas compatibles `/api/...`.
- Para automatizar la verificacion, conviene crear pruebas con `pytest` y `fastapi.testclient.TestClient` en lugar de depender de `curl` y `jq`.
- La persistencia SQLite ya existe, pero el esquema debe ampliarse con tablas y columnas para estudiantes, ejemplares, multas, reservas/lista de espera y reglas de prestamo.
- Debe agregarse un manejador global de `RequestValidationError` para transformar los `422` de FastAPI en `400 Bad Request`, como exige el plan.
