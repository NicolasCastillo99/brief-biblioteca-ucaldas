from datetime import datetime, timedelta
from enum import Enum
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

import database


app = FastAPI(
    title="API Gestion de Prestamos - Biblioteca Ucaldas",
    description="API REST para gestionar prestamos de libros en una biblioteca universitaria",
    version="1.0.0",
)


@app.on_event("startup")
def startup_event() -> None:
    database.seed_if_empty()


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


database.seed_if_empty()


# ==================== ENDPOINTS: LIBROS ====================
@app.get("/libros", response_model=List[LibroResponse], tags=["Libros"])
def listar_libros():
    """
    Obtiene la lista de todos los libros disponibles en la biblioteca.
    """
    return [LibroResponse(**libro) for libro in database.listar_libros()]


@app.get("/libros/{libro_id}", response_model=LibroResponse, tags=["Libros"])
def obtener_libro(libro_id: int):
    """
    Obtiene los detalles de un libro especifico por su ID.
    """
    libro = database.obtener_libro(libro_id)
    if libro is None:
        raise HTTPException(status_code=404, detail=f"Libro con ID {libro_id} no encontrado")
    return LibroResponse(**libro)


# ==================== ENDPOINTS: PRESTAMOS ====================
@app.post("/prestamos", response_model=PrestamoResponse, tags=["Prestamos"], status_code=201)
def crear_prestamo(prestamo_create: PrestamoCreate):
    """
    Crea un nuevo prestamo de un libro para un usuario.
    """
    libro = database.obtener_libro(prestamo_create.libro_id)
    if libro is None:
        raise HTTPException(
            status_code=404,
            detail=f"Libro con ID {prestamo_create.libro_id} no encontrado",
        )

    usuario = database.obtener_usuario(prestamo_create.usuario_id)
    if usuario is None:
        raise HTTPException(
            status_code=404,
            detail=f"Usuario con ID {prestamo_create.usuario_id} no encontrado",
        )

    if libro["cantidad_disponible"] <= 0:
        raise HTTPException(
            status_code=400,
            detail=f"No hay copias disponibles del libro '{libro['titulo']}'",
        )

    fecha_prestamo = datetime.now()
    fecha_vencimiento = fecha_prestamo + timedelta(days=prestamo_create.dias_duracion)

    nuevo_prestamo = database.crear_prestamo(
        libro_id=prestamo_create.libro_id,
        usuario_id=prestamo_create.usuario_id,
        fecha_prestamo=fecha_prestamo.isoformat(),
        fecha_vencimiento=fecha_vencimiento.isoformat(),
        estado=EstadoPrestamo.activo.value,
    )

    return PrestamoResponse(**nuevo_prestamo)


@app.post("/prestamos/{prestamo_id}/devolver", response_model=PrestamoResponse, tags=["Prestamos"])
def devolver_libro(prestamo_id: int):
    """
    Registra la devolucion de un libro previamente prestado.
    """
    try:
        prestamo = database.devolver_prestamo(
            prestamo_id=prestamo_id,
            fecha_devolucion=datetime.now().isoformat(),
        )
    except ValueError as error:
        if str(error) == "prestamo_ya_devuelto":
            raise HTTPException(status_code=400, detail="Este libro ya ha sido devuelto")
        raise HTTPException(status_code=404, detail=f"Prestamo con ID {prestamo_id} no encontrado")

    return PrestamoResponse(**prestamo)


@app.get("/prestamos/vigentes", response_model=List[PrestamoResponse], tags=["Prestamos"])
def listar_prestamos_vigentes():
    """
    Lista todos los prestamos vigentes (no devueltos) de la biblioteca.
    """
    return [PrestamoResponse(**prestamo) for prestamo in database.listar_prestamos_vigentes()]


@app.get("/usuarios/{usuario_id}/prestamos", response_model=List[PrestamoResponse], tags=["Prestamos"])
def listar_prestamos_usuario(usuario_id: int, solo_vigentes: bool = True):
    """
    Lista los prestamos de un usuario especifico.

    Parametros:
    - solo_vigentes: Si es True, solo muestra prestamos activos (default: True)
    """
    usuario = database.obtener_usuario(usuario_id)
    if usuario is None:
        raise HTTPException(status_code=404, detail=f"Usuario con ID {usuario_id} no encontrado")

    prestamos = database.listar_prestamos_usuario(usuario_id, solo_vigentes=solo_vigentes)
    return [PrestamoResponse(**prestamo) for prestamo in prestamos]


# ==================== ENDPOINT: INFORMACION ====================
@app.get("/", tags=["Info"])
def root():
    """
    Endpoint raiz con informacion de la API.
    """
    return {
        "nombre": "API Gestion de Prestamos - Biblioteca Ucaldas",
        "version": "1.0.0",
        "documentacion": "/docs",
        "endpoints": {
            "libros": "/libros",
            "crear_prestamo": "POST /prestamos",
            "devolver_libro": "POST /prestamos/{id}/devolver",
            "prestamos_vigentes": "/prestamos/vigentes",
        },
    }


# ==================== ENDPOINT: HEALTH CHECK ====================
@app.get("/health", tags=["Info"])
def health_check():
    """
    Verifica que la API este funcionando correctamente.
    """
    counts = database.contar_registros()
    return {
        "status": "ok",
        "timestamp": datetime.now(),
        **counts,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
