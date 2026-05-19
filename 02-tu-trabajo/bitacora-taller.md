# Respuestas Taller de Análisis v1 vs v2 — Sistema de Préstamo de Libros
**Institución:** Universidad de Caldas  
**Asignatura:** Taller de Pruebas de Software  
**Fecha:** 19 de mayo de 2026  
**Autores:** Nicolás Castillo Galeano, Santiago Silva Guarnizo

---

## Bloque 1 — Lectura y Comparación Estructural

### Ejercicio 1.1 — Inventario de Diferencias

| Dimensión | v1 | v2 |
|---|---|---|
| **Lenguaje** | Python (FastAPI) | Python (FastAPI) |
| **Validación de entradas al servidor** | Pydantic en los modelos de request/response; validación básica de tipos y algunos `if` dentro de los endpoints | Modelos tipados y validaciones de reglas de negocio en la capa de servicios |
| **Manejo de errores HTTP** | HTTPException genérica; códigos HTTP inconsistentes (ej: 400 vs 409) | Excepciones de dominio customizadas; códigos HTTP específicos por tipo de error |
| **Arquitectura (número de capas)** | 1 capa (monolítica) — todo en `main.py`: modelos, lógica, rutas, persistencia | 4 capas: Routes (presentación), Services (casos de uso), Repositories (persistencia), Models (dominio) |
| **Tests incluidos** | Ninguno | Tests de modelos, servicios y rutas con Pytest |
| **Tipado de datos** | Tipado en Pydantic models, pero sin separar tipos de dominio ni repositorios | Entidades y servicios con anotaciones de tipo; reglas de negocio expresadas en servicios |
| **Forma de iniciar la aplicación** | `python main.py` con uvicorn configurado inline | `python main.py` con configuración externa en `app/config.py` |

---

### Ejercicio 1.2 — Rastreo de una Regla de Negocio: RN1 (Límite de Préstamos)

#### 1. ¿En qué archivo está en v1? ¿En cuántas líneas se implementa?

**v1:** En `proyecto-v1/main.py`, líneas **91-141** (función `crear_prestamo`).

**Análisis:**
- La validación de disponibilidad (RN4) está en líneas **109-114**.
- **Pero RN1 (límite de préstamos) no está implementada** en v1. 
- El código actual solo valida:
  - Existencia del libro y usuario
  - Disponibilidad de copias (`cantidad_disponible`)
  - **Falta:** No hay verificación del tipo de estudiante (pregrado/posgrado) ni del contador de préstamos activos.

**Conclusión:** RN1 está **ausente** en v1. Sería necesario:
1. Iterar sobre `prestamos_db` filtrando por `usuario_id` y estado `activo`
2. Contar préstamos activos
3. Comparar con límite según tipo de estudiante (¡que tampoco está en el modelo!)

---

#### 2. ¿En qué archivo(s) está en v2? ¿Qué capas atraviesa?

**v2:** RN1 se distribuye en **3 archivos y 3 capas:**

| Capa | Archivo | Líneas | Código |
|------|---------|--------|--------|
| **Models (Entidad)** | `app/models/entities.py` | — | Entidad `Estudiante` con campo `tipo: str` ("pregrado" \| "posgrado") |
| **Repository** | `app/repositories/prestamo_repository.py` | — | Método `get_activos_by_estudiante_id(id)` → retorna lista de préstamos activos |
| **Service (Lógica de Negocio)** | `app/services/prestamo_service.py` | **73-78** | Verificación RN1: cuenta préstamos activos y compara con límite según tipo |

**Código en v2 (líneas 73-78 de `prestamo_service.py`):**
```python
# RN1: Verificar límite de préstamos activos
prestamos_activos = self.prestamo_repo.get_activos_by_estudiante_id(estudiante_id)
limite_prestamos = 3 if estudiante.tipo == "pregrado" else 5
if len(prestamos_activos) >= limite_prestamos:
    raise LimitePrestamosAlcanzado()
```

---

