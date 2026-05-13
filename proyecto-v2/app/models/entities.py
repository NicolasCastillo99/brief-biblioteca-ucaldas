from dataclasses import dataclass, field
from datetime import date
from typing import Optional


@dataclass
class Libro:
    """Entidad: Libro"""
    id: str
    titulo: str
    autor: str
    ubicacion: str
    alta_demanda: bool = False  # Campo agregado para RN5


@dataclass
class Ejemplar:
    """Entidad: Ejemplar"""
    id: str
    libro_id: str
    estado: str = "disponible"  # disponible / prestado


@dataclass
class Estudiante:
    """Entidad: Estudiante"""
    id: str
    nombre: str
    programa: str
    semestre: int
    tipo: str  # pregrado / posgrado
    multas_pendientes: float = 0.0


@dataclass
class Prestamo:
    """Entidad: Préstamo"""
    id: str
    estudiante_id: str
    ejemplar_id: str
    fecha_prestamo: date
    fecha_devolucion_esperada: date
    fecha_devolucion_real: Optional[date] = None
    estado: str = "activo"  # activo / devuelto / vencido
    renovado: bool = False


@dataclass
class Multa:
    """Entidad: Multa"""
    id: str
    estudiante_id: str
    prestamo_id: str
    monto: float
    dias_retraso: int
    pagada: bool = False
