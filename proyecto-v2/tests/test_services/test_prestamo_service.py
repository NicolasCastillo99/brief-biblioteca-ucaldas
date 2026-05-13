import pytest
from datetime import date, timedelta
from app.services.prestamo_service import PrestamoService
from app.repositories.prestamo_repository import PrestamoRepository
from app.repositories.ejemplar_repository import EjemplarRepository
from app.repositories.libro_repository import LibroRepository
from app.repositories.estudiante_repository import EstudianteRepository
from app.repositories.multa_repository import MultaRepository
from app.models.entities import Libro, Ejemplar, Estudiante, Prestamo
from app.exceptions.custom_exceptions import (
    LimitePrestamosAlcanzado,
    MultasPendientes,
    PrestamosVencidos,
    EjemplarNoDisponible,
    PrestamoYaDevuelto,
    ResourceNotFound,
)


@pytest.fixture
def prestamo_service_with_repos():
    """Fixture de PrestamoService con repositorios"""
    prestamo_repo = PrestamoRepository()
    ejemplar_repo = EjemplarRepository()
    libro_repo = LibroRepository()
    estudiante_repo = EstudianteRepository()
    multa_repo = MultaRepository()

    return (
        PrestamoService(
            prestamo_repository=prestamo_repo,
            ejemplar_repository=ejemplar_repo,
            libro_repository=libro_repo,
            estudiante_repository=estudiante_repo,
            multa_repository=multa_repo,
        ),
        prestamo_repo,
        ejemplar_repo,
        libro_repo,
        estudiante_repo,
        multa_repo,
    )


class TestRN1_LimitePrestamos:
    """Tests para RN1: Límite de préstamos por estudiante"""

    def test_pregrado_puede_crear_3_prestamos(self, prestamo_service_with_repos):
        """Un estudiante de pregrado puede crear máximo 3 préstamos activos"""
        service, prestamo_repo, ejemplar_repo, libro_repo, estudiante_repo, multa_repo = (
            prestamo_service_with_repos
        )

        # Crear libro
        libro = Libro(
            id="LIB001",
            titulo="Test",
            autor="Test",
            ubicacion="Test",
            alta_demanda=False,
        )
        libro_repo.create(libro, libro.id)

        # Crear 3 ejemplares
        for i in range(3):
            ejemplar = Ejemplar(
                id=f"EJE00{i+1}",
                libro_id=libro.id,
                estado="disponible",
            )
            ejemplar_repo.create(ejemplar, ejemplar.id)

        # Crear estudiante pregrado
        estudiante = Estudiante(
            id="EST001",
            nombre="Test",
            programa="Test",
            semestre=5,
            tipo="pregrado",
            multas_pendientes=0.0,
        )
        estudiante_repo.create(estudiante, estudiante.id)

        # Crear 3 préstamos (debe funcionar)
        for i in range(3):
            prestamo = service.crear_prestamo("EST001", f"EJE00{i+1}")
            assert prestamo.estado == "activo"

        # Crear 4to préstamo (debe fallar)
        ejemplar4 = Ejemplar(
            id="EJE004",
            libro_id=libro.id,
            estado="disponible",
        )
        ejemplar_repo.create(ejemplar4, ejemplar4.id)

        with pytest.raises(LimitePrestamosAlcanzado):
            service.crear_prestamo("EST001", "EJE004")

    def test_posgrado_puede_crear_5_prestamos(self, prestamo_service_with_repos):
        """Un estudiante de posgrado puede crear máximo 5 préstamos activos"""
        service, prestamo_repo, ejemplar_repo, libro_repo, estudiante_repo, multa_repo = (
            prestamo_service_with_repos
        )

        # Crear libro
        libro = Libro(
            id="LIB002",
            titulo="Test",
            autor="Test",
            ubicacion="Test",
            alta_demanda=False,
        )
        libro_repo.create(libro, libro.id)

        # Crear 5 ejemplares
        for i in range(5):
            ejemplar = Ejemplar(
                id=f"EJE10{i+1}",
                libro_id=libro.id,
                estado="disponible",
            )
            ejemplar_repo.create(ejemplar, ejemplar.id)

        # Crear estudiante posgrado
        estudiante = Estudiante(
            id="EST002",
            nombre="Test",
            programa="Test",
            semestre=2,
            tipo="posgrado",
            multas_pendientes=0.0,
        )
        estudiante_repo.create(estudiante, estudiante.id)

        # Crear 5 préstamos (debe funcionar)
        for i in range(5):
            prestamo = service.crear_prestamo("EST002", f"EJE10{i+1}")
            assert prestamo.estado == "activo"

        # Crear 6to préstamo (debe fallar)
        ejemplar6 = Ejemplar(
            id="EJE106",
            libro_id=libro.id,
            estado="disponible",
        )
        ejemplar_repo.create(ejemplar6, ejemplar6.id)

        with pytest.raises(LimitePrestamosAlcanzado):
            service.crear_prestamo("EST002", "EJE106")


