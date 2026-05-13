from app.models.entities import Libro, Ejemplar, Estudiante, Prestamo, Multa
from datetime import date


def test_crear_libro():
    """Test para crear una entidad Libro"""
    libro = Libro(
        id="LIB001",
        titulo="Python Avanzado",
        autor="Guido van Rossum",
        ubicacion="Piso 2",
        alta_demanda=False,
    )
    assert libro.id == "LIB001"
    assert libro.titulo == "Python Avanzado"
    assert libro.autor == "Guido van Rossum"
    assert libro.alta_demanda is False


def test_crear_ejemplar():
    """Test para crear una entidad Ejemplar"""
    ejemplar = Ejemplar(
        id="EJE001",
        libro_id="LIB001",
        estado="disponible",
    )
    assert ejemplar.id == "EJE001"
    assert ejemplar.libro_id == "LIB001"
    assert ejemplar.estado == "disponible"


def test_crear_estudiante():
    """Test para crear una entidad Estudiante"""
    estudiante = Estudiante(
        id="EST001",
        nombre="Juan Pérez",
        programa="Ingeniería de Sistemas",
        semestre=5,
        tipo="pregrado",
        multas_pendientes=0.0,
    )
    assert estudiante.id == "EST001"
    assert estudiante.nombre == "Juan Pérez"
    assert estudiante.tipo == "pregrado"
    assert estudiante.multas_pendientes == 0.0


def test_crear_prestamo():
    """Test para crear una entidad Préstamo"""
    prestamo = Prestamo(
        id="PRES001",
        estudiante_id="EST001",
        ejemplar_id="EJE001",
        fecha_prestamo=date(2026, 5, 1),
        fecha_devolucion_esperada=date(2026, 5, 16),
        estado="activo",
        renovado=False,
    )
    assert prestamo.id == "PRES001"
    assert prestamo.estado == "activo"
    assert prestamo.renovado is False
    assert prestamo.fecha_devolucion_real is None


def test_crear_multa():
    """Test para crear una entidad Multa"""
    multa = Multa(
        id="MULT001",
        estudiante_id="EST001",
        prestamo_id="PRES001",
        monto=4000.0,
        dias_retraso=2,
        pagada=False,
    )
    assert multa.id == "MULT001"
    assert multa.monto == 4000.0
    assert multa.dias_retraso == 2
    assert multa.pagada is False
