# 📊 Análisis Comparativo: Proyecto-v1 vs Proyecto-v2

## 1. 🛠️ Lenguaje y Framework Principal

| Aspecto | Proyecto-v1 | Proyecto-v2 |
|---------|-------------|-------------|
| **Lenguaje** | Python 3.10+ | Python 3.10+ |
| **Framework REST** | FastAPI 0.104.1 | FastAPI 0.104.1 |
| **Servidor** | Uvicorn | Uvicorn |
| **Testing** | Pytest (no hay tests) | Pytest 7.4.3 + pytest-asyncio |
| **Validación** | Pydantic (BaseModel) | Pydantic 2.5.0 |
| **Config** | Hardcoded | python-dotenv + config.py |

---

## 2. 🏗️ Estructura del Proyecto

### Proyecto-v1: Monolítico

```
proyecto-v1/
├── main.py                          # TODO en un archivo (≈320 líneas)
├── requirements.txt
└── README.md
```

**Características:**
- **Single File Architecture**: Toda la lógica en `main.py`
- **No hay separación de capas**: Modelos, endpoints, BD en memoria todo junto
- **Inline data**: Estructuras de datos inicializadas en el mismo archivo
- **Global state**: Variables globales (`libros_db`, `usuarios_db`, `prestamos_db`)
- **Líneas de código**: ~320 líneas

**File:** [proyecto-v1/main.py](proyecto-v1/main.py)

### Proyecto-v2: Arquitectura en Capas

```
proyecto-v2/
├── main.py                          # Punto de entrada (17 líneas)
├── app/
│   ├── config.py                   # Variables de entorno
│   ├── models/
│   │   └── entities.py             # Dataclasses: Libro, Ejemplar, Estudiante, Prestamo, Multa
│   ├── repositories/               # Data Access Layer
│   │   ├── base.py                 # BaseRepository genérico
│   │   ├── libro_repository.py
│   │   ├── ejemplar_repository.py
│   │   ├── estudiante_repository.py
│   │   ├── prestamo_repository.py
│   │   └── multa_repository.py
│   ├── services/                   # Business Logic Layer
│   │   ├── libro_service.py
│   │   ├── estudiante_service.py
│   │   └── prestamo_service.py
│   ├── routes/                     # API Layer
│   │   ├── libros.py
│   │   ├── prestamos.py
│   │   └── estudiantes.py
│   └── exceptions/
│       └── custom_exceptions.py    # Excepciones personalizadas
├── tests/
│   ├── conftest.py                # Fixtures
│   ├── test_models/               # Tests de entidades
│   ├── test_services/             # Tests de lógica de negocio
│   └── test_routes/               # Tests de endpoints
├── docs/
│   └── ARQUITECTURA.md            # Decisiones arquitectónicas
└── seed_data.py                   # Script de datos de prueba
```

**Características:**
- **Layered Architecture (4 capas)**:
  - Routes (API) → Services (Business Logic) → Repositories (Data Access) → Models (Entities)
- **Separación de responsabilidades clara**
- **Generic Base Repository** con TypeVar para reutilización
- **Dependency Injection** en servicios (inyección de repositorios)
- **Más archivos pero código mejor organizado**

---

## 3. ✅ Validación de Entrada

### Proyecto-v1

