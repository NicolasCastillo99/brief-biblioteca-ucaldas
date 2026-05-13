# Arquitectura - Sistema de Préstamo de Libros

## Decisiones Arquitectónicas

### 1. Patrón: Layered Architecture (Arquitectura en Capas)

El proyecto sigue una arquitectura en capas clara:

```
┌─────────────────────┐
│   API REST (Routes) │
├─────────────────────┤
│   Services (BL)     │
├─────────────────────┤
│  Repositories (DA)  │
├─────────────────────┤
│   Models (Entities) │
└─────────────────────┘
```

**Ventajas:**
- Separación de responsabilidades clara
- Fácil testing (cada capa puede testearse independientemente)
- Mantenibilidad y escalabilidad
- Fácil agregar nuevas funcionalidades

### 2. Persistencia en Memoria

Se utilizan diccionarios de Python (`dict`) para almacenar datos:

```python
# BaseRepository
self.data: dict[str, T] = {}
```

**Justificación:**
- Requisito explícito de la especificación
- Simplicidad en fase inicial
- Suficiente para testing y demostración

**Limitación:** Los datos se pierden al reiniciar la aplicación.

### 3. Generación de IDs

Los IDs se generan usando `uuid.uuid4()`:

```python
import uuid
entity_id = str(uuid.uuid4())
```

**Justificación:**
- Garantiza unicidad global
- No requiere base de datos ni auto-incrementos
- Determinista y reproducible

### 4. Manejo de Excepciones Personalizadas

Se crearon excepciones específicas para cada regla de negocio:

- `LimitePrestamosAlcanzado` (RN1)
- `MultasPendientes` (RN2)
- `PrestamosVencidos` (RN3)
- `EjemplarNoDisponible` (RN4)
- `NoSePuedeRenovar` (RN6)
- `PrestamoNoActivo` (RN6)
- `PrestamoYaDevuelto` (RN8)

**Ventaja:** Manejo específico de errores en rutas, mejor comunicación con cliente.

### 5. Validación en Servicios

Toda la lógica de negocio y validaciones ocurren en los servicios, no en las rutas:

```
Route -> Service (validations + business logic) -> Repository -> Model
```

**Ventaja:** Lógica reutilizable, fácil testing, cambios en API no afectan servicios.

## Implementación de Reglas de Negocio

### RN1: Límite de Préstamos por Estudiante

```python
# PrestamoService.crear_prestamo()
prestamos_activos = self.prestamo_repo.get_activos_by_estudiante_id(estudiante_id)
limite = 3 if estudiante.tipo == "pregrado" else 5
if len(prestamos_activos) >= limite:
    raise LimitePrestamosAlcanzado()
```

### RN2: Bloqueo por Multas Pendientes

```python
if estudiante.multas_pendientes > 0:
    raise MultasPendientes()
```

### RN3: Bloqueo por Préstamos Vencidos

```python
prestamos_vencidos = self.prestamo_repo.get_vencidos_by_estudiante_id(estudiante_id)
if len(prestamos_vencidos) > 0:
    raise PrestamosVencidos()
```

### RN4: Disponibilidad de Ejemplar

```python
if ejemplar.estado != "disponible":
    raise EjemplarNoDisponible()
```

### RN5: Duración del Préstamo

```python
dias_prestamo = 3 if libro.alta_demanda else 15
fecha_devolucion_esperada = fecha_prestamo + timedelta(days=dias_prestamo)
```

### RN6: Renovación de Préstamo

```python
if prestamo.estado != "activo":
    raise PrestamoNoActivo()
# Extender fecha de devolución esperada
prestamo.fecha_devolucion_esperada += timedelta(days=dias_prestamo)
```

### RN7: Control de Estado del Ejemplar

```python
# Al crear préstamo:
ejemplar.estado = "prestado"

# Al devolver:
ejemplar.estado = "disponible"
```

### RN8: Cálculo de Multas

```python
dias_retraso = (fecha_devolucion_real - prestamo.fecha_devolucion_esperada).days
if dias_retraso > 0:
    monto = 2000 * dias_retraso
    multa = Multa(monto=monto, dias_retraso=dias_retraso, ...)
    # Actualizar multas_pendientes del estudiante
```

### RN9: Historial de Préstamos

```python
# GET /estudiantes/{id}/historial
def obtener_historial_prestamos_estudiante(estudiante_id):
    return self.prestamo_repo.get_by_estudiante_id(estudiante_id)
```

## Testing

### Cobertura

Se implementaron tests para:

- **Modelos** (`test_models/`): Validación de entidades
- **Servicios** (`test_services/`): Lógica de negocio y RN1-RN9
- **Rutas** (`test_routes/`): Endpoints REST

### Ejecución

```bash
# Todos los tests
pytest

# Con cobertura
pytest --cov=app

# Tests específicos
pytest tests/test_services/test_prestamo_service.py -v
```

## Flujos Principales

### 1. Flujo de Préstamo (Happy Path)

```
1. Cliente crea estudiante (POST /estudiantes)
2. Cliente crea libro (POST /libros)
3. Sistema crea ejemplar (internamente)
4. Cliente solicita préstamo (POST /prestamos)
   - Validar RN1-RN4, RN7
5. Sistema responde con préstamo activo (201)
```

### 2. Flujo de Devolución

```
1. Cliente registra devolución (POST /prestamos/:id/devolver)
   - Validar que préstamo es activo
   - Calcular multa (RN8)
   - Cambiar estado a "devuelto"
   - Liberar ejemplar
2. Sistema responde con préstamo actualizado (200)
```

### 3. Flujo de Renovación

```
1. Cliente solicita renovación (POST /prestamos/:id/renovar)
   - Validar RN6 (estado activo)
   - Extender fecha de devolución
2. Sistema responde con préstamo actualizado (200)
```

## Campos Agregados a la Especificación

### 1. `Libro.alta_demanda` (bool)

- **Razón:** Requerido por RN5 para determinar duración del préstamo
- **Valor por defecto:** False
- **Uso:** Diferencia entre libros de 3 días (alta demanda) y 15 días (normal)

### 2. `Ejemplar.estado` (default: "disponible")

- **Razón:** Simplificar inicialización
- **Estados:** "disponible", "prestado"

### 3. Endpoints no especificados

- `POST /libros` - Crear libros (testing interno)
- `POST /estudiantes` - Crear estudiantes (testing interno)
- `GET /libros/disponibles` ya está en especificación

## Mejoras Futuras

1. **Autenticación y Autorización**
   - JWT tokens
   - Roles de usuario

2. **Base de Datos Real**
   - PostgreSQL o MongoDB
   - ORM (SQLAlchemy)

3. **Sistema de Reservas**
   - Permitir que estudiantes reserven libros
   - Cola de espera

4. **Notificaciones**
   - Email de recordatorios
   - SMS de devoluciones vencidas

5. **Sistema de Pagos**
   - Integración con pasarela de pagos
   - Registro de pagos de multas

6. **API Avanzada**
   - Filtros y búsquedas avanzadas
   - Paginación
   - Sorting
   - Reportes

## Referencias

- **FastAPI:** https://fastapi.tiangolo.com/
- **Pytest:** https://pytest.org/
- **Python Dataclasses:** https://docs.python.org/3/library/dataclasses.html
