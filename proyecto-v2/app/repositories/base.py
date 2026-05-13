from abc import ABC, abstractmethod
from typing import List, Optional, TypeVar, Generic

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    """Repositorio genérico en memoria"""

    def __init__(self):
        self.data: dict[str, T] = {}

    def create(self, entity: T, entity_id: str) -> T:
        """Crear una entidad"""
        self.data[entity_id] = entity
        return entity

    def get_by_id(self, entity_id: str) -> Optional[T]:
        """Obtener una entidad por ID"""
        return self.data.get(entity_id)

    def get_all(self) -> List[T]:
        """Obtener todas las entidades"""
        return list(self.data.values())

    def update(self, entity_id: str, entity: T) -> T:
        """Actualizar una entidad"""
        self.data[entity_id] = entity
        return entity

    def delete(self, entity_id: str) -> bool:
        """Eliminar una entidad"""
        if entity_id in self.data:
            del self.data[entity_id]
            return True
        return False

    def exists(self, entity_id: str) -> bool:
        """Verificar si una entidad existe"""
        return entity_id in self.data