**Ubicación:** [proyecto-v1/main.py](proyecto-v1/main.py#L84-L116)

**Enfoque:**
- Validación **inline en endpoints** con `if` statements
- Usa **Pydantic BaseModel** para request/response
- **HTTPException directa** para errores
- No hay validaciones de reglas de negocio

**Ejemplo:**
```python
# main.py, líneas 100-104
if prestamo_create.libro_id not in libros_db:
    raise HTTPException(status_code=404, detail=f"Libro con ID {prestamo_create.libro_id} no encontrado")

if prestamo_create.usuario_id not in usuarios_db:
    raise HTTPException(status_code=404, detail=f"Usuario con ID {prestamo_create.usuario_id} no encontrado")
```

### Proyecto-v2

**Ubicación:** 
- Rutas: [proyecto-v2/app/routes/prestamos.py](proyecto-v2/app/routes/prestamos.py#L42-L99)
- Servicios: [proyecto-v2/app/services/prestamo_service.py](proyecto-v2/app/services/prestamo_service.py#L47-L105)

**Enfoque:**
- Validación **en servicios (capa de negocio)**
- **Excepciones personalizadas** para cada regla
- **Rutas delegan** a servicios
- Validaciones de reglas de negocio + disponibilidad

**Ejemplo:**
```python
# prestamo_service.py, líneas 72-75
prestamos_activos = self.prestamo_repo.get_activos_by_estudiante_id(estudiante_id)
limite_prestamos = 3 if estudiante.tipo == "pregrado" else 5
if len(prestamos_activos) >= limite_prestamos:
    raise LimitePrestamosAlcanzado()
```

---

## 4. 🚨 Manejo de Errores

### Proyecto-v1

**Estructura:**
- **Sin centralización**: Cada endpoint usa `HTTPException` directamente
- **Errores genéricos**: status_code 404, 400
- **Sin excepciones personalizadas**
- Sin documentación de errores

**Patrones encontrados:**
```python
# main.py, línea 111-113
raise HTTPException(
    status_code=400, 
    detail=f"No hay copias disponibles del libro '{libro.titulo}'"
)
```

### Proyecto-v2

**Estructura:**
- **Excepciones personalizadas**: [proyecto-v2/app/exceptions/custom_exceptions.py](proyecto-v2/app/exceptions/custom_exceptions.py)
- **Manejo centralizado** en rutas
- **Errores específicos por regla de negocio**
- Mapping automático de excepciones a HTTP status

**Excepciones definidas:**
```python
# custom_exceptions.py
- BibliotecaException (base)
- LimitePrestamosAlcanzado (RN1)
- MultasPendientes (RN2)
- PrestamosVencidos (RN3)
- EjemplarNoDisponible (RN4)
- NoSePuedeRenovar (RN6)
- PrestamoNoActivo (RN6)
- PrestamoYaDevuelto (RN8)
- ResourceNotFound
```

**Manejo en rutas:**
```python
# prestamos.py, líneas 73-84
except LimitePrestamosAlcanzado:
    raise HTTPException(
        status_code=409,
        detail={"error": "limite_prestamos_alcanzado"},
    )
```

---

## 5. 🏷️ Seguridad de Tipos

### Proyecto-v1

**Tipo Checking:**
- **Pydantic models** para request/response
- **Type hints básicos** en algunos lugares
- **Sin type checking en lógica**
- No hay validación de tipos en servidor

**Modelos:**
```python
# main.py, líneas 7-18
class Libro(BaseModel):
    id: int
    titulo: str
    isbn: str
    cantidad_disponible: int
    cantidad_total: int
```

### Proyecto-v2

**Tipo Checking:**
- **Dataclasses** con type hints completos
- **Type hints en servicios y repositorios**
- **Generic BaseRepository[T]** con TypeVar
- **Type hints en funciones** (parámetros y retorno)

**Modelos:**
```python
# entities.py, líneas 1-15
@dataclass
class Libro:
    id: str
    titulo: str
    autor: str
    ubicacion: str
    alta_demanda: bool = False

@dataclass
class Ejemplar:
    id: str
    libro_id: str
    estado: str = "disponible"
```

**Type safety en servicios:**
```python
# prestamo_service.py
def crear_prestamo(
    self,
    estudiante_id: str,
    ejemplar_id: str,
    fecha_prestamo: Optional[date] = None,
) -> Prestamo:  # Retorno explícito
```

---

## 6. 🧪 Tests

### Proyecto-v1

**Tests:** ❌ No hay tests

**Archivos:** No existe directorio `tests/`

### Proyecto-v2

**Cobertura Extensa:** ✅ Tests en 3 niveles

**Ubicación:** [proyecto-v2/tests/](proyecto-v2/tests/)

#### 6.1 Tests de Modelos
**Archivo:** [tests/test_models/test_entities.py](proyecto-v2/tests/test_models/test_entities.py)

```python
def test_crear_libro():
    """Test para crear una entidad Libro"""
    libro = Libro(...)
    assert libro.id == "LIB001"

def test_crear_estudiante():
    """Test para crear una entidad Estudiante"""
    estudiante = Estudiante(...)
    assert estudiante.tipo == "pregrado"
```

#### 6.2 Tests de Servicios
**Archivo:** [tests/test_services/test_prestamo_service.py](proyecto-v2/tests/test_services/test_prestamo_service.py)

Cobertura de reglas de negocio:

```python
class TestRN1_LimitePrestamos:
    """Tests para RN1: Límite de préstamos por estudiante"""
    
    def test_pregrado_puede_crear_3_prestamos():
        """Pregrado máximo 3 activos"""
    
    def test_posgrado_puede_crear_5_prestamos():
        """Posgrado máximo 5 activos"""
```

#### 6.3 Tests de Rutas
**Archivo:** [tests/test_routes/test_libros_routes.py](proyecto-v2/tests/test_routes/test_libros_routes.py)

```python
class TestLibrosRoutes:
    def test_listar_libros_vacio()
    def test_crear_libro()
    def test_obtener_libro()
    def test_obtener_libro_no_existe()
```

**Framework:** `pytest` + `TestClient` de FastAPI

---

## 7. 🚀 Punto de Entrada

### Proyecto-v1

**Archivo:** [proyecto-v1/main.py](proyecto-v1/main.py#L257-L259)

```python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**Configuración:**
- Puerto hardcoded: `8000`
- Host hardcoded: `0.0.0.0`
- Datos cargados al iniciar (variables globales)

### Proyecto-v2

**Archivo:** [proyecto-v2/main.py](proyecto-v2/main.py)

```python
import uvicorn
from fastapi import FastAPI
from app.config import DEBUG, PORT, HOST
from app.routes import libros, prestamos, estudiantes

app = FastAPI(...)

app.include_router(libros.router)
app.include_router(prestamos.router)
app.include_router(estudiantes.router)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=DEBUG,
    )
```

**Configuración:**
- Variables desde `.env` via [config.py](proyecto-v2/app/config.py)
- Routers registrados dinámicamente
- Modo reload desde configuración
- **Script seed_data.py** para datos iniciales

---

## 8. 📋 Reglas de Negocio (RN) - Implementación Detallada

### Regla RN1: Límite de Préstamos por Estudiante

**Descripción:** El estudiante debe tener un límite máximo de préstamos activos según su tipo.

#### Proyecto-v1
**Status:** ❌ NO IMPLEMENTADA

El proyecto-v1 no tiene límites de préstamos. No existe validación de esto.

#### Proyecto-v2
**Status:** ✅ IMPLEMENTADA

**Ubicación:** [proyecto-v2/app/services/prestamo_service.py](proyecto-v2/app/services/prestamo_service.py#L72-L76)

```python
# Líneas 72-76
# RN1: Verificar límite de préstamos activos
prestamos_activos = self.prestamo_repo.get_activos_by_estudiante_id(
    estudiante_id
)
limite_prestamos = 3 if estudiante.tipo == "pregrado" else 5
if len(prestamos_activos) >= limite_prestamos:
    raise LimitePrestamosAlcanzado()
```

**Rango:** Líneas 72-76 en `prestamo_service.py`

**Dependencias:**
- [PrestamoRepository.get_activos_by_estudiante_id()](proyecto-v2/app/repositories/prestamo_repository.py#L9-L16): Filtra préstamos activos
- [Estudiante.tipo](proyecto-v2/app/models/entities.py#L28): Campo que determina el límite

**Excepciones:**
- [LimitePrestamosAlcanzado](proyecto-v2/app/exceptions/custom_exceptions.py#L12-L16): Excepción personalizada

**Tests:**
- [TestRN1_LimitePrestamos](proyecto-v2/tests/test_services/test_prestamo_service.py#L45)
  - test_pregrado_puede_crear_3_prestamos()
  - test_posgrado_puede_crear_5_prestamos()

**Flujo Completo:**
1. Route llama → [prestamos.py, línea 70](proyecto-v2/app/routes/prestamos.py#L70): `prestamo_service.crear_prestamo()`
2. Service valida → [prestamo_service.py, líneas 72-76](proyecto-v2/app/services/prestamo_service.py#L72-L76): RN1
3. Si excede límite → Lanza [LimitePrestamosAlcanzado](proyecto-v2/app/exceptions/custom_exceptions.py#L12-L16)
4. Route captura → [prestamos.py, líneas 74-79](proyecto-v2/app/routes/prestamos.py#L74-L79): Retorna 409

---

### Regla RN2: Bloqueo por Multas Pendientes

#### Proyecto-v1
**Status:** ❌ NO IMPLEMENTADA

#### Proyecto-v2
**Status:** ✅ IMPLEMENTADA

**Ubicación:** [proyecto-v2/app/services/prestamo_service.py](proyecto-v2/app/services/prestamo_service.py#L78-L81)

```python
# Líneas 78-81
# RN2: Verificar multas pendientes
if estudiante.multas_pendientes > 0:
    raise MultasPendientes()
```

**Span:** 4 líneas (78-81)

---

### Regla RN3: Bloqueo por Préstamos Vencidos

#### Proyecto-v1
**Status:** ❌ NO IMPLEMENTADA

#### Proyecto-v2
**Status:** ✅ IMPLEMENTADA

**Ubicación:** [proyecto-v2/app/services/prestamo_service.py](proyecto-v2/app/services/prestamo_service.py#L83-L88)

```python
# Líneas 83-88
# RN3: Verificar préstamos vencidos
prestamos_vencidos = self.prestamo_repo.get_vencidos_by_estudiante_id(
    estudiante_id
)
if len(prestamos_vencidos) > 0:
    raise PrestamosVencidos()
```

**Span:** 6 líneas (83-88)

---

### Regla RN4: Disponibilidad de Ejemplar

#### Proyecto-v1
**Status:** ❌ Parcial (solo cantidad disponible)

[proyecto-v1/main.py](proyecto-v1/main.py#L111-114):
```python
if libro.cantidad_disponible <= 0:
    raise HTTPException(
        status_code=400, 
        detail=f"No hay copias disponibles del libro '{libro.titulo}'"
    )
```

#### Proyecto-v2
**Status:** ✅ IMPLEMENTADA (estado del ejemplar)

[proyecto-v2/app/services/prestamo_service.py](proyecto-v2/app/services/prestamo_service.py#L90-U93):
```python
# Líneas 90-93
# RN4: Verificar disponibilidad del ejemplar
if ejemplar.estado != "disponible":
    raise EjemplarNoDisponible()
```

---

### Regla RN5: Duración del Préstamo según Demanda

#### Proyecto-v1
**Status:** ❌ NO IMPLEMENTADA (hardcoded a 14 días)

[proyecto-v1/main.py](proyecto-v1/main.py#L115-U119):
```python
# Línea 35: hardcoded
dias_duracion: int = 14
```

#### Proyecto-v2
**Status:** ✅ IMPLEMENTADA

**Ubicación:** [proyecto-v2/app/services/prestamo_service.py](proyecto-v2/app/services/prestamo_service.py#L95-U99)

```python
# Líneas 95-99
# RN5: Calcular fecha de devolución esperada
if fecha_prestamo is None:
    fecha_prestamo = date.today()

dias_prestamo = 3 if libro.alta_demanda else 15
fecha_devolucion_esperada = fecha_prestamo + timedelta(days=dias_prestamo)
```

**Span:** 5 líneas (95-99)

**Dependencia:** Campo [Libro.alta_demanda](proyecto-v2/app/models/entities.py#L10)

---

### Regla RN6: Renovación de Préstamo

#### Proyecto-v1
**Status:** ❌ NO IMPLEMENTADA

#### Proyecto-v2
**Status:** ✅ IMPLEMENTADA

**Ubicación:** [proyecto-v2/app/services/prestamo_service.py](proyecto-v2/app/services/prestamo_service.py#L178-U210)

```python
# Líneas 178-210
def renovar_prestamo(self, prestamo_id: str) -> Prestamo:
    """
    Renovar un préstamo extendiendo su plazo.
    
    Valida:
    - RN6: Debe estar en estado "activo"
    - RN6: No debe existir restricción sobre el libro
    """
    # Verificaciones...
```

**Span:** 33 líneas (178-210)

---

### Regla RN7: Control de Estado del Ejemplar

#### Proyecto-v1
**Status:** ❌ Parcial (solo incrementa/decrementa cantidad)

[proyecto-v1/main.py](proyecto-v1/main.py#L132-U134):
```python
# Reducir cantidad disponible
libro.cantidad_disponible -= 1
```

#### Proyecto-v2
**Status:** ✅ IMPLEMENTADA (cambio de estado)

**Al crear préstamo:**
[proyecto-v2/app/services/prestamo_service.py](proyecto-v2/app/services/prestamo_service.py#L107-U109)
```python
# Líneas 107-109
# RN7: Cambiar estado del ejemplar a "prestado"
ejemplar.estado = "prestado"
self.ejemplar_repo.update(ejemplar_id, ejemplar)
```

**Al devolver:**
[proyecto-v2/app/services/prestamo_service.py](proyecto-v2/app/services/prestamo_service.py#L167-U171)
```python
# Líneas 167-171
# Liberar el ejemplar (cambiar estado a "disponible")
ejemplar = self.ejemplar_repo.get_by_id(prestamo.ejemplar_id)
if ejemplar:
    ejemplar.estado = "disponible"
    self.ejemplar_repo.update(prestamo.ejemplar_id, ejemplar)
```

---

### Regla RN8: Cálculo de Multas por Retraso

#### Proyecto-v1
**Status:** ❌ NO IMPLEMENTADA

#### Proyecto-v2
**Status:** ✅ IMPLEMENTADA

**Ubicación:** [proyecto-v2/app/services/prestamo_service.py](proyecto-v2/app/services/prestamo_service.py#L145-U166)

```python
# Líneas 145-166
# RN8: Calcular multa si hay retraso
dias_retraso = (
    fecha_devolucion_real - prestamo.fecha_devolucion_esperada
).days
if dias_retraso > 0:
    monto_multa = 2000 * dias_retraso
    multa_id = str(uuid.uuid4())
    multa = Multa(
        id=multa_id,
        estudiante_id=prestamo.estudiante_id,
        prestamo_id=prestamo_id,
        monto=monto_multa,
        dias_retraso=dias_retraso,
        pagada=False,
    )
    self.multa_repo.create(multa, multa_id)

    # Actualizar multas_pendientes del estudiante
    estudiante = self.estudiante_repo.get_by_id(prestamo.estudiante_id)
    if estudiante:
        estudiante.multas_pendientes += monto_multa
        self.estudiante_repo.update(prestamo.estudiante_id, estudiante)
```

**Span:** 22 líneas (145-166)

**Parámetros:**
- Costo por día: 2000 unidades
- Cálculo: `dias_retraso * 2000`

---

### Resumen de Implementación de Reglas

| RN | Descripción | v1 | v2 | Ubicación v2 |
|---|---|---|---|---|
| RN1 | Límite de préstamos | ❌ | ✅ | [prestamo_service.py:72-76](proyecto-v2/app/services/prestamo_service.py#L72-L76) |
| RN2 | Bloqueo por multas | ❌ | ✅ | [prestamo_service.py:78-81](proyecto-v2/app/services/prestamo_service.py#L78-L81) |
| RN3 | Bloqueo por vencidos | ❌ | ✅ | [prestamo_service.py:83-88](proyecto-v2/app/services/prestamo_service.py#L83-L88) |
| RN4 | Disponibilidad ejemplar | ✅ Parcial | ✅ | [prestamo_service.py:90-93](proyecto-v2/app/services/prestamo_service.py#L90-L93) |
| RN5 | Duración según demanda | ❌ | ✅ | [prestamo_service.py:95-99](proyecto-v2/app/services/prestamo_service.py#L95-L99) |
| RN6 | Renovación | ❌ | ✅ | [prestamo_service.py:178-210](proyecto-v2/app/services/prestamo_service.py#L178-L210) |
| RN7 | Control estado ejemplar | ✅ Parcial | ✅ | [prestamo_service.py:107-109, 167-171](proyecto-v2/app/services/prestamo_service.py#L107-L109) |
| RN8 | Cálculo multas | ❌ | ✅ | [prestamo_service.py:145-166](proyecto-v2/app/services/prestamo_service.py#L145-L166) |

---

## 9. 📦 Modelos de Datos

### Proyecto-v1

**Ubicación:** [proyecto-v1/main.py](proyecto-v1/main.py#L7-U52)

**Modelos Pydantic (7 clases):**

```python
class Libro(BaseModel):
    id: int
    titulo: str
    autor: str
    isbn: str
    cantidad_disponible: int
    cantidad_total: int

class Usuario(BaseModel):
    id: int
    nombre: str
    email: str
    carnet: str

class PrestamoCreate(BaseModel):
    libro_id: int
    usuario_id: int
    dias_duracion: int = 14

class Prestamo(BaseModel):
    id: int
    libro_id: int
    usuario_id: int
    fecha_prestamo: datetime
    fecha_vencimiento: datetime
    fecha_devolucion: Optional[datetime] = None
    estado: EstadoPrestamo

class PrestamoResponse(Prestamo):
    libro_titulo: str
    usuario_nombre: str
```

**Almacenamiento en memoria:**
```python
libros_db = {...}      # dict[int, Libro]
usuarios_db = {...}    # dict[int, Usuario]
prestamos_db = {}      # dict[int, Prestamo]
prestamo_counter = 1
```

**Características:**
- IDs numéricos (auto-incremento con contador)
- Usuario, no Estudiante
- Campo `cantidad_total` y `cantidad_disponible`
- Modelo separado PrestamoCreate
- sin Multa, sin Ejemplar

### Proyecto-v2

**Ubicación:** [proyecto-v2/app/models/entities.py](proyecto-v2/app/models/entities.py)

**Modelos Dataclass (5 clases):**

```python
@dataclass
class Libro:
    id: str
    titulo: str
    autor: str
    ubicacion: str
    alta_demanda: bool = False

@dataclass
class Ejemplar:
    id: str
    libro_id: str
    estado: str = "disponible"

@dataclass
class Estudiante:
    id: str
    nombre: str
    programa: str
    semestre: int
    tipo: str  # pregrado / posgrado
    multas_pendientes: float = 0.0

@dataclass
class Prestamo:
    id: str
    estudiante_id: str
    ejemplar_id: str
    fecha_prestamo: date
    fecha_devolucion_esperada: date
    fecha_devolucion_real: Optional[date] = None
    estado: str = "activo"
    renovado: bool = False

@dataclass
class Multa:
    id: str
    estudiante_id: str
    prestamo_id: str
    monto: float
    dias_retraso: int
    pagada: bool = False
```

**Almacenamiento en memoria:**
```python
# Usado en BaseRepository
self.data: dict[str, T] = {}
```

**Características:**
- IDs tipo UUID (str)
- Estudiante con tipo (pregrado/posgrado)
- Ejemplar como entidad separada
- Modelo Multa independiente
- Campo `multas_pendientes` en Estudiante
- Campo `renovado` en Prestamo

---

## 🔍 Comparación Detallada: Modelos

| Característica | v1 | v2 |
|---|---|---|
| **Tipo de ID** | int (auto-increment) | str (UUID) |
| **Estudiantes vs Usuarios** | Usuario | Estudiante + tipo |
| **Libros** | Cantidad disponible/total | Alta demanda flag |
| **Ejemplar** | No existe | Entidad separada |
| **Multa** | No existe | Entidad con cálculo |
| **Estados** | EstadoPrestamo enum | str ("activo"/"devuelto"/...) |
| **Tipos de Datos** | Pydantic + datetime | Dataclass + date |

---

## 📊 Tabla Resumen Global

| Aspecto | Proyecto-v1 | Proyecto-v2 |
|---|---|---|
| **Lenguaje** | Python 3.10+ | Python 3.10+ |
| **Framework** | FastAPI 0.104.1 | FastAPI 0.104.1 |
| **Estructura** | Monolítica (1 archivo) | Capas (5 capas) |
| **Archivos** | 3 | 18+ |
| **Separación** | Ninguna | Clara (Routes→Services→Repos→Models) |
| **Validación** | En endpoints | En servicios |
| **Errores** | HTTPException genérica | Excepciones personalizadas |
| **Type Safety** | Pydantic models | Dataclasses + Type hints |
| **Tests** | 0 | 15+ test cases |
| **Reglas Negocio** | 0/8 implementadas | 8/8 implementadas ✅ |
| **Documentación** | README básico | README + ARQUITECTURA.md + inline docs |
| **Datos Iniciales** | Hardcoded | seed_data.py |
| **Configuración** | Hardcoded | .env + config.py |
| **IDs** | Integer counter | UUID |
| **Modelos** | 6 (Pydantic) | 5 (Dataclass) |
| **Persistencia** | dict global | dict en BaseRepository |

---

## 🎓 Conclusiones

### Proyecto-v1: MVP Simple
- ✅ Rápido de entender
- ✅ Funcional para demostración
- ❌ No escalable
- ❌ Difícil de testear
- ❌ Sin reglas de negocio complejas
- ❌ Acoplado

### Proyecto-v2: Arquitectura Profesional
- ✅ Bien estructurado
- ✅ Fácil de testear (cobertura)
- ✅ Escalable
- ✅ Mantenible
- ✅ Todas las reglas implementadas
- ✅ Documentado
- ❌ Más archivos (complejidad inicial)

**Recomendación:** v2 es la arquitectura producción-ready. v1 es un buen punto de partida educativo que evolucionó a v2.
