# API Gestión de Préstamos - Biblioteca Ucaldas

API REST construida con FastAPI para gestionar préstamos de libros en una biblioteca universitaria.

## Características

- ✅ Listar libros disponibles en la biblioteca
- ✅ Crear préstamos de libros
- ✅ Devolver libros prestados
- ✅ Consultar préstamos vigentes
- ✅ Ver préstamos por usuario
- ✅ Datos almacenados en memoria
- ✅ Documentación interactiva automática (Swagger UI)

## Instalación

1. Crear un entorno virtual (opcional pero recomendado):
```bash
python -m venv venv
venv\Scripts\activate  # En Windows
# o source venv/bin/activate  # En Linux/Mac
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

## Ejecución

```bash
python main.py
```

La API estará disponible en: `http://localhost:8000`

La documentación interactiva (Swagger UI) estará en: `http://localhost:8000/docs`

## Endpoints Disponibles

### 📚 Gestión de Libros

#### GET `/libros`
Lista todos los libros disponibles en la biblioteca.

**Respuesta:**
```json
[
  {
    "id": 1,
    "titulo": "Clean Code",
    "autor": "Robert C. Martin",
    "isbn": "978-0132350884",
    "cantidad_disponible": 3,
    "cantidad_total": 5
  },
  ...
]
```

#### GET `/libros/{libro_id}`
Obtiene los detalles de un libro específico.

**Parámetros:**
- `libro_id` (int): ID del libro

### 📖 Gestión de Préstamos

#### POST `/prestamos`
Crea un nuevo préstamo de un libro.

**Body:**
```json
{
  "libro_id": 1,
  "usuario_id": 1,
  "dias_duracion": 14
}
```

**Respuesta (201 Created):**
```json
{
  "id": 1,
  "libro_id": 1,
  "usuario_id": 1,
  "fecha_prestamo": "2026-05-12T10:30:00",
  "fecha_vencimiento": "2026-05-26T10:30:00",
  "fecha_devolucion": null,
  "estado": "activo",
  "libro_titulo": "Clean Code",
  "usuario_nombre": "Juan Pérez"
}
```

#### POST `/prestamos/{prestamo_id}/devolver`
Registra la devolución de un libro.

**Parámetros:**
- `prestamo_id` (int): ID del préstamo

**Respuesta:**
```json
{
  "id": 1,
  "libro_id": 1,
  "usuario_id": 1,
  "fecha_prestamo": "2026-05-12T10:30:00",
  "fecha_vencimiento": "2026-05-26T10:30:00",
  "fecha_devolucion": "2026-05-20T15:45:00",
  "estado": "devuelto",
  "libro_titulo": "Clean Code",
  "usuario_nombre": "Juan Pérez"
}
```

#### GET `/prestamos/vigentes`
Lista todos los préstamos vigentes (activos, no devueltos).

**Respuesta:**
```json
[
  {
    "id": 1,
    "libro_id": 1,
    "usuario_id": 1,
    "fecha_prestamo": "2026-05-12T10:30:00",
    "fecha_vencimiento": "2026-05-26T10:30:00",
    "fecha_devolucion": null,
    "estado": "activo",
    "libro_titulo": "Clean Code",
    "usuario_nombre": "Juan Pérez"
  },
  ...
]
```

#### GET `/usuarios/{usuario_id}/prestamos`
Lista los préstamos de un usuario específico.

**Parámetros:**
- `usuario_id` (int): ID del usuario
- `solo_vigentes` (bool, optional): Si es True solo muestra préstamos activos (default: True)

**Respuesta:**
```json
[
  {
    "id": 1,
    "libro_id": 1,
    "usuario_id": 1,
    "fecha_prestamo": "2026-05-12T10:30:00",
    "fecha_vencimiento": "2026-05-26T10:30:00",
    "fecha_devolucion": null,
    "estado": "activo",
    "libro_titulo": "Clean Code",
    "usuario_nombre": "Juan Pérez"
  }
]
```

### ℹ️ Información

#### GET `/`
Información general de la API.

#### GET `/health`
Health check de la API.

**Respuesta:**
```json
{
  "status": "ok",
  "timestamp": "2026-05-12T10:30:00",
  "libros_totales": 5,
  "usuarios_totales": 3,
  "prestamos_totales": 2
}
```

## Base de Datos en Memoria

### Libros Precargados
1. Clean Code - Robert C. Martin
2. The Pragmatic Programmer - Andrew Hunt
3. Design Patterns - Gang of Four
4. Python Fluent - Luciano Ramalho
5. Refactoring - Martin Fowler

### Usuarios Precargados
1. Juan Pérez (2021-001)
2. María García (2021-002)
3. Carlos López (2022-001)

## Ejemplos de Uso con cURL

### Listar libros
```bash
curl http://localhost:8000/libros
```

### Crear un préstamo
```bash
curl -X POST http://localhost:8000/prestamos \
  -H "Content-Type: application/json" \
  -d '{
    "libro_id": 1,
    "usuario_id": 1,
    "dias_duracion": 14
  }'
```

### Devolver un libro
```bash
curl -X POST http://localhost:8000/prestamos/1/devolver
```

### Listar préstamos vigentes
```bash
curl http://localhost:8000/prestamos/vigentes
```

### Ver préstamos de un usuario
```bash
curl http://localhost:8000/usuarios/1/prestamos
```

### Health check
```bash
curl http://localhost:8000/health
```

## Códigos de Estado HTTP

- `200 OK`: Solicitud exitosa
- `201 Created`: Recurso creado exitosamente
- `400 Bad Request`: Error en la solicitud (ej: libro no disponible)
- `404 Not Found`: Recurso no encontrado
- `500 Internal Server Error`: Error del servidor

## Estructura del Proyecto

```
proyecto-v1/
├── main.py              # Aplicación FastAPI principal
├── requirements.txt     # Dependencias del proyecto
└── README.md           # Este archivo
```

## Notas

- La API usa almacenamiento en memoria, por lo que los datos se perderán al reiniciar el servidor
- Los préstamos tienen una duración configurable (por defecto 14 días)
- La API incluye validaciones para:
  - Verificar existencia de libros y usuarios
  - Validar disponibilidad de copias
  - Evitar devolver libros ya devueltos

## Desarrollo Futuro

- [ ] Persistencia en base de datos (SQLite, PostgreSQL)
- [ ] Autenticación y autorización
- [ ] Multas por retrasos en devoluciones
- [ ] Reservas de libros
- [ ] Notificaciones de vencimiento
- [ ] Reportes y estadísticas
- [ ] Tests automatizados
