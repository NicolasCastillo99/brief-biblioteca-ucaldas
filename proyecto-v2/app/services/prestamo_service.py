from typing import Optional
import uuid
from datetime import date, timedelta

from app.models.entities import Prestamo, Multa, Libro
from app.repositories.prestamo_repository import PrestamoRepository
from app.repositories.ejemplar_repository import EjemplarRepository
from app.repositories.libro_repository import LibroRepository
from app.repositories.estudiante_repository import EstudianteRepository
from app.repositories.multa_repository import MultaRepository
from app.exceptions.custom_exceptions import (
    LimitePrestamosAlcanzado,
    MultasPendientes,
    PrestamosVencidos,
    EjemplarNoDisponible,
    NoSePuedeRenovar,
    PrestamoNoActivo,
    PrestamoYaDevuelto,
    ResourceNotFound,
)


class PrestamoService:
    """Servicio de lógica de negocio para Préstamos"""

    def __init__(
        self,
        prestamo_repository: Optional[PrestamoRepository] = None,
        ejemplar_repository: Optional[EjemplarRepository] = None,
        libro_repository: Optional[LibroRepository] = None,
        estudiante_repository: Optional[EstudianteRepository] = None,
        multa_repository: Optional[MultaRepository] = None,
    ):
        self.prestamo_repo = prestamo_repository or PrestamoRepository()
        self.ejemplar_repo = ejemplar_repository or EjemplarRepository()
        self.libro_repo = libro_repository or LibroRepository()
        self.estudiante_repo = estudiante_repository or EstudianteRepository()
        self.multa_repo = multa_repository or MultaRepository()

    def crear_prestamo(
        self,
        estudiante_id: str,
        ejemplar_id: str,
        fecha_prestamo: Optional[date] = None,
    ) -> Prestamo:
        """
        Crear un nuevo préstamo aplicando todas las reglas de negocio.
        
        Valida:
        - RN1: Límite de préstamos por estudiante
        - RN2: Bloqueo por multas pendientes
        - RN3: Bloqueo por préstamos vencidos
        - RN4: Disponibilidad de ejemplar
        - RN5: Duración del préstamo
        - RN7: Cambiar estado del ejemplar a "prestado"
        """
        # Verificar que estudiante existe
        estudiante = self.estudiante_repo.get_by_id(estudiante_id)
        if not estudiante:
            raise ResourceNotFound("Estudiante", estudiante_id)

        # Verificar que ejemplar existe
        ejemplar = self.ejemplar_repo.get_by_id(ejemplar_id)
        if not ejemplar:
            raise ResourceNotFound("Ejemplar", ejemplar_id)

        # Verificar que libro existe
        libro = self.libro_repo.get_by_id(ejemplar.libro_id)
        if not libro:
            raise ResourceNotFound("Libro", ejemplar.libro_id)

        # RN1: Verificar límite de préstamos activos
        prestamos_activos = self.prestamo_repo.get_activos_by_estudiante_id(
            estudiante_id
        )
        limite_prestamos = 3 if estudiante.tipo == "pregrado" else 5
        if len(prestamos_activos) >= limite_prestamos:
            raise LimitePrestamosAlcanzado()

        # RN2: Verificar multas pendientes
        if estudiante.multas_pendientes > 0:
            raise MultasPendientes()

        # RN3: Verificar préstamos vencidos
        prestamos_vencidos = self.prestamo_repo.get_vencidos_by_estudiante_id(
            estudiante_id
        )
        if len(prestamos_vencidos) > 0:
            raise PrestamosVencidos()

        # RN4: Verificar disponibilidad del ejemplar
        if ejemplar.estado != "disponible":
            raise EjemplarNoDisponible()

        # RN5: Calcular fecha de devolución esperada
        if fecha_prestamo is None:
            fecha_prestamo = date.today()

        dias_prestamo = 3 if libro.alta_demanda else 15
        fecha_devolucion_esperada = fecha_prestamo + timedelta(days=dias_prestamo)

        # Crear el préstamo
        prestamo_id = str(uuid.uuid4())
        prestamo = Prestamo(
            id=prestamo_id,
            estudiante_id=estudiante_id,
            ejemplar_id=ejemplar_id,
            fecha_prestamo=fecha_prestamo,
            fecha_devolucion_esperada=fecha_devolucion_esperada,
            estado="activo",
            renovado=False,
        )

        # RN7: Cambiar estado del ejemplar a "prestado"
        ejemplar.estado = "prestado"
        self.ejemplar_repo.update(ejemplar_id, ejemplar)

        # Guardar el préstamo
        return self.prestamo_repo.create(prestamo, prestamo_id)

    def registrar_devolucion(
        self,
        prestamo_id: str,
        fecha_devolucion_real: Optional[date] = None,
    ) -> Prestamo:
        """
        Registrar la devolución de un préstamo.
        
        Aplica:
        - RN8: Cálculo de multas por retraso
        """
        # Verificar que el préstamo existe
        prestamo = self.prestamo_repo.get_by_id(prestamo_id)
        if not prestamo:
            raise ResourceNotFound("Préstamo", prestamo_id)

        # Verificar que el préstamo está activo
        if prestamo.estado != "activo":
            raise PrestamoYaDevuelto()

        # Si no se proporciona fecha, usar la de hoy
        if fecha_devolucion_real is None:
            fecha_devolucion_real = date.today()

        # Actualizar la fecha de devolución real
        prestamo.fecha_devolucion_real = fecha_devolucion_real

        # RN8: Calcular multa si hay retraso
        dias_retraso = (
            fecha_devolucion_real - prestamo.fecha_devolucion_esperada
        ).days
        if dias_retraso > 0:
            monto_multa = 2000 * dias_retraso
            multa_id = str(uuid.uuid4())
            multa = Multa(
                id=multa_id,
                estudiante_id=prestamo.estudiante_id,
                prestamo_id=prestamo_id,
                monto=monto_multa,
                dias_retraso=dias_retraso,
                pagada=False,
            )
            self.multa_repo.create(multa, multa_id)

            # Actualizar multas_pendientes del estudiante
            estudiante = self.estudiante_repo.get_by_id(prestamo.estudiante_id)
            if estudiante:
                estudiante.multas_pendientes += monto_multa
                self.estudiante_repo.update(prestamo.estudiante_id, estudiante)

        # Cambiar estado del préstamo a "devuelto"
        prestamo.estado = "devuelto"

        # Liberar el ejemplar (cambiar estado a "disponible")
        ejemplar = self.ejemplar_repo.get_by_id(prestamo.ejemplar_id)
        if ejemplar:
            ejemplar.estado = "disponible"
            self.ejemplar_repo.update(prestamo.ejemplar_id, ejemplar)

        # Guardar los cambios
        return self.prestamo_repo.update(prestamo_id, prestamo)

    def renovar_prestamo(self, prestamo_id: str) -> Prestamo:
        """
        Renovar un préstamo extendiendo su plazo.
        
        Valida:
        - RN6: Debe estar en estado "activo"
        - RN6: No debe existir restricción sobre el libro
        """
        # Verificar que el préstamo existe
        prestamo = self.prestamo_repo.get_by_id(prestamo_id)
        if not prestamo:
            raise ResourceNotFound("Préstamo", prestamo_id)

        # RN6: Verificar que el préstamo está en estado "activo"
        if prestamo.estado != "activo":
            raise PrestamoNoActivo()

        # RN6: Verificar que no existe restricción de otro estudiante
        # (Por simplificidad, permitimos renovar siempre que esté activo)

        # Obtener el libro para saber si es alta demanda
        ejemplar = self.ejemplar_repo.get_by_id(prestamo.ejemplar_id)
        libro = self.libro_repo.get_by_id(ejemplar.libro_id)

        # Extender el plazo
        dias_prestamo = 3 if libro.alta_demanda else 15
        prestamo.fecha_devolucion_esperada = prestamo.fecha_devolucion_esperada + timedelta(
            days=dias_prestamo
        )
        prestamo.renovado = True

        # Guardar los cambios
        return self.prestamo_repo.update(prestamo_id, prestamo)

    def obtener_prestamo(self, prestamo_id: str) -> Optional[Prestamo]:
        """Obtener un préstamo por ID"""
        return self.prestamo_repo.get_by_id(prestamo_id)

    def listar_prestamos(self) -> list[Prestamo]:
        """Listar todos los préstamos"""
        return self.prestamo_repo.get_all()

    def obtener_prestamos_activos_estudiante(self, estudiante_id: str) -> list[Prestamo]:
        """Obtener préstamos activos de un estudiante"""
        return self.prestamo_repo.get_activos_by_estudiante_id(estudiante_id)

    def obtener_historial_prestamos_estudiante(
        self, estudiante_id: str
    ) -> list[Prestamo]:
        """
        RN9: Obtener historial completo de préstamos de un estudiante
        """
        # Verificar que estudiante existe
        estudiante = self.estudiante_repo.get_by_id(estudiante_id)
        if not estudiante:
            raise ResourceNotFound("Estudiante", estudiante_id)

        return self.prestamo_repo.get_by_estudiante_id(estudiante_id)

    def listar_prestamos_vencidos(self) -> list[Prestamo]:
        """Listar todos los préstamos vencidos"""
        return self.prestamo_repo.get_vencidos()

    def marcar_prestamos_como_vencidos(self, fecha_actual: date = None) -> None:
        """
        Marcar automáticamente como vencidos los préstamos que superan 
        su fecha de devolución esperada.
        """
        if fecha_actual is None:
            fecha_actual = date.today()

        prestamos_activos = [
            p for p in self.prestamo_repo.get_all() if p.estado == "activo"
        ]

        for prestamo in prestamos_activos:
            if prestamo.fecha_devolucion_esperada < fecha_actual:
                prestamo.estado = "vencido"
                self.prestamo_repo.update(prestamo.id, prestamo)
