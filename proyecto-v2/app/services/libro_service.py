from typing import Optional
import uuid
from datetime import date

from app.models.entities import Libro
from app.repositories.libro_repository import LibroRepository
from app.repositories.ejemplar_repository import EjemplarRepository


class LibroService:
    """Servicio de lógica de negocio para Libros"""

    def __init__(
        self,
        libro_repository: Optional[LibroRepository] = None,
        ejemplar_repository: Optional[EjemplarRepository] = None,
    ):
        self.libro_repo = libro_repository or LibroRepository()
        self.ejemplar_repo = ejemplar_repository or EjemplarRepository()

    def crear_libro(
        self,
        titulo: str,
        autor: str,
        ubicacion: str,
        alta_demanda: bool = False,
    ) -> Libro:
        """Crear un nuevo libro"""
        libro_id = str(uuid.uuid4())
        libro = Libro(
            id=libro_id,
            titulo=titulo,
            autor=autor,
            ubicacion=ubicacion,
            alta_demanda=alta_demanda,
        )
        return self.libro_repo.create(libro, libro_id)

    def obtener_libro(self, libro_id: str) -> Optional[Libro]:
        """Obtener un libro por ID"""
        return self.libro_repo.get_by_id(libro_id)

    def listar_libros(self) -> list[Libro]:
        """Listar todos los libros"""
        return self.libro_repo.get_all()

    def listar_libros_disponibles(self) -> list[Libro]:
        """Listar libros que tienen al menos un ejemplar disponible"""
        ejemplares_disponibles = self.ejemplar_repo.get_disponibles()
        libro_ids_disponibles = set(ej.libro_id for ej in ejemplares_disponibles)
        libros = self.libro_repo.get_all()
        return [libro for libro in libros if libro.id in libro_ids_disponibles]
