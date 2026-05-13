# 🧪 Guía de Testing Manual de Endpoints

Este documento proporciona ejemplos de cómo probar manualmente cada endpoint de la API.

## 🔄 Flujo Recomendado de Testing

### Paso 1: Crear Libros

```bash
# Crear libro de alta demanda
curl -X POST "http://localhost:8000/libros" \
  -H "Content-Type: application/json" \
  -d '{
    "titulo": "Clean Code",
    "autor": "Robert C. Martin",
    "ubicacion": "Piso 1 - Sección A",
    "alta_demanda": true
  }'

# Respuesta esperada (201):
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "titulo": "Clean Code",
  "autor": "Robert C. Martin",
  "ubicacion": "Piso 1 - Sección A",
  "alta_demanda": true
}

# Guardar el id para pasos posteriores
# LIBRO_ID = "550e8400-e29b-41d4-a716-446655440000"
```

### Paso 2: Crear Estudiantes

```bash
# Crear estudiante de pregrado
curl -X POST "http://localhost:8000/estudiantes" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Juan Pérez",
    "programa": "Ingeniería de Sistemas",
    "semestre": 5,
    "tipo": "pregrado"
  }'

# Respuesta esperada (201):
{
  "id": "1a2b3c4d-5e6f-7g8h-9i0j-1k2l3m4n5o6p",
  "nombre": "Juan Pérez",
  "programa": "Ingeniería de Sistemas",
  "semestre": 5,
  "tipo": "pregrado",
  "multas_pendientes": 0.0
}

# Guardar el id
# ESTUDIANTE_ID = "1a2b3c4d-5e6f-7g8h-9i0j-1k2l3m4n5o6p"
```

### Paso 3: Listar Libros

```bash
# GET /libros
curl "http://localhost:8000/libros"

# Respuesta esperada (200):
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "titulo": "Clean Code",
    "autor": "Robert C. Martin",
    "ubicacion": "Piso 1 - Sección A",
    "alta_demanda": true
  }
]
```

### Paso 4: Listar Libros Disponibles

```bash
# GET /libros/disponibles
curl "http://localhost:8000/libros/disponibles"

# Respuesta esperada (200):
# Lista de libros que tienen al menos un ejemplar disponible
```

### Paso 5: Crear Préstamo (RN1-RN4, RN5, RN7)

```bash
# Nota: Los ejemplares se crean automáticamente en seed_data
# Para este test, necesitas ejecutar seed_data.py primero
python seed_data.py

# Luego, obtener IDs:
# Ejecutar: curl http://localhost:8000/libros/disponibles

# Crear préstamo
curl -X POST "http://localhost:8000/prestamos" \
  -H "Content-Type: application/json" \
  -d '{
    "estudiante_id": "1a2b3c4d-5e6f-7g8h-9i0j-1k2l3m4n5o6p",
    "ejemplar_id": "LIB001_EJE1"
  }'

# Respuesta esperada (201):
{
  "id": "9z8y7x6w-5v4u-3t2s-1r0q-9p8o7n6m5l4k",
  "estudiante_id": "1a2b3c4d-5e6f-7g8h-9i0j-1k2l3m4n5o6p",
  "ejemplar_id": "LIB001_EJE1",
  "fecha_prestamo": "2026-05-12",
  "fecha_devolucion_esperada": "2026-05-27",
  "fecha_devolucion_real": null,
  "estado": "activo",
  "renovado": false
}

# Guardar el id del préstamo
# PRESTAMO_ID = "9z8y7x6w-5v4u-3t2s-1r0q-9p8o7n6m5l4k"
```

## 🧪 Tests de Reglas de Negocio

### Test RN1: Límite de Préstamos

```bash
# Intentar crear más préstamos que el límite (3 para pregrado)
# Ejecutar 3 veces la creación de préstamo
# En la 4ta vez, debe retornar 409:

# Respuesta esperada (409):
{
  "detail": {
    "error": "limite_prestamos_alcanzado"
  }
}
```

### Test RN2: Bloqueo por Multas Pendientes

```bash
# Crear estudiante con multas (usando seed_data)
# Luego intentar crear préstamo:

# Respuesta esperada (409):
{
  "detail": {
    "error": "multas_pendientes"
  }
}
```

### Test RN3: Bloqueo por Préstamos Vencidos

```bash
# Obtener préstamos vencidos:
curl "http://localhost:8000/prestamos/vencidos"

# El sistema marca automáticamente como vencido si:
# fecha_actual > fecha_devolucion_esperada
```

### Test RN4: Disponibilidad de Ejemplar

```bash
# Crear un préstamo con un ejemplar ya prestado

# Respuesta esperada (409):
{
  "detail": {
    "error": "ejemplar_no_disponible"
  }
}
```

### Test RN5: Duración del Préstamo

