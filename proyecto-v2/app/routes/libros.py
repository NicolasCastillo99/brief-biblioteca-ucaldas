from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.services.libro_service import LibroService
from app.exceptions.custom_exceptions import ResourceNotFound

router = APIRouter(prefix="/libros", tags=["libros"])

# Instanciar el servicio
libro_service = LibroService()


# Modelos Pydantic para request/response
class LibroResponse(BaseModel):
    id: str
    titulo: str
    autor: str
    ubicacion: str
    alta_demanda: bool


class LibroCreateRequest(BaseModel):
    titulo: str
    autor: str
    ubicacion: str
    alta_demanda: bool = False


@router.get("", response_model=list[LibroResponse])
def listar_libros():
    """Listar catálogo de libros"""
    libros = libro_service.listar_libros()
    return [
        LibroResponse(
            id=libro.id,
            titulo=libro.titulo,
            autor=libro.autor,
            ubicacion=libro.ubicacion,
            alta_demanda=libro.alta_demanda,
        )
        for libro in libros
    ]


@router.get("/disponibles", response_model=list[LibroResponse])
def listar_libros_disponibles():
    """Listar libros con ejemplares disponibles"""
    libros = libro_service.listar_libros_disponibles()
    return [
        LibroResponse(
            id=libro.id,
            titulo=libro.titulo,
            autor=libro.autor,
            ubicacion=libro.ubicacion,
            alta_demanda=libro.alta_demanda,
        )
        for libro in libros
    ]


@router.get("/{libro_id}", response_model=LibroResponse)
def obtener_libro(libro_id: str):
    """Obtener detalles de un libro"""
    libro = libro_service.obtener_libro(libro_id)
    if not libro:
        raise HTTPException(status_code=404, detail=f"Libro '{libro_id}' no encontrado")

    return LibroResponse(
        id=libro.id,
        titulo=libro.titulo,
        autor=libro.autor,
        ubicacion=libro.ubicacion,
        alta_demanda=libro.alta_demanda,
    )


@router.post("", response_model=LibroResponse, status_code=201)
def crear_libro(request: LibroCreateRequest):
    """Crear un nuevo libro"""
    libro = libro_service.crear_libro(
        titulo=request.titulo,
        autor=request.autor,
        ubicacion=request.ubicacion,
        alta_demanda=request.alta_demanda,
    )
    return LibroResponse(
        id=libro.id,
        titulo=libro.titulo,
        autor=libro.autor,
        ubicacion=libro.ubicacion,
        alta_demanda=libro.alta_demanda,
    )