class TestRN2_MultasPendientes:
    """Tests para RN2: Bloqueo por multas pendientes"""

    def test_estudiante_con_multas_no_puede_prestar(
        self, prestamo_service_with_repos
    ):
        """Un estudiante con multas pendientes no puede crear préstamos"""
        service, prestamo_repo, ejemplar_repo, libro_repo, estudiante_repo, multa_repo = (
            prestamo_service_with_repos
        )

        # Crear libro y ejemplar
        libro = Libro(
            id="LIB003",
            titulo="Test",
            autor="Test",
            ubicacion="Test",
            alta_demanda=False,
        )
        libro_repo.create(libro, libro.id)

        ejemplar = Ejemplar(
            id="EJE201",
            libro_id=libro.id,
            estado="disponible",
        )
        ejemplar_repo.create(ejemplar, ejemplar.id)

        # Crear estudiante con multas
        estudiante = Estudiante(
            id="EST003",
            nombre="Test",
            programa="Test",
            semestre=5,
            tipo="pregrado",
            multas_pendientes=5000.0,  # Tiene multas
        )
        estudiante_repo.create(estudiante, estudiante.id)

        # Intentar crear préstamo (debe fallar)
        with pytest.raises(MultasPendientes):
            service.crear_prestamo("EST003", "EJE201")


class TestRN3_PrestamosVencidos:
    """Tests para RN3: Bloqueo por préstamos vencidos"""

    def test_estudiante_con_prestamos_vencidos_no_puede_prestar(
        self, prestamo_service_with_repos
    ):
        """Un estudiante con préstamos vencidos no puede crear préstamos"""
        service, prestamo_repo, ejemplar_repo, libro_repo, estudiante_repo, multa_repo = (
            prestamo_service_with_repos
        )

        # Crear libros y ejemplares
        for i in range(2):
            libro = Libro(
                id=f"LIB30{i+1}",
                titulo="Test",
                autor="Test",
                ubicacion="Test",
                alta_demanda=False,
            )
            libro_repo.create(libro, libro.id)

            ejemplar = Ejemplar(
                id=f"EJE30{i+1}",
                libro_id=libro.id,
                estado="disponible",
            )
            ejemplar_repo.create(ejemplar, ejemplar.id)

        # Crear estudiante
        estudiante = Estudiante(
            id="EST004",
            nombre="Test",
            programa="Test",
            semestre=5,
            tipo="pregrado",
            multas_pendientes=0.0,
        )
        estudiante_repo.create(estudiante, estudiante.id)

        # Crear préstamo vencido
        prestamo_vencido = Prestamo(
            id="PRES301",
            estudiante_id="EST004",
            ejemplar_id="EJE301",
            fecha_prestamo=date(2026, 1, 1),
            fecha_devolucion_esperada=date(2026, 1, 15),
            estado="vencido",
            renovado=False,
        )
        prestamo_repo.create(prestamo_vencido, prestamo_vencido.id)

        # Intentar crear nuevo préstamo (debe fallar)
        with pytest.raises(PrestamosVencidos):
            service.crear_prestamo("EST004", "EJE302")


class TestRN4_DisponibilidadEjemplar:
    """Tests para RN4: Disponibilidad de ejemplar"""

    def test_ejemplar_no_disponible_no_puede_ser_prestado(
        self, prestamo_service_with_repos
    ):
        """Un ejemplar no disponible no puede ser prestado"""
        service, prestamo_repo, ejemplar_repo, libro_repo, estudiante_repo, multa_repo = (
            prestamo_service_with_repos
        )

        # Crear libro
        libro = Libro(
            id="LIB004",
            titulo="Test",
            autor="Test",
            ubicacion="Test",
            alta_demanda=False,
        )
        libro_repo.create(libro, libro.id)

        # Crear ejemplar NO disponible
        ejemplar = Ejemplar(
            id="EJE401",
            libro_id=libro.id,
            estado="prestado",  # Ya prestado
        )
        ejemplar_repo.create(ejemplar, ejemplar.id)

        # Crear estudiante
        estudiante = Estudiante(
            id="EST005",
            nombre="Test",
            programa="Test",
            semestre=5,
            tipo="pregrado",
            multas_pendientes=0.0,
        )
        estudiante_repo.create(estudiante, estudiante.id)

        # Intentar crear préstamo (debe fallar)
        with pytest.raises(EjemplarNoDisponible):
            service.crear_prestamo("EST005", "EJE401")


