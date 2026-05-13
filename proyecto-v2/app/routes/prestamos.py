from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import date

from app.services.prestamo_service import PrestamoService
from app.services.libro_service import LibroService
from app.services.estudiante_service import EstudianteService
from app.repositories.prestamo_repository import PrestamoRepository
from app.repositories.ejemplar_repository import EjemplarRepository
from app.repositories.libro_repository import LibroRepository
from app.repositories.estudiante_repository import EstudianteRepository
from app.repositories.multa_repository import MultaRepository
from app.exceptions.custom_exceptions import (
    LimitePrestamosAlcanzado,
    MultasPendientes,
    PrestamosVencidos,
    EjemplarNoDisponible,
    NoSePuedeRenovar,
    PrestamoNoActivo,
    PrestamoYaDevuelto,
    ResourceNotFound,
    BibliotecaException,
)

router = APIRouter(prefix="/prestamos", tags=["prestamos"])

# Instanciar repositorios
prestamo_repo = PrestamoRepository()
ejemplar_repo = EjemplarRepository()
libro_repo = LibroRepository()
estudiante_repo = EstudianteRepository()
multa_repo = MultaRepository()

# Instanciar servicios
prestamo_service = PrestamoService(
    prestamo_repository=prestamo_repo,
    ejemplar_repository=ejemplar_repo,
    libro_repository=libro_repo,
    estudiante_repository=estudiante_repo,
    multa_repository=multa_repo,
)


# Modelos Pydantic
class PrestamoResponse(BaseModel):
    id: str
    estudiante_id: str
    ejemplar_id: str
    fecha_prestamo: date
    fecha_devolucion_esperada: date
    fecha_devolucion_real: Optional[date]
    estado: str
    renovado: bool


class CrearPrestamoRequest(BaseModel):
    estudiante_id: str
    ejemplar_id: str
    fecha_prestamo: Optional[date] = None


class RegistrarDevolucionRequest(BaseModel):
    fecha_devolucion_real: Optional[date] = None


class ErrorResponse(BaseModel):
    error: str


def _map_prestamo_to_response(prestamo) -> PrestamoResponse:
    """Convertir entidad Prestamo a PrestamoResponse"""
    return PrestamoResponse(
        id=prestamo.id,
        estudiante_id=prestamo.estudiante_id,
        ejemplar_id=prestamo.ejemplar_id,
        fecha_prestamo=prestamo.fecha_prestamo,
        fecha_devolucion_esperada=prestamo.fecha_devolucion_esperada,
        fecha_devolucion_real=prestamo.fecha_devolucion_real,
        estado=prestamo.estado,
        renovado=prestamo.renovado,
    )


@router.post("", response_model=PrestamoResponse, status_code=201)
def crear_prestamo(request: CrearPrestamoRequest):
    """Crear un nuevo préstamo"""
    try:
        prestamo = prestamo_service.crear_prestamo(
            estudiante_id=request.estudiante_id,
            ejemplar_id=request.ejemplar_id,
            fecha_prestamo=request.fecha_prestamo,
        )
        return _map_prestamo_to_response(prestamo)
    except LimitePrestamosAlcanzado:
        raise HTTPException(
            status_code=409,
            detail={"error": "limite_prestamos_alcanzado"},
        )
    except MultasPendientes:
        raise HTTPException(
            status_code=409,
            detail={"error": "multas_pendientes"},
        )
    except PrestamosVencidos:
        raise HTTPException(
            status_code=409,
            detail={"error": "prestamos_vencidos"},
        )
    except EjemplarNoDisponible:
        raise HTTPException(
            status_code=409,
            detail={"error": "ejemplar_no_disponible"},
        )
    except ResourceNotFound as e:
        raise HTTPException(status_code=404, detail=e.message)


@router.post("/{prestamo_id}/devolver", response_model=PrestamoResponse)
def registrar_devolucion(
    prestamo_id: str, request: RegistrarDevolucionRequest
):
    """Registrar la devolución de un préstamo"""
    try:
        prestamo = prestamo_service.registrar_devolucion(
            prestamo_id=prestamo_id,
            fecha_devolucion_real=request.fecha_devolucion_real,
        )
        return _map_prestamo_to_response(prestamo)
    except PrestamoYaDevuelto:
        raise HTTPException(
            status_code=409,
            detail={"error": "prestamo_ya_devuelto"},
        )
    except ResourceNotFound as e:
        raise HTTPException(status_code=404, detail=e.message)


@router.post("/{prestamo_id}/renovar", response_model=PrestamoResponse)
def renovar_prestamo(prestamo_id: str):
    """Renovar un préstamo"""
    try:
        prestamo = prestamo_service.renovar_prestamo(prestamo_id)
        return _map_prestamo_to_response(prestamo)
    except PrestamoNoActivo:
        raise HTTPException(
            status_code=409,
            detail={"error": "no_se_puede_renovar"},
        )
    except ResourceNotFound as e:
        raise HTTPException(status_code=404, detail=e.message)


@router.get("/vencidos", response_model=list[PrestamoResponse])
def listar_prestamos_vencidos():
    """Listar todos los préstamos vencidos"""
    # Marcar automáticamente los que cumplan la condición
    prestamo_service.marcar_prestamos_como_vencidos()
    
    prestamos = prestamo_service.listar_prestamos_vencidos()
    return [_map_prestamo_to_response(p) for p in prestamos]


@router.get("/{prestamo_id}", response_model=PrestamoResponse)
def obtener_prestamo(prestamo_id: str):
    """Obtener detalles de un préstamo"""
    prestamo = prestamo_service.obtener_prestamo(prestamo_id)
    if not prestamo:
        raise HTTPException(status_code=404, detail=f"Préstamo '{prestamo_id}' no encontrado")

    return _map_prestamo_to_response(prestamo)