#### 3. Si el cliente pide cambiar el límite de pregrado de 3 a 4, ¿cuántos archivos hay que modificar en cada versión?

**v1:**
- **Archivos a modificar:** 0 (porque RN1 no está implementada)
- **Si se implementara:** 1 archivo (`main.py`) + modelo `Usuario` tendría que agregar tipo

**v2:**
- **Archivos a modificar:** 1 archivo (`app/services/prestamo_service.py`, línea 76)
- **Cambio:** `limite_prestamos = 4 if estudiante.tipo == "pregrado" else 5`
- **Ventaja:** Localizado, centralizado, fácil de cambiar sin afectar rutas o persistencia

---

#### 4. ¿Cómo sabrías que el cambio no rompió nada en cada versión?

**v1:**
- **Sin tests:** Hay que hacer pruebas manuales con `curl`:
  ```bash
  # Primero habría que implementar el tipo de usuario/estudiante
  # Luego crear préstamos manualmente
  # Verificar que el préstamo que supera el límite falle
  # Proceso manual, propenso a errores y lento
  ```
- **Tiempo estimado:** 10-15 minutos por cambio
- **Confianza:** Baja (se pueden olvidar casos edge)

**v2:**
- **Con tests:** Ejecutar suite de tests (todos pasan/fallan instantáneamente):
  ```bash
  pytest tests/test_services/test_prestamo_service.py::TestRN1_LimitePrestamos -v
  ```
- **Tests relevantes:**
  - `test_pregrado_puede_crear_3_prestamos` → Falla si cambias el código sin actualizar límite
  - `test_posgrado_puede_crear_5_prestamos` → Verifica que posgrado sigue con límite 5
- **Tiempo estimado:** 2 segundos (ejecución de tests)
- **Confianza:** Muy alta (la suite de tests lo valida automáticamente)

---

## Bloque 2 — Análisis de Calidad y Comportamiento ante Errores

### Ejercicio 2.1 — El Request que No Debería Funcionar

**Aclaración importante sobre los campos:** v1 y v2 no reciben exactamente el mismo JSON.

- En **v1**, el endpoint espera `libro_id`, `usuario_id` y opcionalmente `dias_duracion`.
- En **v2**, el flujo de préstamos trabaja con `estudiante_id` y `ejemplar_id`.

Por eso, si enviamos literalmente este request a **v1**:

```bash
curl -s -X POST http://localhost:8000/prestamos \
  -H "Content-Type: application/json" \
  -d '{"estudianteId": "NO-EXISTE", "ejemplarId": "abc"}' | jq
```

v1 no llega a validar si el usuario existe, porque los nombres de campos no coinciden con su modelo `PrestamoCreate`. Lo esperable es un error de validación de FastAPI/Pydantic, normalmente `422 Unprocessable Entity`, por faltar `libro_id` y `usuario_id`.

Para comparar correctamente el comportamiento por recurso inexistente, hay que usar el contrato de cada versión:

**v1:**
```bash
curl -s -X POST http://localhost:8000/prestamos \
  -H "Content-Type: application/json" \
  -d '{"libro_id": 1, "usuario_id": 999, "dias_duracion": 14}' | jq
```

**v2:**
```bash
curl -s -X POST http://localhost:8000/prestamos \
  -H "Content-Type: application/json" \
  -d '{"estudiante_id": "NO-EXISTE", "ejemplar_id": "EJE001"}' | jq
```

#### 1. ¿Qué código HTTP devuelve cada versión?

| Versión | Caso probado | Código HTTP esperado |
|---------|--------------|----------------------|
| **v1** | Campos incorrectos (`estudianteId`, `ejemplarId`) | 422 Unprocessable Entity |
| **v1** | `usuario_id` inexistente con contrato correcto | 404 Not Found |
| **v2** | `estudiante_id` inexistente con contrato correcto | 404 Not Found |

**Conclusión:** no se deben comparar los dos proyectos con el mismo payload si el contrato de entrada cambió entre versiones.

---

#### 2. ¿Qué información contiene el cuerpo de la respuesta en cada caso?