```bash
# Crear libro de alta demanda (3 días)
{
  "titulo": "Libro Popular",
  "autor": "Autor",
  "ubicacion": "Loc",
  "alta_demanda": true
}

# Crear préstamo hoy 2026-05-12:
# fecha_devolucion_esperada debe ser 2026-05-15 (3 días)

# Crear libro normal (15 días)
{
  "titulo": "Libro Normal",
  "autor": "Autor",
  "ubicacion": "Loc",
  "alta_demanda": false
}

# Crear préstamo hoy 2026-05-12:
# fecha_devolucion_esperada debe ser 2026-05-27 (15 días)
```

### Test RN6: Renovación de Préstamo

```bash
# Renovar un préstamo activo
curl -X POST "http://localhost:8000/prestamos/PRESTAMO_ID/renovar"

# Respuesta esperada (200):
{
  "id": "9z8y7x6w-5v4u-3t2s-1r0q-9p8o7n6m5l4k",
  "fecha_devolucion_esperada": "2026-06-11",  # Extendido 15 días más
  "renovado": true
}

# Intentar renovar un préstamo devuelto (debe fallar):
# Respuesta esperada (409):
{
  "detail": {
    "error": "no_se_puede_renovar"
  }
}
```

### Test RN7: Control de Estado del Ejemplar

```bash
# Al crear un préstamo, el ejemplar cambia a "prestado"
# Al devolver, el ejemplar vuelve a "disponible"

# Verificar en seed_data.py después de crear un préstamo
# El ejemplar tiene estado "prestado"
```

### Test RN8: Cálculo de Multas

```bash
# Crear préstamo
curl -X POST "http://localhost:8000/prestamos" \
  -H "Content-Type: application/json" \
  -d '{
    "estudiante_id": "EST001",
    "ejemplar_id": "EJE001",
    "fecha_prestamo": "2026-05-01"
  }'

# Devolver con 2 días de retraso (fecha esperada 2026-05-16, devolver 2026-05-18)
curl -X POST "http://localhost:8000/prestamos/PRESTAMO_ID/devolver" \
  -H "Content-Type: application/json" \
  -d '{
    "fecha_devolucion_real": "2026-05-18"
  }'

# Respuesta esperada (200):
{
  "id": "PRESTAMO_ID",
  "estado": "devuelto",
  "fecha_devolucion_real": "2026-05-18"
}

# Verificar que se creó la multa:
# multas = 2 días * 2000 = 4000

# El estudiante debe tener multas_pendientes = 4000
curl "http://localhost:8000/estudiantes/EST001"

# Respuesta esperada (200):
{
  "id": "EST001",
  "multas_pendientes": 4000.0  # Suma de todas las multas
}
```

### Test RN9: Historial de Préstamos

```bash
# Obtener historial completo de un estudiante
curl "http://localhost:8000/estudiantes/EST001/historial"

# Respuesta esperada (200):
[
  {
    "id": "PRESTAMO1",
    "estado": "devuelto"
  },
  {
    "id": "PRESTAMO2",
    "estado": "activo"
  },
  ...
]
```

## 📊 Endpoints Completos

| Método | Endpoint | Body | Respuesta |
|--------|----------|------|-----------|
| GET | `/libros` | - | 200: lista de libros |
| GET | `/libros/{id}` | - | 200: libro o 404 |
| GET | `/libros/disponibles` | - | 200: libros disponibles |
| POST | `/libros` | título, autor, ubicación, alta_demanda | 201: libro creado |
| POST | `/prestamos` | estudiante_id, ejemplar_id, fecha_prestamo? | 201: préstamo o 409 |
| POST | `/prestamos/{id}/devolver` | fecha_devolucion_real? | 200: préstamo o 404/409 |
| POST | `/prestamos/{id}/renovar` | - | 200: préstamo o 404/409 |
| GET | `/prestamos/vencidos` | - | 200: lista vencidos |
| GET | `/prestamos/{id}` | - | 200: préstamo o 404 |
| POST | `/estudiantes` | nombre, programa, semestre, tipo | 201: estudiante |
| GET | `/estudiantes/{id}` | - | 200: estudiante o 404 |
| GET | `/estudiantes/{id}/prestamos` | - | 200: préstamos activos o 404 |
| GET | `/estudiantes/{id}/historial` | - | 200: historial o 404 |

## 🔗 URL Base

```
http://localhost:8000
```

## 📚 Documentación Interactiva

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 💡 Tips para Testing

1. **Usar Swagger UI** es más fácil que curl para pruebas manuales
2. **Copiar IDs** de respuestas para usarlos en próximos requests
3. **Ejecutar seed_data.py** para tener datos precargados
4. **Verificar logs** en la terminal donde corre la aplicación
5. **Usar pytest** para tests automatizados: `pytest -v`

## ❌ Errores Comunes

| Error | Causa | Solución |
|-------|-------|----------|
| 404 | Recurso no existe | Verificar ID correcto |
| 409 | Regla de negocio violada | Revisar validaciones en especificación |
| 400 | JSON malformado | Verificar sintaxis JSON |
| Connection refused | Servidor no está corriendo | Ejecutar `python main.py` |
