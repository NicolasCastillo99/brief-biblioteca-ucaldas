from app.models.entities import Ejemplar
from app.repositories.base import BaseRepository


class EjemplarRepository(BaseRepository[Ejemplar]):
    """Repositorio para Ejemplar"""

    def get_by_libro_id(self, libro_id: str) -> list[Ejemplar]:
        """Obtener ejemplares por libro ID"""
        return [ejemplar for ejemplar in self.get_all() if ejemplar.libro_id == libro_id]

    def get_disponibles(self) -> list[Ejemplar]:
        """Obtener ejemplares disponibles"""
        return [ejemplar for ejemplar in self.get_all() if ejemplar.estado == "disponible"]

    def get_disponibles_by_libro(self, libro_id: str) -> list[Ejemplar]:
        """Obtener ejemplares disponibles de un libro específico"""
        return [
            ejemplar
            for ejemplar in self.get_all()
            if ejemplar.libro_id == libro_id and ejemplar.estado == "disponible"
        ]
