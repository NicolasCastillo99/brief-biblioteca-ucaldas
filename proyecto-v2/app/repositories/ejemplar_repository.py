from app.models.entities import Ejemplar
from app.repositories.base import BaseRepository


class EjemplarRepository(BaseRepository[Ejemplar]):
    """Repositorio para Ejemplar."""

    table_name = "ejemplares"
    entity_class = Ejemplar

    def get_by_libro_id(self, libro_id: str) -> list[Ejemplar]:
        """Obtener ejemplares por libro ID."""
        cursor = self.connection.execute(
            "SELECT * FROM ejemplares WHERE libro_id = ?",
            (libro_id,),
        )
        return [self._row_to_entity(row) for row in cursor.fetchall()]

    def get_disponibles(self) -> list[Ejemplar]:
        """Obtener ejemplares disponibles."""
        cursor = self.connection.execute(
            "SELECT * FROM ejemplares WHERE estado = ?",
            ("disponible",),
        )
        return [self._row_to_entity(row) for row in cursor.fetchall()]

    def get_disponibles_by_libro(self, libro_id: str) -> list[Ejemplar]:
        """Obtener ejemplares disponibles de un libro específico."""
        cursor = self.connection.execute(
            "SELECT * FROM ejemplares WHERE libro_id = ? AND estado = ?",
            (libro_id, "disponible"),
        )
        return [self._row_to_entity(row) for row in cursor.fetchall()]
