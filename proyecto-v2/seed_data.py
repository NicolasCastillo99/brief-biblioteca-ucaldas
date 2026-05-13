"""
Script de inicialización con datos de prueba.
Ejecutar: python seed_data.py
"""

from datetime import date, timedelta
from app.services.libro_service import LibroService
from app.services.estudiante_service import EstudianteService
from app.services.prestamo_service import PrestamoService
from app.repositories.libro_repository import LibroRepository
from app.repositories.ejemplar_repository import EjemplarRepository
from app.repositories.estudiante_repository import EstudianteRepository
from app.repositories.prestamo_repository import PrestamoRepository
from app.repositories.multa_repository import MultaRepository
from app.models.entities import Ejemplar


def seed_data():
    """Poblar la base de datos en memoria con datos de prueba"""

    # Inicializar repositorios
    libro_repo = LibroRepository()
    ejemplar_repo = EjemplarRepository()
    estudiante_repo = EstudianteRepository()
    prestamo_repo = PrestamoRepository()
    multa_repo = MultaRepository()

    # Inicializar servicios
    libro_service = LibroService(libro_repo, ejemplar_repo)
    estudiante_service = EstudianteService(estudiante_repo)
    prestamo_service = PrestamoService(
        prestamo_repo, ejemplar_repo, libro_repo, estudiante_repo, multa_repo
    )

    print("🔄 Poblando base de datos con datos de prueba...\n")

    # Crear Libros
    print("📚 Creando libros...")
    libros = [
        libro_service.crear_libro(
            "Clean Code",
            "Robert C. Martin",
            "Piso 1 - Sección Programación",
            alta_demanda=True,
        ),
        libro_service.crear_libro(
            "Design Patterns",
            "Gang of Four",
            "Piso 1 - Sección Programación",
            alta_demanda=False,
        ),
        libro_service.crear_libro(
            "Python Avanzado",
            "Guido van Rossum",
            "Piso 2 - Sección Python",
            alta_demanda=False,
        ),
        libro_service.crear_libro(
            "Refactoring",
            "Martin Fowler",
            "Piso 1 - Sección Programación",
            alta_demanda=True,
        ),
        libro_service.crear_libro(
            "The Pragmatic Programmer",
            "Hunt & Thomas",
            "Piso 2 - Sección General",
            alta_demanda=False,
        ),
    ]
    print(f"✅ {len(libros)} libros creados\n")

    # Crear Ejemplares
    print("📖 Creando ejemplares...")
    ejemplares = []
    for libro in libros:
        for i in range(3):  # 3 ejemplares por libro
            ejemplar = Ejemplar(
                id=f"{libro.id}_EJE{i+1}",
                libro_id=libro.id,
                estado="disponible",
            )
            ejemplar_repo.create(ejemplar, ejemplar.id)
            ejemplares.append(ejemplar)
    print(f"✅ {len(ejemplares)} ejemplares creados\n")

    # Crear Estudiantes
    print("👥 Creando estudiantes...")
    estudiantes = [
        estudiante_service.crear_estudiante(
            "Juan Pérez",
            "Ingeniería de Sistemas",
            5,
            "pregrado",
        ),
        estudiante_service.crear_estudiante(
            "María García",
            "Maestría en Ingeniería de Software",
            2,
            "posgrado",
        ),
        estudiante_service.crear_estudiante(
            "Carlos López",
            "Ingeniería de Sistemas",
            3,
            "pregrado",
        ),
        estudiante_service.crear_estudiante(
            "Ana Martínez",
            "Ingeniería Industrial",
            6,
            "pregrado",
        ),
        estudiante_service.crear_estudiante(
            "Roberto Sánchez",
            "Doctorado en Ingeniería",
            1,
            "posgrado",
        ),
    ]
    print(f"✅ {len(estudiantes)} estudiantes creados\n")

    # Crear Préstamos
    print("📋 Creando préstamos de prueba...")
    hoy = date.today()

    # Préstamo activo normal
    prestamo1 = prestamo_service.crear_prestamo(
        estudiantes[0].id,
        ejemplares[0].id,
        fecha_prestamo=hoy - timedelta(days=5),
    )
    print(f"✅ Préstamo activo: {prestamo1.id}")

    # Préstamo activo de alta demanda
    prestamo2 = prestamo_service.crear_prestamo(
        estudiantes[1].id,
        ejemplares[3].id,  # Clean Code (alta demanda)
        fecha_prestamo=hoy - timedelta(days=2),
    )
    print(f"✅ Préstamo activo (alta demanda): {prestamo2.id}")

    # Préstamo con retraso (para testing de multas)
    prestamo3 = prestamo_service.crear_prestamo(
        estudiantes[2].id,
        ejemplares[1].id,
        fecha_prestamo=hoy - timedelta(days=20),
    )
    print(f"✅ Préstamo con retraso: {prestamo3.id}")

    print("\n" + "=" * 60)
    print("✅ DATOS DE PRUEBA CARGADOS EXITOSAMENTE")
    print("=" * 60)
    print("\nEndpoints útiles para probar:")
    print(f"  - GET /libros")
    print(f"  - GET /libros/disponibles")
    print(f"  - GET /estudiantes/{estudiantes[0].id}")
    print(f"  - GET /estudiantes/{estudiantes[0].id}/prestamos")
    print(f"  - GET /prestamos/vencidos")
    print("\nDatos de ejemplo:")
    print(f"  Estudiante ID: {estudiantes[0].id}")
    print(f"  Ejemplar ID: {ejemplares[0].id}")
    print(f"  Préstamo ID: {prestamo1.id}")


if __name__ == "__main__":
    seed_data()
