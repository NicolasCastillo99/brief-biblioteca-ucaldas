# 🚀 Quick Start - Sistema de Préstamo de Libros

## Prerequisitos

- Python 3.10+
- pip

## Instalación Rápida

```bash
# 1. Crear entorno virtual
python -m venv venv

# 2. Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt
```

## Ejecutar la Aplicación

```bash
# Opción 1: Con Python directo
python main.py

# Opción 2: Con Uvicorn
uvicorn main:app --reload --port 8000
```

La API estará disponible en: **http://localhost:8000**

### Documentación Interactiva

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Cargar Datos de Prueba

En una terminal diferente (con el entorno virtual activado):

```bash
python seed_data.py
```

Esto cargará:
- 5 libros
- 15 ejemplares
- 5 estudiantes
- 3 préstamos de prueba

## Ejemplos de Uso

### 1. Listar libros disponibles

```bash
curl http://localhost:8000/libros/disponibles
```

### 2. Crear un estudiante

```bash
curl -X POST http://localhost:8000/estudiantes \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Pedro González",
    "programa": "Ingeniería Civil",
    "semestre": 4,
    "tipo": "pregrado"
  }'
```

### 3. Crear un préstamo

```bash
curl -X POST http://localhost:8000/prestamos \
  -H "Content-Type: application/json" \
  -d '{
    "estudiante_id": "STUDENT_ID_HERE",
    "ejemplar_id": "EXEMPLAR_ID_HERE"
  }'
```

### 4. Devolver un libro

```bash
curl -X POST http://localhost:8000/prestamos/PRESTAMO_ID_HERE/devolver \
  -H "Content-Type: application/json" \
  -d '{
    "fecha_devolucion_real": "2026-05-20"
  }'
```

### 5. Renovar un préstamo

```bash
curl -X POST http://localhost:8000/prestamos/PRESTAMO_ID_HERE/renovar
```

### 6. Obtener préstamos activos de un estudiante

```bash
curl http://localhost:8000/estudiantes/STUDENT_ID_HERE/prestamos
```

### 7. Obtener historial completo de un estudiante

```bash
curl http://localhost:8000/estudiantes/STUDENT_ID_HERE/historial
```

## Ejecutar Tests

```bash
# Todos los tests
pytest -v

# Con cobertura
pytest --cov=app tests/

# Tests específicos
pytest tests/test_services/test_prestamo_service.py -v

# Solo tests de un módulo
pytest tests/test_models/ -v
```

## Estructura de Carpetas

```
proyecto-v2/
├── app/
│   ├── models/              # Entidades de datos
│   ├── repositories/        # Acceso a datos (en memoria)
│   ├── services/            # Lógica de negocio
│   ├── routes/              # Endpoints REST
│   ├── exceptions/          # Excepciones personalizadas
│   └── config.py            # Configuración
├── tests/                   # Tests (unitarios e integración)
├── docs/                    # Documentación
├── main.py                  # Punto de entrada
├── seed_data.py             # Poblar datos de prueba
├── requirements.txt         # Dependencias
└── README.md                # Documentación completa
```

## Archivos Importantes

| Archivo | Propósito |
|---------|-----------|
| `main.py` | Crea la aplicación FastAPI |
| `seed_data.py` | Carga datos de prueba |
| `README.md` | Documentación completa |
| `docs/ARQUITECTURA.md` | Decisiones arquitectónicas |

## Códigos de Respuesta HTTP

| Código | Significado | Cuándo |
|--------|-------------|--------|
| 200 | OK | GET/POST exitosos |
| 201 | Created | POST que crea recursos |
| 400 | Bad Request | Datos inválidos |
| 404 | Not Found | Recurso no existe |
| 409 | Conflict | Regla de negocio violada |

## Troubleshooting

### Error: "ModuleNotFoundError: No module named 'fastapi'"

Solución:
```bash
pip install -r requirements.txt
```

### Error: "Address already in use"

Solución:
```bash
# Usar otro puerto
uvicorn main:app --port 8001
```

### Error en tests

```bash
# Reinstalar paquetes de test
pip install pytest pytest-asyncio
# Luego ejecutar
pytest
```

## Logs y Debugging

Para ver logs más detallados:

```bash
# Con debug activado
DEBUG=True python main.py
```

## Próximos Pasos

1. Leer `docs/ARQUITECTURA.md` para entender la estructura
2. Explorar los endpoints en Swagger UI (http://localhost:8000/docs)
3. Ejecutar los tests: `pytest -v`
4. Revisar la especificación: `02-tu-trabajo/plantilla-especificacion.md`

## Soporte

Para preguntas o issues, revisar:
- README.md (documentación completa)
- docs/ARQUITECTURA.md (decisiones de arquitectura)
- tests/ (ejemplos de uso)

---

**¡Happy Testing! 🎉**
