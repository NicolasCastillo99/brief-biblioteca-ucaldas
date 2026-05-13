# Sistema de Préstamo de Libros - API REST

## Descripción

API REST para gestión de préstamos de libros en una biblioteca universitaria. Permite consultar catálogos, solicitar préstamos, registrar devoluciones, renovar préstamos y gestionar multas automáticas.

## Stack Tecnológico

- **Lenguaje:** Python 3.10+
- **Framework:** FastAPI 0.104.1
- **Servidor:** Uvicorn
- **Testing:** Pytest
- **Persistencia:** En memoria (estructuras de Python)

## Requisitos

- Python 3.10 o superior
- pip

## Instalación

1. Clonar o descargar el proyecto
2. Crear un entorno virtual:
   ```bash
   python -m venv venv
   ```
3. Activar el entorno virtual:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`
4. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

## Ejecución

```bash
python main.py
```

El servidor estará disponible en `http://localhost:8000`

### Documentación interactiva

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Estructura del Proyecto

```
proyecto-v2/
├── app/
│   ├── models/
│   │   └── entities.py           # Modelos de datos
│   ├── repositories/
│   │   ├── base.py               # Repositorio base
│   │   ├── libro_repository.py
│   │   ├── ejemplar_repository.py
│   │   ├── estudiante_repository.py
│   │   ├── prestamo_repository.py
│   │   └── multa_repository.py
│   ├── services/
│   │   ├── libro_service.py
│   │   ├── prestamo_service.py
│   │   └── estudiante_service.py
│   ├── routes/
│   │   ├── libros.py
│   │   ├── prestamos.py
│   │   └── estudiantes.py
│   ├── exceptions/
│   │   └── custom_exceptions.py
│   └── config.py
├── tests/
│   ├── test_models/
│   ├── test_services/
│   ├── test_routes/
│   └── conftest.py
├── main.py
├── requirements.txt
└── README.md
```

## Endpoints

### Libros

- `GET /libros` - Listar catálogo
- `GET /libros/:id` - Detalle de un libro
- `GET /libros/disponibles` - Listar libros con ejemplares disponibles

### Préstamos

- `POST /prestamos` - Crear préstamo
- `POST /prestamos/:id/devolver` - Registrar devolución
- `POST /prestamos/:id/renovar` - Renovar préstamo
- `GET /prestamos/vencidos` - Listar préstamos vencidos

### Estudiantes

- `GET /estudiantes/:id/prestamos` - Préstamos activos de un estudiante
- `GET /estudiantes/:id/historial` - Historial completo de préstamos

## Reglas de Negocio

1. **RN1:** Límite de préstamos (3 para pregrado, 5 para posgrado)
2. **RN2:** Bloqueo por multas pendientes
3. **RN3:** Bloqueo por préstamos vencidos
4. **RN4:** Validación de disponibilidad de ejemplar
5. **RN5:** Duración del préstamo según demanda (3 o 15 días)
6. **RN6:** Renovación de préstamo con validaciones
7. **RN7:** Cambio de estado de ejemplar a "prestado"
8. **RN8:** Cálculo automático de multas (2000 por día de retraso)
9. **RN9:** Historial de préstamos

## Testing

Ejecutar tests:
```bash
pytest
```

Con cobertura:
```bash
pytest --cov=app tests/
```

## Ejemplos de Uso

### Crear un préstamo

```bash
curl -X POST "http://localhost:8000/prestamos" \
  -H "Content-Type: application/json" \
  -d '{
    "estudiante_id": "EST001",
    "ejemplar_id": "EJE001"
  }'
```

### Devolver un libro

```bash
curl -X POST "http://localhost:8000/prestamos/PRES001/devolver" \
  -H "Content-Type: application/json" \
  -d '{
    "fecha_devolucion_real": "2026-05-20"
  }'
```

### Obtener préstamos activos

```bash
curl "http://localhost:8000/estudiantes/EST001/prestamos"
```

## Notas de Implementación

- Todos los datos se almacenan en memoria (se pierden al reiniciar)
- Los identificadores (IDs) se generan automáticamente
- Las fechas se manejan en formato ISO (YYYY-MM-DD)
- El cálculo de multas usa días calendario
