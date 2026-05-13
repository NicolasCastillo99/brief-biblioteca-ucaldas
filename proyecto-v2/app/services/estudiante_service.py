from typing import Optional
import uuid
from datetime import date, timedelta

from app.models.entities import Estudiante
from app.repositories.estudiante_repository import EstudianteRepository


class EstudianteService:
    """Servicio de lógica de negocio para Estudiantes"""

    def __init__(self, estudiante_repository: Optional[EstudianteRepository] = None):
        self.estudiante_repo = estudiante_repository or EstudianteRepository()

    def crear_estudiante(
        self,
        nombre: str,
        programa: str,
        semestre: int,
        tipo: str,  # pregrado o posgrado
    ) -> Estudiante:
        """Crear un nuevo estudiante"""
        estudiante_id = str(uuid.uuid4())
        estudiante = Estudiante(
            id=estudiante_id,
            nombre=nombre,
            programa=programa,
            semestre=semestre,
            tipo=tipo,
            multas_pendientes=0.0,
        )
        return self.estudiante_repo.create(estudiante, estudiante_id)

    def obtener_estudiante(self, estudiante_id: str) -> Optional[Estudiante]:
        """Obtener un estudiante por ID"""
        return self.estudiante_repo.get_by_id(estudiante_id)

    def listar_estudiantes(self) -> list[Estudiante]:
        """Listar todos los estudiantes"""
        return self.estudiante_repo.get_all()

    def actualizar_multas_pendientes(
        self, estudiante_id: str, monto: float
    ) -> Estudiante:
        """Actualizar el monto de multas pendientes de un estudiante"""
        estudiante = self.estudiante_repo.get_by_id(estudiante_id)
        if estudiante:
            estudiante.multas_pendientes += monto
            return self.estudiante_repo.update(estudiante_id, estudiante)
        return None
