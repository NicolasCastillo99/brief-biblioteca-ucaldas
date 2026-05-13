from app.models.entities import Multa
from app.repositories.base import BaseRepository


class MultaRepository(BaseRepository[Multa]):
    """Repositorio para Multa"""

    def get_by_estudiante_id(self, estudiante_id: str) -> list[Multa]:
        """Obtener multas por estudiante ID"""
        return [multa for multa in self.get_all() if multa.estudiante_id == estudiante_id]

    def get_by_prestamo_id(self, prestamo_id: str) -> Multa | None:
        """Obtener multa por préstamo ID (debe haber solo una)"""
        for multa in self.get_all():
            if multa.prestamo_id == prestamo_id:
                return multa
        return None

    def get_pendientes_by_estudiante_id(self, estudiante_id: str) -> list[Multa]:
        """Obtener multas pendientes de pago por estudiante ID"""
        return [
            multa
            for multa in self.get_all()
            if multa.estudiante_id == estudiante_id and not multa.pagada
        ]