**v1, con usuario inexistente:**
```json
{
  "detail": "Usuario con ID 999 no encontrado"
}
```

- Usa `HTTPException` directamente desde el endpoint.
- El error queda como texto dentro de `detail`.
- No hay un código de error de dominio como `usuario_no_encontrado`.

**v1, con campos incorrectos:**
```json
{
  "detail": [
    {
      "loc": ["body", "libro_id"],
      "msg": "Field required",
      "type": "missing"
    }
  ]
}
```

Ese formato viene de FastAPI/Pydantic y es más técnico.

**v2, con estudiante inexistente:**
```json
{
  "detail": {
    "error": "recurso_no_encontrado"
  }
}
```

La forma exacta puede variar según cómo la ruta convierta la excepción a `HTTPException`, pero la diferencia importante es que v2 maneja errores de dominio con excepciones propias como `ResourceNotFound`, `LimitePrestamosAlcanzado`, `EjemplarNoDisponible`, etc.

---

#### 3. ¿Cuál respuesta es más útil para un cliente que consume la API?

**v2 es más útil a nivel de diseño porque:**

1. **Distingue errores de validación y errores de negocio:** un JSON mal formado o incompleto no es lo mismo que un estudiante inexistente.
2. **Tiene excepciones de dominio:** el servicio no depende directamente de `HTTPException`; lanza errores propios del sistema de biblioteca.
3. **Permite mapear reglas a códigos HTTP más adecuados:** por ejemplo, un préstamo rechazado por límite o disponibilidad se representa mejor como `409 Conflict`.
4. **Facilita pruebas y mantenimiento:** las reglas se prueban en servicios sin depender de levantar toda la API.

**En v1 sería más frágil:**
```python
# El cliente o el test tendría que depender de textos en detail.
if "Usuario" in error_detail:
    ...
```

---

#### 4. ¿Qué pasa en v1 si llega un identificador con tipo incorrecto? ¿Y en v2?

**v1:**
- El campo real no es `ejemplar_id`, sino `libro_id`.
- `PrestamoCreate` define `libro_id: int` y `usuario_id: int`.
- Si se envía un valor no numérico como `"abc"` para `libro_id`, FastAPI/Pydantic responde con `422 Unprocessable Entity`.

Ejemplo:
```bash
curl -s -X POST http://localhost:8000/prestamos \
  -H "Content-Type: application/json" \
  -d '{"libro_id": "abc", "usuario_id": 1}' | jq
```

Respuesta esperada:
```json
{
  "detail": [
    {
      "loc": ["body", "libro_id"],
      "msg": "Input should be a valid integer",
      "type": "int_parsing"
    }
  ]
}
```

**v2:**
- Trabaja con `ejemplar_id` como identificador de ejemplar.
- Si el formato del request es inválido, responde como error de validación de entrada.
- Si el formato es válido pero el recurso no existe, la capa de servicio lanza una excepción de dominio como `ResourceNotFound`.

**Diferencia clave:** v1 mezcla validaciones técnicas y reglas básicas dentro del endpoint; v2 separa mejor la entrada HTTP de las reglas de negocio.

---

### Ejercicio 2.2 — Comparar Errores de Dominio

**Pasos:**
1. En v1, agotar la disponibilidad de un libro hasta que `cantidad_disponible` llegue a 0.
2. En v2, crear un préstamo con un ejemplar y luego intentar prestar ese mismo ejemplar otra vez.

#### Tabla de Comparación

| Aspecto | v1 | v2 |
|---------|----|----|
| **Código HTTP** | 400 Bad Request | 409 Conflict |
| **Campo `error` en la respuesta** | No hay campo `error`; usa `detail: "No hay copias..."` | Usa un código de dominio como `ejemplar_no_disponible` dentro del detalle de la respuesta |
| **Mensaje legible** | "No hay copias disponibles del libro 'Clean Code'" | "El ejemplar no está disponible para prestar" |
| **Información adicional (detalles)** | Solo el mensaje | Incluye un código de error de dominio que el cliente puede interpretar |
| **¿Expone información interna del servidor?** | Sí (nombre del libro en el error) | No (código de error genérico) |

