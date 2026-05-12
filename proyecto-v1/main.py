from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
from enum import Enum

app = FastAPI(
    title="API Gestión de Préstamos - Biblioteca Ucaldas",
    description="API REST para gestionar préstamos de libros en una biblioteca universitaria",
    version="1.0.0"
)

# ==================== ENUMS ====================
class EstadoPrestamo(str, Enum):
    activo = "activo"
    devuelto = "devuelto"
    vencido = "vencido"

# ==================== MODELOS ====================
class Libro(BaseModel):
    id: int
    titulo: str
    autor: str
    isbn: str
    cantidad_disponible: int
    cantidad_total: int

class LibroResponse(Libro):
    pass

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

# ==================== BASE DE DATOS EN MEMORIA ====================
libros_db = {
    1: Libro(id=1, titulo="Clean Code", autor="Robert C. Martin", isbn="978-0132350884", cantidad_disponible=3, cantidad_total=5),
    2: Libro(id=2, titulo="The Pragmatic Programmer", autor="Andrew Hunt", isbn="978-0201616224", cantidad_disponible=2, cantidad_total=3),
    3: Libro(id=3, titulo="Design Patterns", autor="Gang of Four", isbn="978-0201633610", cantidad_disponible=1, cantidad_total=2),
    4: Libro(id=4, titulo="Python Fluent", autor="Luciano Ramalho", isbn="978-1491946237", cantidad_disponible=4, cantidad_total=4),
    5: Libro(id=5, titulo="Refactoring", autor="Martin Fowler", isbn="978-0201485677", cantidad_disponible=0, cantidad_total=2),
}

usuarios_db = {
    1: Usuario(id=1, nombre="Juan Pérez", email="juan.perez@ucaldas.edu.co", carnet="2021-001"),
    2: Usuario(id=2, nombre="María García", email="maria.garcia@ucaldas.edu.co", carnet="2021-002"),
    3: Usuario(id=3, nombre="Carlos López", email="carlos.lopez@ucaldas.edu.co", carnet="2022-001"),
}

prestamos_db = {}
prestamo_counter = 1

# ==================== ENDPOINTS: LIBROS ====================
@app.get("/libros", response_model=List[LibroResponse], tags=["Libros"])
def listar_libros():
    """
    Obtiene la lista de todos los libros disponibles en la biblioteca.
    """
    return list(libros_db.values())

@app.get("/libros/{libro_id}", response_model=LibroResponse, tags=["Libros"])
def obtener_libro(libro_id: int):
    """
    Obtiene los detalles de un libro específico por su ID.
    """
    if libro_id not in libros_db:
        raise HTTPException(status_code=404, detail=f"Libro con ID {libro_id} no encontrado")
    return libros_db[libro_id]

# ==================== ENDPOINTS: PRÉSTAMOS ====================
@app.post("/prestamos", response_model=PrestamoResponse, tags=["Préstamos"], status_code=201)
def crear_prestamo(prestamo_create: PrestamoCreate):
    """
    Crea un nuevo préstamo de un libro para un usuario.
    """
    global prestamo_counter
    
    # Validar que el libro existe
    if prestamo_create.libro_id not in libros_db:
        raise HTTPException(status_code=404, detail=f"Libro con ID {prestamo_create.libro_id} no encontrado")
    
    # Validar que el usuario existe
    if prestamo_create.usuario_id not in usuarios_db:
        raise HTTPException(status_code=404, detail=f"Usuario con ID {prestamo_create.usuario_id} no encontrado")
    
    libro = libros_db[prestamo_create.libro_id]
    usuario = usuarios_db[prestamo_create.usuario_id]
    
    # Validar disponibilidad
    if libro.cantidad_disponible <= 0:
        raise HTTPException(
            status_code=400, 
            detail=f"No hay copias disponibles del libro '{libro.titulo}'"
        )
    
    # Crear préstamo
    fecha_prestamo = datetime.now()
    fecha_vencimiento = fecha_prestamo + timedelta(days=prestamo_create.dias_duracion)
    
    nuevo_prestamo = Prestamo(
        id=prestamo_counter,
        libro_id=prestamo_create.libro_id,
        usuario_id=prestamo_create.usuario_id,
        fecha_prestamo=fecha_prestamo,
        fecha_vencimiento=fecha_vencimiento,
        fecha_devolucion=None,
        estado=EstadoPrestamo.activo
    )
    
    prestamos_db[prestamo_counter] = nuevo_prestamo
    prestamo_counter += 1
    
    # Reducir cantidad disponible
    libro.cantidad_disponible -= 1
    
    return PrestamoResponse(
        **nuevo_prestamo.dict(),
        libro_titulo=libro.titulo,
        usuario_nombre=usuario.nombre
    )

