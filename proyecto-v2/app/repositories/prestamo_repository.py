from datetime import date

from app.models.entities import Prestamo
from app.repositories.base import BaseRepository


class PrestamoRepository(BaseRepository[Prestamo]):
    """Repositorio para Prestamo."""

    table_name = "prestamos"
    entity_class = Prestamo

    def get_by_estudiante_id(self, estudiante_id: str) -> list[Prestamo]:
        """Obtener préstamos por estudiante ID."""
        cursor = self.connection.execute(
            "SELECT * FROM prestamos WHERE estudiante_id = ?",
            (estudiante_id,),
        )
        return [self._row_to_entity(row) for row in cursor.fetchall()]

    def get_activos_by_estudiante_id(self, estudiante_id: str) -> list[Prestamo]:
        """Obtener préstamos activos por estudiante ID."""
        cursor = self.connection.execute(
            "SELECT * FROM prestamos WHERE estudiante_id = ? AND estado = ?",
            (estudiante_id, "activo"),
        )
        return [self._row_to_entity(row) for row in cursor.fetchall()]

    def get_vencidos_by_estudiante_id(self, estudiante_id: str) -> list[Prestamo]:
        """Obtener préstamos vencidos por estudiante ID."""
        cursor = self.connection.execute(
            "SELECT * FROM prestamos WHERE estudiante_id = ? AND estado = ?",
            (estudiante_id, "vencido"),
        )
        return [self._row_to_entity(row) for row in cursor.fetchall()]

    def get_by_ejemplar_id(self, ejemplar_id: str) -> list[Prestamo]:
        """Obtener préstamos por ejemplar ID."""
        cursor = self.connection.execute(
            "SELECT * FROM prestamos WHERE ejemplar_id = ?",
            (ejemplar_id,),
        )
        return [self._row_to_entity(row) for row in cursor.fetchall()]

    def get_activo_by_ejemplar_id(self, ejemplar_id: str) -> Prestamo | None:
        """Obtener préstamo activo de un ejemplar."""
        cursor = self.connection.execute(
            "SELECT * FROM prestamos WHERE ejemplar_id = ? AND estado = ? LIMIT 1",
            (ejemplar_id, "activo"),
        )
        row = cursor.fetchone()
        return self._row_to_entity(row) if row else None

    def get_vencidos(self) -> list[Prestamo]:
        """Obtener todos los préstamos vencidos."""
        cursor = self.connection.execute(
            "SELECT * FROM prestamos WHERE estado = ?",
            ("vencido",),
        )
        return [self._row_to_entity(row) for row in cursor.fetchall()]

    def _deserialize_record(self, payload: dict) -> dict:
        payload["fecha_prestamo"] = date.fromisoformat(payload["fecha_prestamo"])
        payload["fecha_devolucion_esperada"] = date.fromisoformat(
            payload["fecha_devolucion_esperada"]
        )
        if payload["fecha_devolucion_real"]:
            payload["fecha_devolucion_real"] = date.fromisoformat(
                payload["fecha_devolucion_real"]
            )
        payload["renovado"] = bool(payload["renovado"])
        return payload