---

#### Análisis Técnico

**v1 (líneas 110-114 en `main.py`):**
```python
if libro.cantidad_disponible <= 0:
    raise HTTPException(
        status_code=400,  # ❌ Incorrecto: 400 es para validación de formato
        detail=f"No hay copias disponibles del libro '{libro.titulo}'"  # ❌ Expone lógica
    )
```

**Problemas:**
- Usa 400 (Bad Request) cuando debería ser 409 (Conflict/regla de negocio)
- Expone el nombre del libro (información interna)
- No hay código de error máquina-legible

**v2 (líneas 91-93 en `prestamo_service.py`):**
```python
if ejemplar.estado != "disponible":
    raise EjemplarNoDisponible()  # Excepción de dominio custom
```

**En `custom_exceptions.py`:**
```python
class EjemplarNoDisponible(BibliotecaException):
    """El ejemplar no está disponible"""
    def __init__(self):
        self.message = "ejemplar_no_disponible"  # Código máquina-legible
        super().__init__(self.message)
```

**En la capa HTTP de v2 (ruta/controlador):**
```python
except EjemplarNoDisponible:
    raise HTTPException(
        status_code=409,  # ✓ Correcto
        detail={"error": "ejemplar_no_disponible"}
    )
```

**Ventajas:**
- Usa código HTTP correcto (409 Conflict)
- Error máquina-legible para lógica cliente
- No expone detalles de implementación
- Separación: excepciones de dominio vs respuestas HTTP

---

## Bloque 3 — Análisis de los Tests de v2

### Ejercicio 3.1 — Lectura de un Test Unitario

**Archivo:** `proyecto-v2/tests/test_services/test_prestamo_service.py`, líneas 48-99

#### 1. ¿Qué técnica de aislamiento se usa? (mocks, stubs, fakes, spies)

**Técnica:** **Fakes** (no mocks, sino objetos reales)

**Explicación:**
```python
@pytest.fixture
def prestamo_service_with_repos():
    """Fixture que crea repositorios REALES con persistencia en memoria"""
    prestamo_repo = PrestamoRepository()
    ejemplar_repo = EjemplarRepository()
    libro_repo = LibroRepository()
    estudiante_repo = EstudianteRepository()
    multa_repo = MultaRepository()
    
    return PrestamoService(
        prestamo_repository=prestamo_repo,  # ← Instancia REAL
        ejemplar_repository=ejemplar_repo,  # ← Instancia REAL
        ...
    )
```

**Tipo de aislamiento:**
- **No son mocks** (no verificamos llamadas con `assert_called_with`)
- **Son fakes:** Implementaciones reales pero aisladas (persistencia en memoria)
- **Ventaja:** El test prueba el comportamiento real sin dependencias externas
- **Trade-off:** Un poco más lento que mocks puros, pero más confiable

**Alternativa con Mocks sería:**
```python
from unittest.mock import Mock

@pytest.fixture
def prestamo_service_with_mocks():
    prestamo_repo = Mock(spec=PrestamoRepository)
    prestamo_repo.get_activos_by_estudiante_id.return_value = []
    # ... etc
```
Esto sería más rápido pero menos realista.

---

#### 2. ¿Se levanta algún servidor HTTP para ejecutar este test? ¿Por qué importa esto?

**Respuesta:** **No, no se levanta servidor HTTP.**

**Prueba:**
```python
# En test_prestamo_service.py:
from app.services.prestamo_service import PrestamoService  # ← Importa servicio DIRECTO
# No hay: from fastapi.testclient import TestClient
# No hay: client = TestClient(app)
```

**¿Por qué importa?**

| Aspecto | Con servidor HTTP | Sin servidor (test unitario) |
|--------|------------------|------------------------------|
| **Velocidad** | 50-100ms por test | <5ms por test |
| **Cobertura** | Valida toda la cadena HTTP | Valida solo lógica de negocio |
| **Aislamiento** | Prueba rutas, serialización, middleware | Prueba servicio puro |
| **Uso en CI/CD** | Lento en pipeline | Rápido, ejecutable 1000s de tests |

