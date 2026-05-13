from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import date
from typing import Optional

from app.services.prestamo_service import PrestamoService
from app.services.estudiante_service import EstudianteService
from app.repositories.prestamo_repository import PrestamoRepository
from app.repositories.ejemplar_repository import EjemplarRepository
from app.repositories.libro_repository import LibroRepository
from app.repositories.estudiante_repository import EstudianteRepository
from app.repositories.multa_repository import MultaRepository
from app.exceptions.custom_exceptions import ResourceNotFound

router = APIRouter(prefix="/estudiantes", tags=["estudiantes"])

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
estudiante_service = EstudianteService(estudiante_repository=estudiante_repo)


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


class EstudianteResponse(BaseModel):
    id: str
    nombre: str
    programa: str
    semestre: int
    tipo: str
    multas_pendientes: float


class EstudianteCreateRequest(BaseModel):
    nombre: str
    programa: str
    semestre: int
    tipo: str


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


def _map_estudiante_to_response(estudiante) -> EstudianteResponse:
    """Convertir entidad Estudiante a EstudianteResponse"""
    return EstudianteResponse(
        id=estudiante.id,
        nombre=estudiante.nombre,
        programa=estudiante.programa,
        semestre=estudiante.semestre,
        tipo=estudiante.tipo,
        multas_pendientes=estudiante.multas_pendientes,
    )


@router.post("", response_model=EstudianteResponse, status_code=201)
def crear_estudiante(request: EstudianteCreateRequest):
    """Crear un nuevo estudiante"""
    estudiante = estudiante_service.crear_estudiante(
        nombre=request.nombre,
        programa=request.programa,
        semestre=request.semestre,
        tipo=request.tipo,
    )
    return _map_estudiante_to_response(estudiante)


@router.get("/{estudiante_id}", response_model=EstudianteResponse)
def obtener_estudiante(estudiante_id: str):
    """Obtener detalles de un estudiante"""
    estudiante = estudiante_service.obtener_estudiante(estudiante_id)
    if not estudiante:
        raise HTTPException(
            status_code=404, detail=f"Estudiante '{estudiante_id}' no encontrado"
        )

    return _map_estudiante_to_response(estudiante)


@router.get("/{estudiante_id}/prestamos", response_model=list[PrestamoResponse])
def obtener_prestamos_activos(estudiante_id: str):
    """Obtener préstamos activos de un estudiante"""
    # Verificar que el estudiante existe
    estudiante = estudiante_service.obtener_estudiante(estudiante_id)
    if not estudiante:
        raise HTTPException(
            status_code=404, detail=f"Estudiante '{estudiante_id}' no encontrado"
        )

    prestamos = prestamo_service.obtener_prestamos_activos_estudiante(estudiante_id)
    return [_map_prestamo_to_response(p) for p in prestamos]


@router.get("/{estudiante_id}/historial", response_model=list[PrestamoResponse])
def obtener_historial_prestamos(estudiante_id: str):
    """Obtener historial completo de préstamos de un estudiante"""
    try:
        prestamos = prestamo_service.obtener_historial_prestamos_estudiante(
            estudiante_id
        )
        return [_map_prestamo_to_response(p) for p in prestamos]
    except ResourceNotFound as e:
        raise HTTPException(status_code=404, detail=e.message)
