from app.models.entities import Estudiante
from app.repositories.base import BaseRepository


class EstudianteRepository(BaseRepository[Estudiante]):
    """Repositorio para Estudiante"""

    def get_by_tipo(self, tipo: str) -> list[Estudiante]:
        """Obtener estudiantes por tipo (pregrado/posgrado)"""
        return [estudiante for estudiante in self.get_all() if estudiante.tipo == tipo]

    def get_by_programa(self, programa: str) -> list[Estudiante]:
        """Obtener estudiantes por programa"""
        return [estudiante for estudiante in self.get_all() if estudiante.programa == programa]