**En v2 se tienen dos tipos de tests:**
1. **Unitarios (Test Service):** Sin servidor → RÁPIDOS (como este)
2. **Integración (Test Routes):** Con `TestClient` → MÁS LENTOS pero validan stack completo

---

#### 3. Identifica en qué línea(s) se prueba RN1 (límite de préstamos) y RN3 (préstamos vencidos)

**RN1:** Líneas **100-150** (`test_posgrado_puede_crear_5_prestamos`)
```python
def test_posgrado_puede_crear_5_prestamos(self, prestamo_service_with_repos):
    # ... setup de 5 ejemplares y estudiante posgrado ...
    
    # Crear 5 préstamos (debe funcionar)
    for i in range(5):
        prestamo = service.crear_prestamo("EST002", f"EJE10{i+1}")
        assert prestamo.estado == "activo"  # ← Verifica RN1: permite 5
    
    # Crear 6to préstamo (debe fallar)
    with pytest.raises(LimitePrestamosAlcanzado):  # ← Verifica RN1: rechaza 6to
        service.crear_prestamo("EST002", "EJE106")
```

**RN3 (Préstamos Vencidos):** 
- Se prueba en la misma suite de servicios, en el grupo dedicado a préstamos vencidos.
- La idea del test es construir un estudiante con al menos un préstamo vencido y verificar que el servicio rechaza un préstamo nuevo.
- **Patrón de la prueba:**
```python
def test_bloquear_si_prestamos_vencidos(self, prestamo_service_with_repos):
    # ... crear estudiante con préstamo vencido ...
    
    with pytest.raises(PrestamosVencidos):
        service.crear_prestamo("EST001", "EJE001")  # ← Rechaza si hay vencidos
```

---

#### 4. ¿Cuánto tiempo tarda en ejecutarse este test?

**Tiempo típico:** **0.02 - 0.05 segundos** (20-50 milisegundos)

**Verificación:**
```bash
cd proyecto-v2
pytest tests/test_services/test_prestamo_service.py::TestRN1_LimitePrestamos::test_posgrado_puede_crear_5_prestamos -v --durations=10
```

**Salida esperada:**
```
test_posgrado_puede_crear_5_prestamos PASSED [100%]

===== 1 passed in 0.05s =====
```

**¿Por qué es tan rápido?**
1. No hay I/O (sin base de datos real)
2. No hay red HTTP (sin TestClient)
3. Operaciones de memoria (diccionarios en Python)
4. Pytest fixture caching (setup reutilizado entre tests)

**Comparación:**
- Test unitario (este): 0.05s
- Test integración con HTTP: 0.5-1.0s
- Test e2e con BD real: 2-5s

---

## Bloque 4 — Escritura de Tests

### Ejercicio 4.1 — Test Unitario: Posgrado con 5 Préstamos

**Descripción:** Escribir un test que verifica que un estudiante de posgrado puede tener **hasta 5 préstamos simultáneos pero falla al intentar el sexto**.

#### Código Completo del Test

