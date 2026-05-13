from app.models.entities import Libro
from app.repositories.base import BaseRepository


class LibroRepository(BaseRepository[Libro]):
    """Repositorio para Libro"""

    def get_by_titulo(self, titulo: str) -> list[Libro]:
        """Obtener libros por título"""
        return [libro for libro in self.get_all() if titulo.lower() in libro.titulo.lower()]

    def get_by_autor(self, autor: str) -> list[Libro]:
        """Obtener libros por autor"""
        return [libro for libro in self.get_all() if autor.lower() in libro.autor.lower()]
