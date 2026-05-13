import pytest
from datetime import date
from app.models.entities import Libro, Ejemplar, Estudiante, Prestamo, Multa
from app.repositories.libro_repository import LibroRepository
from app.repositories.ejemplar_repository import EjemplarRepository
from app.repositories.estudiante_repository import EstudianteRepository
from app.repositories.prestamo_repository import PrestamoRepository
from app.repositories.multa_repository import MultaRepository


@pytest.fixture
def libro_repository():
    """Fixture de repositorio de libros"""
    return LibroRepository()


@pytest.fixture
def ejemplar_repository():
    """Fixture de repositorio de ejemplares"""
    return EjemplarRepository()


@pytest.fixture
def estudiante_repository():
    """Fixture de repositorio de estudiantes"""
    return EstudianteRepository()


@pytest.fixture
def prestamo_repository():
    """Fixture de repositorio de préstamos"""
    return PrestamoRepository()


@pytest.fixture
def multa_repository():
    """Fixture de repositorio de multas"""
    return MultaRepository()


@pytest.fixture
def sample_libro(libro_repository):
    """Fixture de libro de prueba"""
    libro = Libro(
        id="LIB001",
        titulo="Python Avanzado",
        autor="Guido van Rossum",
        ubicacion="Piso 2 - Sección A",
        alta_demanda=False,
    )
    libro_repository.create(libro, libro.id)
    return libro


@pytest.fixture
def sample_libro_alta_demanda(libro_repository):
    """Fixture de libro de alta demanda"""
    libro = Libro(
        id="LIB002",
        titulo="Clean Code",
        autor="Robert C. Martin",
        ubicacion="Piso 1 - Sección B",
        alta_demanda=True,
    )
    libro_repository.create(libro, libro.id)
    return libro


@pytest.fixture
def sample_ejemplar(ejemplar_repository, sample_libro):
    """Fixture de ejemplar disponible"""
    ejemplar = Ejemplar(
        id="EJE001",
        libro_id=sample_libro.id,
        estado="disponible",
    )
    ejemplar_repository.create(ejemplar, ejemplar.id)
    return ejemplar


@pytest.fixture
def sample_estudiante_pregrado(estudiante_repository):
    """Fixture de estudiante de pregrado"""
    estudiante = Estudiante(
        id="EST001",
        nombre="Juan Pérez",
        programa="Ingeniería de Sistemas",
        semestre=5,
        tipo="pregrado",
        multas_pendientes=0.0,
    )
    estudiante_repository.create(estudiante, estudiante.id)
    return estudiante


@pytest.fixture
def sample_estudiante_posgrado(estudiante_repository):
    """Fixture de estudiante de posgrado"""
    estudiante = Estudiante(
        id="EST002",
        nombre="María García",
        programa="Maestría en Ingeniería de Software",
        semestre=2,
        tipo="posgrado",
        multas_pendientes=0.0,
    )
    estudiante_repository.create(estudiante, estudiante.id)
    return estudiante


@pytest.fixture
def sample_prestamo(prestamo_repository, sample_estudiante_pregrado, sample_ejemplar):
    """Fixture de préstamo activo"""
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