```python
# archivo: proyecto-v2/tests/test_services/test_prestamo_service.py
# Agregar a la clase TestRN1_LimitePrestamos

def test_rn1_posgrado_falla_al_sexto_prestamo(self, prestamo_service_with_repos):
    """
    RN1: Un estudiante de posgrado puede prestar hasta 5 libros simultáneamente
    pero debe fallar al intentar el sexto préstamo.
    
    Caso de uso crítico: verificar que el límite está correctamente implementado
    y que la excepción se lanza en el momento exacto.
    """
    service, prestamo_repo, ejemplar_repo, libro_repo, estudiante_repo, multa_repo = (
        prestamo_service_with_repos
    )
    
    # ========== SETUP ==========
    # 1. Crear un libro (con atributos mínimos)
    libro = Libro(
        id="LIB_POSTGRADO_001",
        titulo="Advanced Python Architectures",
        autor="Raymond Hettinger",
        ubicacion="Piso 3 - Sección de Posgrados",
        alta_demanda=False,  # Duración estándar: 15 días
    )
    libro_repo.create(libro, libro.id)
    
    # 2. Crear 6 ejemplares del mismo libro (necesitamos 6 para probar)
    ejemplares_ids = []
    for i in range(1, 7):
        ejemplar = Ejemplar(
            id=f"EJE_POSTGRADO_{i}",
            libro_id=libro.id,
            estado="disponible",
        )
        ejemplar_repo.create(ejemplar, ejemplar.id)
        ejemplares_ids.append(ejemplar.id)
    
    # 3. Crear un estudiante de POSGRADO
    estudiante_posgrado = Estudiante(
        id="EST_POSTGRADO_LIMITS",
        nombre="Dra. María Advanced",
        programa="Maestría en Ingeniería de Software",
        semestre=2,
        tipo="posgrado",  # ← CLAVE: tipo posgrado
        multas_pendientes=0.0,  # Sin deudas
    )
    estudiante_repo.create(estudiante_posgrado, estudiante_posgrado.id)
    
    # ========== PRUEBA: Crear 5 préstamos (DEBE FUNCIONAR) ==========
    prestamos_creados = []
    for i in range(5):
        prestamo = service.crear_prestamo(
            estudiante_id=estudiante_posgrado.id,
            ejemplar_id=ejemplares_ids[i],
            fecha_prestamo=date(2026, 5, 1),  # Fecha consistente
        )
        
        # Validaciones unitarias
        assert prestamo.id is not None, "El préstamo debe tener un ID"
        assert prestamo.estado == "activo", "El préstamo debe estar en estado activo"
        assert prestamo.estudiante_id == estudiante_posgrado.id
        assert prestamo.ejemplar_id == ejemplares_ids[i]
        assert prestamo.fecha_devolucion_esperada == date(2026, 5, 16), \
            "Fecha de devolución debe ser 15 días después (no es alta demanda)"
        
        prestamos_creados.append(prestamo)
        
        # Verificar que los ejemplares se marcan como prestados
        ejemplar_actualizado = ejemplar_repo.get_by_id(ejemplares_ids[i])
        assert ejemplar_actualizado.estado == "prestado", \
            f"El ejemplar debe estar en estado 'prestado' después del préstamo"
    
    # Verificar que el repositorio registró todos los 5 préstamos
    prestamos_activos_en_repo = prestamo_repo.get_activos_by_estudiante_id(
        estudiante_posgrado.id
    )
    assert len(prestamos_activos_en_repo) == 5, \
        f"Debería haber 5 préstamos activos, pero hay {len(prestamos_activos_en_repo)}"
    
    # ========== PRUEBA CRÍTICA: El 6to préstamo DEBE FALLAR ==========
    with pytest.raises(LimitePrestamosAlcanzado) as exc_info:
        service.crear_prestamo(
            estudiante_id=estudiante_posgrado.id,
            ejemplar_id=ejemplares_ids[5],  # El 6to ejemplar
            fecha_prestamo=date(2026, 5, 1),
        )
    
    # Validar que la excepción contiene el mensaje correcto
    assert exc_info.value.message == "limite_prestamos_alcanzado"
    
    # Verificar que el 6to ejemplar sigue siendo disponible (no se asignó)
    ejemplar_6to = ejemplar_repo.get_by_id(ejemplares_ids[5])
    assert ejemplar_6to.estado == "disponible", \
        "El ejemplar no debe estar prestado si el préstamo fue rechazado"
    
    # Verificar que el repositorio SIGUE registrando solo 5 préstamos
    prestamos_finales = prestamo_repo.get_activos_by_estudiante_id(
        estudiante_posgrado.id
    )
    assert len(prestamos_finales) == 5, \
        "El recuento de préstamos no debe aumentar si el 6to es rechazado"
```

---

#### Explicación Línea por Línea