class TestRN5_DuracionPrestamo:
    """Tests para RN5: Duración del préstamo"""

    def test_alta_demanda_prestamo_3_dias(self, prestamo_service_with_repos):
        """Un libro de alta demanda se presta por 3 días"""
        service, prestamo_repo, ejemplar_repo, libro_repo, estudiante_repo, multa_repo = (
            prestamo_service_with_repos
        )

        # Crear libro de alta demanda
        libro = Libro(
            id="LIB005",
            titulo="Test",
            autor="Test",
            ubicacion="Test",
            alta_demanda=True,  # Alta demanda
        )
        libro_repo.create(libro, libro.id)

        # Crear ejemplar
        ejemplar = Ejemplar(
            id="EJE501",
            libro_id=libro.id,
            estado="disponible",
        )
        ejemplar_repo.create(ejemplar, ejemplar.id)

        # Crear estudiante
        estudiante = Estudiante(
            id="EST006",
            nombre="Test",
            programa="Test",
            semestre=5,
            tipo="pregrado",
            multas_pendientes=0.0,
        )
        estudiante_repo.create(estudiante, estudiante.id)

        # Crear préstamo
        fecha_prestamo = date(2026, 5, 1)
        prestamo = service.crear_prestamo(
            "EST006", "EJE501", fecha_prestamo=fecha_prestamo
        )

        # Verificar fecha de devolución (3 días después)
        assert prestamo.fecha_devolucion_esperada == date(2026, 5, 4)

    def test_normal_prestamo_15_dias(self, prestamo_service_with_repos):
        """Un libro normal se presta por 15 días"""
        service, prestamo_repo, ejemplar_repo, libro_repo, estudiante_repo, multa_repo = (
            prestamo_service_with_repos
        )

        # Crear libro normal
        libro = Libro(
            id="LIB006",
            titulo="Test",
            autor="Test",
            ubicacion="Test",
            alta_demanda=False,  # Normal
        )
        libro_repo.create(libro, libro.id)

        # Crear ejemplar
        ejemplar = Ejemplar(
            id="EJE601",
            libro_id=libro.id,
            estado="disponible",
        )
        ejemplar_repo.create(ejemplar, ejemplar.id)

        # Crear estudiante
        estudiante = Estudiante(
            id="EST007",
            nombre="Test",
            programa="Test",
            semestre=5,
            tipo="pregrado",
            multas_pendientes=0.0,
        )
        estudiante_repo.create(estudiante, estudiante.id)

        # Crear préstamo
        fecha_prestamo = date(2026, 5, 1)
        prestamo = service.crear_prestamo(
            "EST007", "EJE601", fecha_prestamo=fecha_prestamo
        )

        # Verificar fecha de devolución (15 días después)
        assert prestamo.fecha_devolucion_esperada == date(2026, 5, 16)


class TestRN8_CalculoMultas:
    """Tests para RN8: Cálculo de multas por retraso"""

    def test_multa_por_retraso_calculada_correctamente(
        self, prestamo_service_with_repos
    ):
        """La multa se calcula correctamente: 2000 * días de retraso"""
        service, prestamo_repo, ejemplar_repo, libro_repo, estudiante_repo, multa_repo = (
            prestamo_service_with_repos
        )

        # Crear libro
        libro = Libro(
            id="LIB008",
            titulo="Test",
            autor="Test",
            ubicacion="Test",
            alta_demanda=False,
        )
        libro_repo.create(libro, libro.id)

        # Crear ejemplar
        ejemplar = Ejemplar(
            id="EJE801",
            libro_id=libro.id,
            estado="disponible",
        )
        ejemplar_repo.create(ejemplar, ejemplar.id)

        # Crear estudiante
        estudiante = Estudiante(
            id="EST008",
            nombre="Test",
            programa="Test",
            semestre=5,
            tipo="pregrado",
            multas_pendientes=0.0,
        )
        estudiante_repo.create(estudiante, estudiante.id)

        # Crear préstamo
        fecha_prestamo = date(2026, 5, 1)
        prestamo = service.crear_prestamo(
            "EST008", "EJE801", fecha_prestamo=fecha_prestamo
        )

        # Devolver con 2 días de retraso
        fecha_devolucion = date(2026, 5, 18)  # 2 días después de la fecha esperada (16)
        prestamo_devuelto = service.registrar_devolucion(
            prestamo.id, fecha_devolucion_real=fecha_devolucion
        )

        # Verificar que se creó la multa
        multa = multa_repo.get_by_prestamo_id(prestamo.id)
        assert multa is not None
        assert multa.monto == 4000.0  # 2000 * 2 días
        assert multa.dias_retraso == 2

    def test_sin_multa_si_devuelve_a_tiempo(self, prestamo_service_with_repos):
        """No se genera multa si se devuelve a tiempo"""
        service, prestamo_repo, ejemplar_repo, libro_repo, estudiante_repo, multa_repo = (
            prestamo_service_with_repos
        )

        # Crear libro
        libro = Libro(
            id="LIB009",
            titulo="Test",
            autor="Test",
            ubicacion="Test",
            alta_demanda=False,
        )
        libro_repo.create(libro, libro.id)

        # Crear ejemplar
        ejemplar = Ejemplar(
            id="EJE901",
            libro_id=libro.id,
            estado="disponible",
        )
        ejemplar_repo.create(ejemplar, ejemplar.id)

        # Crear estudiante
        estudiante = Estudiante(
            id="EST009",
            nombre="Test",
            programa="Test",
            semestre=5,
            tipo="pregrado",
            multas_pendientes=0.0,
        )
        estudiante_repo.create(estudiante, estudiante.id)

        # Crear préstamo
        fecha_prestamo = date(2026, 5, 1)
        prestamo = service.crear_prestamo(
            "EST009", "EJE901", fecha_prestamo=fecha_prestamo
        )

        # Devolver a tiempo
        fecha_devolucion = date(2026, 5, 15)  # Antes de la fecha esperada
        prestamo_devuelto = service.registrar_devolucion(
            prestamo.id, fecha_devolucion_real=fecha_devolucion
        )

        # Verificar que NO se creó multa
        multa = multa_repo.get_by_prestamo_id(prestamo.id)
        assert multa is None


