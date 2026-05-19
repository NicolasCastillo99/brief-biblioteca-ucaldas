"""
Script de inicializacion con datos de prueba.
Ejecutar: python seed_data.py
"""

from datetime import date, timedelta

from app.database import DatabaseManager
from app.models.entities import Ejemplar
from app.repositories.ejemplar_repository import EjemplarRepository
from app.repositories.estudiante_repository import EstudianteRepository
from app.repositories.libro_repository import LibroRepository
from app.repositories.multa_repository import MultaRepository
from app.repositories.prestamo_repository import PrestamoRepository
from app.services.estudiante_service import EstudianteService
from app.services.libro_service import LibroService
from app.services.prestamo_service import PrestamoService


def seed_data():
    """Poblar la base de datos SQLite con datos de prueba."""

    DatabaseManager.clear_database()

    libro_repo = LibroRepository()
    ejemplar_repo = EjemplarRepository()
    estudiante_repo = EstudianteRepository()
    prestamo_repo = PrestamoRepository()
    multa_repo = MultaRepository()

    libro_service = LibroService(libro_repo, ejemplar_repo)
    estudiante_service = EstudianteService(estudiante_repo)
    prestamo_service = PrestamoService(
        prestamo_repo, ejemplar_repo, libro_repo, estudiante_repo, multa_repo
    )

    print("Poblando base de datos con datos de prueba...\n")

    libros = [
        libro_service.crear_libro(
            "Clean Code",
            "Robert C. Martin",
            "Piso 1 - Seccion Programacion",
            alta_demanda=True,
        ),
        libro_service.crear_libro(
            "Design Patterns",
            "Gang of Four",
            "Piso 1 - Seccion Programacion",
            alta_demanda=False,
        ),
        libro_service.crear_libro(
            "Python Avanzado",
            "Guido van Rossum",
            "Piso 2 - Seccion Python",
            alta_demanda=False,
        ),
        libro_service.crear_libro(
            "Refactoring",
            "Martin Fowler",
            "Piso 1 - Seccion Programacion",
            alta_demanda=True,
        ),
        libro_service.crear_libro(
            "The Pragmatic Programmer",
            "Hunt & Thomas",
            "Piso 2 - Seccion General",
            alta_demanda=False,
        ),
    ]
    print(f"{len(libros)} libros creados")

    ejemplares = []
    for libro in libros:
        for i in range(3):
            ejemplar = Ejemplar(
                id=f"{libro.id}_EJE{i + 1}",
                libro_id=libro.id,
                estado="disponible",
            )
            ejemplar_repo.create(ejemplar, ejemplar.id)
            ejemplares.append(ejemplar)
    print(f"{len(ejemplares)} ejemplares creados")

    estudiantes = [
        estudiante_service.crear_estudiante(
            "Juan Perez", "Ingenieria de Sistemas", 5, "pregrado"
        ),
        estudiante_service.crear_estudiante(
            "Maria Garcia", "Maestria en Ingenieria de Software", 2, "posgrado"
        ),
        estudiante_service.crear_estudiante(
            "Carlos Lopez", "Ingenieria de Sistemas", 3, "pregrado"
        ),
        estudiante_service.crear_estudiante(
            "Ana Martinez", "Ingenieria Industrial", 6, "pregrado"
        ),
        estudiante_service.crear_estudiante(
            "Roberto Sanchez", "Doctorado en Ingenieria", 1, "posgrado"
        ),
    ]
    print(f"{len(estudiantes)} estudiantes creados")

    hoy = date.today()

    prestamo1 = prestamo_service.crear_prestamo(
        estudiantes[0].id,
        ejemplares[0].id,
        fecha_prestamo=hoy - timedelta(days=5),
    )
    prestamo2 = prestamo_service.crear_prestamo(
        estudiantes[1].id,
        ejemplares[3].id,
        fecha_prestamo=hoy - timedelta(days=2),
    )
    prestamo3 = prestamo_service.crear_prestamo(
        estudiantes[2].id,
        ejemplares[1].id,
        fecha_prestamo=hoy - timedelta(days=20),
    )

    print("\nDatos de prueba cargados exitosamente")
    print(f"Estudiante ID: {estudiantes[0].id}")
    print(f"Ejemplar ID: {ejemplares[0].id}")
    print(f"Prestamo ID: {prestamo1.id}")
    print(f"Prestamo ID alta demanda: {prestamo2.id}")
    print(f"Prestamo con retraso: {prestamo3.id}")


if __name__ == "__main__":
    seed_data()
