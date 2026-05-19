from app.models.entities import Multa
from app.repositories.base import BaseRepository


class MultaRepository(BaseRepository[Multa]):
    """Repositorio para Multa."""

    table_name = "multas"
    entity_class = Multa

    def get_by_estudiante_id(self, estudiante_id: str) -> list[Multa]:
        """Obtener multas por estudiante ID."""
        cursor = self.connection.execute(
            "SELECT * FROM multas WHERE estudiante_id = ?",
            (estudiante_id,),
        )
        return [self._row_to_entity(row) for row in cursor.fetchall()]

    def get_by_prestamo_id(self, prestamo_id: str) -> Multa | None:
        """Obtener multa por préstamo ID."""
        cursor = self.connection.execute(
            "SELECT * FROM multas WHERE prestamo_id = ? LIMIT 1",
            (prestamo_id,),
        )
        row = cursor.fetchone()
        return self._row_to_entity(row) if row else None

    def get_pendientes_by_estudiante_id(self, estudiante_id: str) -> list[Multa]:
        """Obtener multas pendientes por estudiante ID."""
        cursor = self.connection.execute(
            "SELECT * FROM multas WHERE estudiante_id = ? AND pagada = 0",
            (estudiante_id,),
        )
        return [self._row_to_entity(row) for row in cursor.fetchall()]

    def _deserialize_record(self, payload: dict) -> dict:
        payload["monto"] = float(payload["monto"])
        payload["dias_retraso"] = int(payload["dias_retraso"])
        payload["pagada"] = bool(payload["pagada"])
        return payload