| Sección | Propósito | Líneas |
|---------|-----------|--------|
| **SETUP** | Crear datos de prueba: libro, ejemplares, estudiante | 1-50 |
| **Validación 5 préstamos OK** | Verificar que 5 se crean exitosamente | 52-80 |
| **Validación 6to falla** | Verificar que el 6to lanza `LimitePrestamosAlcanzado` | 82-95 |
| **Validación postcondición** | Verificar que no se modificó estado | 97-107 |

---

#### Propiedades del Test

| Propiedad | Valor |
|-----------|-------|
| **Tipo** | Test unitario (sin HTTP, sin BD real) |
| **Complejidad** | Media (múltiples pasos, varias aserciones) |
| **Cobertura** | RN1 para posgrado + efectos secundarios (ejemplar → prestado) |
| **Duración esperada** | ~30ms |
| **Frágil?** | No (solo valida comportamiento observable) |
| **Reutilizable?** | Sí (es un patrón clásico de límites) |

---

### Ejercicio 4.2 — ¿Por Qué Este Test es Mucho Más Lento/Difícil en v1?

#### Resumen Comparativo

| Aspecto | v1 | v2 |
|---------|----|----|
| **¿Existe la RN1?** | ❌ No (no está implementada) | ✅ Sí (líneas 73-78) |
| **¿Hay framework de tests?** | ❌ No | ✅ Sí (Pytest + fixtures) |
| **¿Hay inyección de dependencias?** | ❌ No | ✅ Sí (DI en service) |
| **¿Hay separación de capas?** | ❌ No (todo en main.py) | ✅ Sí (4 capas) |

---

#### Razón 1: La RN1 Simplemente No Existe en v1

**v1 (`main.py` líneas 91-141):**
```python
def crear_prestamo(prestamo_create: PrestamoCreate):
    # Valida existencia del libro
    # Valida existencia del usuario
    # Valida cantidad disponible (RN4)
    # ❌ NO VALIDA LÍMITE DE PRÉSTAMOS POR TIPO DE ESTUDIANTE
```

**Consecuencia:** No hay **nada que probar**. El test tendría que:
1. Primero, **implementar RN1** en v1
2. Luego, escribir el test

Esto significa que el exercise sería imposible sin antes arreglar v1.

---

#### Razón 2: Imposibilidad de Aislar Lógica (Sin Inyección de Dependencias)

**v1 (Acoplamiento fuerte):**
```python
# main.py
prestamos_db = {}  # Global

def crear_prestamo(prestamo_create: PrestamoCreate):
    # Lectura directa de global prestamos_db
    # No hay forma de mockearla sin manipular module globals
    
    # Para "testear" habría que:
    # 1. Hacer un POST HTTP real
    # 2. Levantar el servidor
    # 3. Hacer varias peticiones
    # 4. Parsear respuestas JSON
```

**Test en v1 sería así (¡horrible!):**
```python
import requests
import time
import subprocess

# Levantar servidor en background
process = subprocess.Popen(["python", "main.py"])
time.sleep(2)  # Esperar a que levante

try:
    # Crear 5 préstamos vía HTTP
    for i in range(5):
        resp = requests.post(
            "http://localhost:8000/prestamos",
            json={"usuario_id": 1, "libro_id": 1, "dias_duracion": 14}
        )
        assert resp.status_code == 201
    
    # Intentar 6to
    resp = requests.post(
        "http://localhost:8000/prestamos",
        json={"usuario_id": 1, "libro_id": 2, "dias_duracion": 14}
    )
    assert resp.status_code == 409  # ← Pero esto fallaría porque RN1 no existe
    
finally:
    process.terminate()  # Matar servidor
    time.sleep(1)

# Problemas de este approach:
# - Toma 3-5 segundos por test (no 30ms)
# - Requiere levantar servidor (flaky, puertos en uso)
# - No puedes usar fixtures reutilizables
# - No hay aislamiento (tests interfieren entre sí si no limpias estado)
```

---

#### Razón 3: Falta de Fixture Reutilizables

