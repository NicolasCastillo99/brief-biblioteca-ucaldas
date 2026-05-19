from app.models.entities import Libro
from app.repositories.base import BaseRepository


class LibroRepository(BaseRepository[Libro]):
    """Repositorio para Libro."""

    table_name = "libros"
    entity_class = Libro

    def get_by_titulo(self, titulo: str) -> list[Libro]:
        """Obtener libros por título."""
        cursor = self.connection.execute(
            "SELECT * FROM libros WHERE LOWER(titulo) LIKE ?",
            (f"%{titulo.lower()}%",),
        )
        return [self._row_to_entity(row) for row in cursor.fetchall()]

    def get_by_autor(self, autor: str) -> list[Libro]:
        """Obtener libros por autor."""
        cursor = self.connection.execute(
            "SELECT * FROM libros WHERE LOWER(autor) LIKE ?",
            (f"%{autor.lower()}%",),
        )
        return [self._row_to_entity(row) for row in cursor.fetchall()]

    def _deserialize_record(self, payload: dict) -> dict:
        payload["alta_demanda"] = bool(payload["alta_demanda"])
        return payload
