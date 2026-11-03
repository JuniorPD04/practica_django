class ErrorAPI(Exception):
    """Error esperado del dominio con su código de respuesta."""

    def __init__(self, mensaje, status=400):
        self.mensaje = mensaje
        self.status = status
