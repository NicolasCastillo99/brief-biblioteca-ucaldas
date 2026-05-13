class BibliotecaException(Exception):
    """Excepción base para el sistema de biblioteca"""
    pass


class ResourceNotFound(BibliotecaException):
    """Recurso no encontrado"""
    def __init__(self, resource: str, resource_id: str):
        self.message = f"{resource} con ID '{resource_id}' no encontrado"
        super().__init__(self.message)


class LimitePrestamosAlcanzado(BibliotecaException):
    """El estudiante ha alcanzado el límite de préstamos activos"""
    def __init__(self):
        self.message = "limite_prestamos_alcanzado"
        super().__init__(self.message)


class MultasPendientes(BibliotecaException):
    """El estudiante tiene multas pendientes"""
    def __init__(self):
        self.message = "multas_pendientes"
        super().__init__(self.message)


class PrestamosVencidos(BibliotecaException):
    """El estudiante tiene préstamos vencidos"""
    def __init__(self):
        self.message = "prestamos_vencidos"
        super().__init__(self.message)


class EjemplarNoDisponible(BibliotecaException):
    """El ejemplar no está disponible"""
    def __init__(self):
        self.message = "ejemplar_no_disponible"
        super().__init__(self.message)


class NoSePuedeRenovar(BibliotecaException):
    """No se puede renovar el préstamo"""
    def __init__(self):
        self.message = "no_se_puede_renovar"
        super().__init__(self.message)


class PrestamoNoActivo(BibliotecaException):
    """El préstamo no está en estado activo"""
    def __init__(self):
        self.message = "prestamo_no_activo"
        super().__init__(self.message)


class PrestamoYaDevuelto(BibliotecaException):
    """El préstamo ya ha sido devuelto"""
    def __init__(self):
        self.message = "prestamo_ya_devuelto"
        super().__init__(self.message)
