from __future__ import annotations

from abc import ABC
from dataclasses import asdict
from datetime import date
from typing import Generic, Optional, TypeVar

from app.database import DatabaseManager

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    """Repositorio genérico respaldado por SQLite."""

    table_name: str = ""
    entity_class: type[T]

    def __init__(self, db_path: str | None = None):
        self.db_path = db_path
        self.connection = DatabaseManager.get_connection(db_path)

    def create(self, entity: T, entity_id: str) -> T:
        """Crear una entidad."""
        payload = self._entity_to_record(entity)
        columns = list(payload.keys())
        placeholders = ", ".join("?" for _ in columns)
        sql = (
            f"INSERT INTO {self.table_name} ({', '.join(columns)}) "
            f"VALUES ({placeholders})"
        )
        with self.connection:
            self.connection.execute(sql, [payload[column] for column in columns])
        return entity

    def get_by_id(self, entity_id: str) -> Optional[T]:
        """Obtener una entidad por ID."""
        cursor = self.connection.execute(
            f"SELECT * FROM {self.table_name} WHERE id = ?",
            (entity_id,),
        )
        row = cursor.fetchone()
        return self._row_to_entity(row) if row else None

    def get_all(self) -> list[T]:
        """Obtener todas las entidades."""
        cursor = self.connection.execute(f"SELECT * FROM {self.table_name}")
        return [self._row_to_entity(row) for row in cursor.fetchall()]

    def update(self, entity_id: str, entity: T) -> T:
        """Actualizar una entidad."""
        payload = self._entity_to_record(entity)
        assignments = ", ".join(f"{column} = ?" for column in payload.keys())
        values = [payload[column] for column in payload.keys()]
        values.append(entity_id)
        with self.connection:
            self.connection.execute(
                f"UPDATE {self.table_name} SET {assignments} WHERE id = ?",
                values,
            )
        return entity

    def delete(self, entity_id: str) -> bool:
        """Eliminar una entidad."""
        with self.connection:
            cursor = self.connection.execute(
                f"DELETE FROM {self.table_name} WHERE id = ?",
                (entity_id,),
            )
        return cursor.rowcount > 0

    def exists(self, entity_id: str) -> bool:
        """Verificar si una entidad existe."""
        cursor = self.connection.execute(
            f"SELECT 1 FROM {self.table_name} WHERE id = ? LIMIT 1",
            (entity_id,),
        )
        return cursor.fetchone() is not None

    def _entity_to_record(self, entity: T) -> dict:
        payload = asdict(entity)
        return {key: self._serialize_value(value) for key, value in payload.items()}

    def _row_to_entity(self, row) -> T:
        payload = dict(row)
        return self.entity_class(**self._deserialize_record(payload))

    def _deserialize_record(self, payload: dict) -> dict:
        return payload

    @staticmethod
    def _serialize_value(value):
        if isinstance(value, date):
            return value.isoformat()
        if isinstance(value, bool):
            return int(value)
        return value
