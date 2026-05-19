from app.models.entities import Estudiante
from app.repositories.base import BaseRepository


class EstudianteRepository(BaseRepository[Estudiante]):
    """Repositorio para Estudiante."""

    table_name = "estudiantes"
    entity_class = Estudiante

    def get_by_tipo(self, tipo: str) -> list[Estudiante]:
        """Obtener estudiantes por tipo."""
        cursor = self.connection.execute(
            "SELECT * FROM estudiantes WHERE tipo = ?",
            (tipo,),
        )
        return [self._row_to_entity(row) for row in cursor.fetchall()]

    def get_by_programa(self, programa: str) -> list[Estudiante]:
        """Obtener estudiantes por programa."""
        cursor = self.connection.execute(
            "SELECT * FROM estudiantes WHERE programa = ?",
            (programa,),
        )
        return [self._row_to_entity(row) for row in cursor.fetchall()]

    def _deserialize_record(self, payload: dict) -> dict:
        payload["semestre"] = int(payload["semestre"])
        payload["multas_pendientes"] = float(payload["multas_pendientes"])
        return payload