@app.post("/prestamos/{prestamo_id}/devolver", response_model=PrestamoResponse, tags=["Préstamos"])
def devolver_libro(prestamo_id: int):
    """
    Registra la devolución de un libro previamente prestado.
    """
    if prestamo_id not in prestamos_db:
        raise HTTPException(status_code=404, detail=f"Préstamo con ID {prestamo_id} no encontrado")
    
    prestamo = prestamos_db[prestamo_id]
    
    # Validar que no esté ya devuelto
    if prestamo.estado == EstadoPrestamo.devuelto:
        raise HTTPException(status_code=400, detail="Este libro ya ha sido devuelto")
    
    # Registrar devolución
    prestamo.fecha_devolucion = datetime.now()
    prestamo.estado = EstadoPrestamo.devuelto
    
    # Aumentar cantidad disponible
    libros_db[prestamo.libro_id].cantidad_disponible += 1
    
    libro = libros_db[prestamo.libro_id]
    usuario = usuarios_db[prestamo.usuario_id]
    
    return PrestamoResponse(
        **prestamo.dict(),
        libro_titulo=libro.titulo,
        usuario_nombre=usuario.nombre
    )

@app.get("/prestamos/vigentes", response_model=List[PrestamoResponse], tags=["Préstamos"])
def listar_prestamos_vigentes():
    """
    Lista todos los préstamos vigentes (no devueltos) de la biblioteca.
    """
    vigentes = [
        p for p in prestamos_db.values() 
        if p.estado == EstadoPrestamo.activo
    ]
    
    respuestas = []
    for prestamo in vigentes:
        libro = libros_db[prestamo.libro_id]
        usuario = usuarios_db[prestamo.usuario_id]
        respuestas.append(PrestamoResponse(
            **prestamo.dict(),
            libro_titulo=libro.titulo,
            usuario_nombre=usuario.nombre
        ))
    
    return respuestas

@app.get("/usuarios/{usuario_id}/prestamos", response_model=List[PrestamoResponse], tags=["Préstamos"])
def listar_prestamos_usuario(usuario_id: int, solo_vigentes: bool = True):
    """
    Lista los préstamos de un usuario específico.
    
    Parámetros:
    - solo_vigentes: Si es True, solo muestra préstamos activos (default: True)
    """
    if usuario_id not in usuarios_db:
        raise HTTPException(status_code=404, detail=f"Usuario con ID {usuario_id} no encontrado")
    
    usuario = usuarios_db[usuario_id]
    
    if solo_vigentes:
        prestamos = [
            p for p in prestamos_db.values() 
            if p.usuario_id == usuario_id and p.estado == EstadoPrestamo.activo
        ]
    else:
        prestamos = [p for p in prestamos_db.values() if p.usuario_id == usuario_id]
    
    respuestas = []
    for prestamo in prestamos:
        libro = libros_db[prestamo.libro_id]
        respuestas.append(PrestamoResponse(
            **prestamo.dict(),
            libro_titulo=libro.titulo,
            usuario_nombre=usuario.nombre
        ))
    
    return respuestas

# ==================== ENDPOINT: INFORMACIÓN ====================
@app.get("/", tags=["Info"])
def root():
    """
    Endpoint raíz con información de la API.
    """
    return {
        "nombre": "API Gestión de Préstamos - Biblioteca Ucaldas",
        "version": "1.0.0",
        "documentacion": "/docs",
        "endpoints": {
            "libros": "/libros",
            "crear_prestamo": "POST /prestamos",
            "devolver_libro": "POST /prestamos/{id}/devolver",
            "prestamos_vigentes": "/prestamos/vigentes"
        }
    }

# ==================== ENDPOINT: HEALTH CHECK ====================
@app.get("/health", tags=["Info"])
def health_check():
    """
    Verifica que la API esté funcionando correctamente.
    """
    return {
        "status": "ok",
        "timestamp": datetime.now(),
        "libros_totales": len(libros_db),
        "usuarios_totales": len(usuarios_db),
        "prestamos_totales": len(prestamos_db)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