class TestRN7_CambioEstadoEjemplar:
    """Tests para RN7: Control de un solo ejemplar prestado"""

    def test_ejemplar_cambia_a_prestado_al_crear_prestamo(
        self, prestamo_service_with_repos
    ):
        """El estado del ejemplar cambia a 'prestado' cuando se crea un préstamo"""
        service, prestamo_repo, ejemplar_repo, libro_repo, estudiante_repo, multa_repo = (
            prestamo_service_with_repos
        )

        # Crear libro
        libro = Libro(
            id="LIB0010",
            titulo="Test",
            autor="Test",
            ubicacion="Test",
            alta_demanda=False,
        )
        libro_repo.create(libro, libro.id)

        # Crear ejemplar disponible
        ejemplar = Ejemplar(
            id="EJE1001",
            libro_id=libro.id,
            estado="disponible",
        )
        ejemplar_repo.create(ejemplar, ejemplar.id)

        # Crear estudiante
        estudiante = Estudiante(
            id="EST0010",
            nombre="Test",
            programa="Test",
            semestre=5,
            tipo="pregrado",
            multas_pendientes=0.0,
        )
        estudiante_repo.create(estudiante, estudiante.id)

        # Crear préstamo
        prestamo = service.crear_prestamo("EST0010", "EJE1001")

        # Verificar que el ejemplar cambió a "prestado"
        ejemplar_actualizado = ejemplar_repo.get_by_id("EJE1001")
        assert ejemplar_actualizado.estado == "prestado"

    def test_ejemplar_vuelve_a_disponible_al_devolver(
        self, prestamo_service_with_repos
    ):
        """El estado del ejemplar vuelve a 'disponible' cuando se devuelve el libro"""
        service, prestamo_repo, ejemplar_repo, libro_repo, estudiante_repo, multa_repo = (
            prestamo_service_with_repos
        )

        # Crear libro
        libro = Libro(
            id="LIB0011",
            titulo="Test",
            autor="Test",
            ubicacion="Test",
            alta_demanda=False,
        )
        libro_repo.create(libro, libro.id)

        # Crear ejemplar
        ejemplar = Ejemplar(
            id="EJE1101",
            libro_id=libro.id,
            estado="disponible",
        )
        ejemplar_repo.create(ejemplar, ejemplar.id)

        # Crear estudiante
        estudiante = Estudiante(
            id="EST0011",
            nombre="Test",
            programa="Test",
            semestre=5,
            tipo="pregrado",
            multas_pendientes=0.0,
        )
        estudiante_repo.create(estudiante, estudiante.id)

        # Crear préstamo
        prestamo = service.crear_prestamo("EST0011", "EJE1101")
        assert ejemplar_repo.get_by_id("EJE1101").estado == "prestado"

        # Devolver
        service.registrar_devolucion(prestamo.id, fecha_devolucion_real=date.today())

        # Verificar que el ejemplar volvió a "disponible"
        ejemplar_actualizado = ejemplar_repo.get_by_id("EJE1101")
        assert ejemplar_actualizado.estado == "disponible"