**v2:** Fixtures de Pytest (reutilizables, limpias entre tests)
```python
@pytest.fixture
def prestamo_service_with_repos():
    """Setup completo en memoria, aislado para cada test"""
    prestamo_repo = PrestamoRepository()
    # ... crea instancias limpias ...
    return service, prestamo_repo, ...
    # ← Al finalizar el test, se descarta la instancia (estado limpio)

def test_rn1_posgrado_falla_al_sexto(self, prestamo_service_with_repos):
    # Recibe service limpio automáticamente
    ...
```

**v1:** No hay fixtures, hay que limpiar estado manualmente
```python
# v1: Sin framework de tests
# Habría que hacer:
prestamos_db.clear()  # Limpiar estado anterior
usuarios_db.clear()
libros_db.clear()

# Crear datos de prueba a mano
# Hacer requests HTTP
# Parsear respuestas
# Verificar status codes
```

---

#### Razón 4: Overhead de HTTP en Cada Assertion

**v2 (Directo):**
```python
prestamo = service.crear_prestamo("EST001", "EJE001")
assert prestamo.estado == "activo"  # ← Instant access, no serialization
```

**v1 (Vía HTTP):**
```python
response = requests.post("http://localhost:8000/prestamos", json=...)
prestamo_json = response.json()
assert prestamo_json["estado"] == "activo"  # ← HTTP + JSON parsing overhead
```

**Multiplicador de lentitud:**
- v2: 5 créations × 30ms = 150ms total
- v1: 5 créations × (HTTP 100ms + parsing 10ms) = 550ms total
- **v1 es ~3.7x más lento**

---

#### Tabla: Complejidad Relativa

| Paso | v1 | v2 |
|------|----|----|
| Implementar RN1 | Necesario | ✅ Ya existe |
| Levantar servidor | Necesario (lento) | ❌ No necesario |
| Crear fixtures | Manual (tedioso) | ✅ Auto con Pytest |
| Aislar datos | Limpiar globals (riesgoso) | ✅ Instancias aisladas |
| Escribir assertions | Vía JSON response parsing | ✅ Directo en objeto |
| Duración por test | 3-5 segundos | 30-50ms |
| Confiabilidad | Baja (flaky, dependencias) | Alta (determinístico) |

---

## Resumen Ejecutivo

### Hallazgos Principales

1. **Arquitectura:**
   - v1 es monolítica (todo en 1 archivo): difícil de testear y cambiar
   - v2 usa Clean Architecture (4 capas): permite tests unitarios aislados rápidos

2. **Reglas de Negocio:**
   - RN1 (límite de préstamos) **no está implementada en v1**
   - En v2, está claramente ubicada en la capa de Service (líneas 73-78)

3. **Manejo de Errores:**
   - v1: Usa códigos HTTP genéricos e inconsistentes (400 para todo)
   - v2: Códigos HTTP específicos (409 para conflictos de negocio, 400 para validación)

4. **Testing:**
   - v1: Requiere servidor HTTP + limpieza de estado global → **lento** (3-5s/test)
   - v2: Inyección de dependencias + fixtures → **rápido** (30-50ms/test)

5. **Cambios en Reglas de Negocio:**
   - v1: Cambiar límite de 3→4 requeriría implementar RN1 first + buscar N archivos
   - v2: Un archivo, una línea, probado automáticamente en 50ms

---

### Conclusión

La versión v2 demuestra cómo **la arquitectura limpia y los tests no son overhead sino herramientas de productividad**. Aunque v2 tiene más archivos, permite:

✅ **Cambios rápidos** — Lógica centralizada, fácil de modificar  
✅ **Confianza** — Suite de tests ejecutable en segundos  
✅ **Mantenibilidad** — Código legible en capas vs monolito de 300 líneas  
✅ **Escalabilidad** — Agregar nuevas RN's sin afectar rutas ni persistencia  

En contraste, v1 requeriría **mantenimiento manual, testing lento e incierto, y riesgo de regresiones** conforme crece la complejidad.
