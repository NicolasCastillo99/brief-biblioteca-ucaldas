from datetime import date

import pytest

from app.database import DatabaseManager
from app.models.entities import Ejemplar, Estudiante, Libro, Multa, Prestamo
from app.repositories.ejemplar_repository import EjemplarRepository
from app.repositories.estudiante_repository import EstudianteRepository
from app.repositories.libro_repository import LibroRepository
from app.repositories.multa_repository import MultaRepository
from app.repositories.prestamo_repository import PrestamoRepository


@pytest.fixture(autouse=True)
def clean_database():
    """Garantiza aislamiento entre pruebas."""
    DatabaseManager.clear_database()
    yield
    DatabaseManager.clear_database()


@pytest.fixture
def libro_repository():
    return LibroRepository()


@pytest.fixture
def ejemplar_repository():
    return EjemplarRepository()


@pytest.fixture
def estudiante_repository():
    return EstudianteRepository()


@pytest.fixture
def prestamo_repository():
    return PrestamoRepository()


@pytest.fixture
def multa_repository():
    return MultaRepository()


@pytest.fixture
def sample_libro(libro_repository):
    libro = Libro(
        id="LIB001",
        titulo="Python Avanzado",
        autor="Guido van Rossum",
        ubicacion="Piso 2 - Seccion A",
        alta_demanda=False,
    )
    libro_repository.create(libro, libro.id)
    return libro


@pytest.fixture
def sample_libro_alta_demanda(libro_repository):
    libro = Libro(
        id="LIB002",
        titulo="Clean Code",
        autor="Robert C. Martin",
        ubicacion="Piso 1 - Seccion B",
        alta_demanda=True,
    )
    libro_repository.create(libro, libro.id)
    return libro


@pytest.fixture
def sample_ejemplar(ejemplar_repository, sample_libro):
    ejemplar = Ejemplar(
        id="EJE001",
        libro_id=sample_libro.id,
        estado="disponible",
    )
    ejemplar_repository.create(ejemplar, ejemplar.id)
    return ejemplar


@pytest.fixture
def sample_estudiante_pregrado(estudiante_repository):
    estudiante = Estudiante(
        id="EST001",
        nombre="Juan Perez",
        programa="Ingenieria de Sistemas",
        semestre=5,
        tipo="pregrado",
        multas_pendientes=0.0,
    )
    estudiante_repository.create(estudiante, estudiante.id)
    return estudiante


@pytest.fixture
def sample_estudiante_posgrado(estudiante_repository):
    estudiante = Estudiante(
        id="EST002",
        nombre="Maria Garcia",
        programa="Maestria en Ingenieria de Software",
        semestre=2,
        tipo="posgrado",
        multas_pendientes=0.0,
    )
    estudiante_repository.create(estudiante, estudiante.id)
    return estudiante


@pytest.fixture
def sample_prestamo(prestamo_repository, sample_estudiante_pregrado, sample_ejemplar):
    prestamo = Prestamo(
        id="PRES001",
        estudiante_id=sample_estudiante_pregrado.id,
        ejemplar_id=sample_ejemplar.id,
        fecha_prestamo=date(2026, 5, 1),
        fecha_devolucion_esperada=date(2026, 5, 16),
        estado="activo",
        renovado=False,
    )
    prestamo_repository.create(prestamo, prestamo.id)
    return prestamo
