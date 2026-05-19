from datetime import datetime, timedelta
from enum import Enum
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictInt, StrictStr

import database


app = FastAPI(
    title="API Gestion de Prestamos - Biblioteca Ucaldas",
    description="API REST para gestionar prestamos de libros en una biblioteca universitaria",
    version="1.0.0",
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={
            "error": "bad_request",
            "mensaje": "Datos de entrada invalidos",
            "detalles": exc.errors(),
        },
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


class EstudianteCreate(BaseModel):
    model_config = ConfigDict(strict=True)

    id: StrictStr
    nombre: StrictStr
    programa: StrictStr
    semestre: StrictInt
    tipo: StrictStr


class ApiLibroCreate(BaseModel):
    model_config = ConfigDict(strict=True, populate_by_name=True)

    id: StrictStr
    titulo: StrictStr
    autor: StrictStr
    sala: StrictStr
    alta_demanda: StrictBool = Field(alias="altaDemanda")


class EjemplarCreate(BaseModel):
    model_config = ConfigDict(strict=True)

    id: StrictStr


class ApiPrestamoCreate(BaseModel):
    model_config = ConfigDict(strict=True, populate_by_name=True)

    estudiante_id: StrictStr = Field(alias="estudianteId")
    ejemplar_id: StrictStr = Field(alias="ejemplarId")
    fecha_prestamo: Optional[StrictStr] = Field(default=None, alias="fechaPrestamo")


class ReservaCreate(BaseModel):
    model_config = ConfigDict(strict=True, populate_by_name=True)

    estudiante_id: StrictStr = Field(alias="estudianteId")


database.seed_if_empty()


def raise_api_error(error: ValueError) -> None:
    code = str(error)
    if code in {
        "estudiante_no_encontrado",
        "libro_no_encontrado",
        "ejemplar_no_encontrado",
        "prestamo_no_encontrado",
    }:
        raise HTTPException(status_code=404, detail=code)
    if code in {
        "estudiante_duplicado",
        "libro_duplicado",
        "ejemplar_duplicado",
        "limite_prestamos",
        "prestamo_vencido",
        "multa_pendiente",
        "ejemplar_no_disponible",
        "prestamo_ya_devuelto",
        "prestamo_no_renovable",
        "lista_espera",
    }:
        raise HTTPException(status_code=409, detail=code)
    raise HTTPException(status_code=400, detail=code)


# ==================== ENDPOINTS API: ESTUDIANTES ====================
@app.post("/api/estudiantes", tags=["API Estudiantes"], status_code=201)
def crear_estudiante(estudiante: EstudianteCreate):
    if estudiante.tipo not in {"pregrado", "posgrado"}:
        raise HTTPException(status_code=400, detail="tipo debe ser pregrado o posgrado")
    if estudiante.semestre <= 0:
        raise HTTPException(status_code=400, detail="semestre debe ser mayor a cero")
    try:
        return database.crear_estudiante(estudiante.model_dump())
    except ValueError as error:
        raise_api_error(error)


@app.get("/api/estudiantes/{estudiante_id}", tags=["API Estudiantes"])
def obtener_estudiante_api(estudiante_id: str):
    estudiante = database.obtener_estudiante(estudiante_id)
    if estudiante is None:
        raise HTTPException(status_code=404, detail="estudiante_no_encontrado")
    return estudiante


@app.get("/api/estudiantes/{estudiante_id}/historial", tags=["API Estudiantes"])
def historial_estudiante_api(estudiante_id: str):
    try:
        return database.listar_historial_estudiante(estudiante_id)
    except ValueError as error:
        raise_api_error(error)


# ==================== ENDPOINTS API: LIBROS Y EJEMPLARES ====================
@app.post("/api/libros", tags=["API Libros"], status_code=201)
def crear_libro_api(libro: ApiLibroCreate):
    try:
        return database.crear_api_libro(libro.model_dump())
    except ValueError as error:
        raise_api_error(error)


@app.get("/api/libros", tags=["API Libros"])
def listar_libros_api():
    return database.listar_api_libros()


@app.get("/api/libros/{libro_id}", tags=["API Libros"])
def obtener_libro_api(libro_id: str):
    libro = database.obtener_api_libro(libro_id)
    if libro is None:
        raise HTTPException(status_code=404, detail="libro_no_encontrado")
    return libro


@app.post("/api/libros/{libro_id}/ejemplares", tags=["API Ejemplares"], status_code=201)
def crear_ejemplar_api(libro_id: str, ejemplar: EjemplarCreate):
    try:
        return database.crear_ejemplar(libro_id, ejemplar.id)
    except ValueError as error:
        raise_api_error(error)


@app.get("/api/libros/{libro_id}/ejemplares", tags=["API Ejemplares"])
def listar_ejemplares_api(libro_id: str):
    try:
        return database.listar_ejemplares_libro(libro_id)
    except ValueError as error:
        raise_api_error(error)


@app.get("/api/ejemplares/{ejemplar_id}", tags=["API Ejemplares"])
def obtener_ejemplar_api(ejemplar_id: str):
    ejemplar = database.obtener_ejemplar(ejemplar_id)
    if ejemplar is None:
        raise HTTPException(status_code=404, detail="ejemplar_no_encontrado")
    return ejemplar


# ==================== ENDPOINTS API: PRESTAMOS ====================
@app.post("/api/prestamos", tags=["API Prestamos"], status_code=201)
def crear_prestamo_api(prestamo: ApiPrestamoCreate):
    try:
        return database.crear_api_prestamo(
            estudiante_id=prestamo.estudiante_id,
            ejemplar_id=prestamo.ejemplar_id,
            fecha_prestamo=prestamo.fecha_prestamo,
        )
    except ValueError as error:
        raise_api_error(error)


@app.put("/api/prestamos/{prestamo_id}/devolucion", tags=["API Prestamos"])
def devolver_prestamo_api(prestamo_id: int):
    try:
        return database.devolver_api_prestamo(prestamo_id)
    except ValueError as error:
        raise_api_error(error)


@app.put("/api/prestamos/{prestamo_id}/renovar", tags=["API Prestamos"])
def renovar_prestamo_api(prestamo_id: int):
    try:
        return database.renovar_prestamo(prestamo_id)
    except ValueError as error:
        raise_api_error(error)


# ==================== ENDPOINTS API: RESERVAS ====================
@app.post("/api/libros/{libro_id}/reservas", tags=["API Reservas"], status_code=201)
def crear_reserva_api(libro_id: str, reserva: ReservaCreate):
    try:
        return database.crear_reserva(libro_id, reserva.estudiante_id)
    except ValueError as error:
        raise_api_error(error)


@app.get("/api/libros/{libro_id}/reservas", tags=["API Reservas"])
def listar_reservas_api(libro_id: str):
    try:
        return database.listar_reservas_libro(libro_id)
    except ValueError as error:
        raise_api_error(error)


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
    api_counts = database.contar_api_registros()
    return {
        "status": "ok",
        "timestamp": datetime.now(),
        **counts,
        **api_counts,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
