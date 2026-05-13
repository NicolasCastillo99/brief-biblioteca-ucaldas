from app.models.entities import Prestamo
from app.repositories.base import BaseRepository


class PrestamoRepository(BaseRepository[Prestamo]):
    """Repositorio para Prestamo"""

    def get_by_estudiante_id(self, estudiante_id: str) -> list[Prestamo]:
        """Obtener préstamos por estudiante ID"""
        return [prestamo for prestamo in self.get_all() if prestamo.estudiante_id == estudiante_id]

    def get_activos_by_estudiante_id(self, estudiante_id: str) -> list[Prestamo]:
        """Obtener préstamos activos por estudiante ID"""
        return [
            prestamo
            for prestamo in self.get_all()
            if prestamo.estudiante_id == estudiante_id and prestamo.estado == "activo"
        ]

    def get_vencidos_by_estudiante_id(self, estudiante_id: str) -> list[Prestamo]:
        """Obtener préstamos vencidos por estudiante ID"""
        return [
            prestamo
            for prestamo in self.get_all()
            if prestamo.estudiante_id == estudiante_id and prestamo.estado == "vencido"
        ]

    def get_by_ejemplar_id(self, ejemplar_id: str) -> list[Prestamo]:
        """Obtener préstamos por ejemplar ID"""
        return [prestamo for prestamo in self.get_all() if prestamo.ejemplar_id == ejemplar_id]

    def get_activo_by_ejemplar_id(self, ejemplar_id: str) -> Prestamo | None:
        """Obtener préstamo activo de un ejemplar (debe haber solo uno)"""
        for prestamo in self.get_all():
            if prestamo.ejemplar_id == ejemplar_id and prestamo.estado == "activo":
                return prestamo
        return None

    def get_vencidos(self) -> list[Prestamo]:
        """Obtener todos los préstamos vencidos"""
        return [prestamo for prestamo in self.get_all() if prestamo.estado == "vencido"]
