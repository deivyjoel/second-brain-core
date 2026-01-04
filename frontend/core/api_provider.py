from backend.application.backend_api import BackendAPI

class ApiProvider:
    """
    Service Locator para centralizar el acceso al backend/fachada.
    Evita el 'prop drilling' (pasar el backend por todos los constructores).
    """
    _instance = None

    @classmethod
    def set(cls, api_instance: BackendAPI):
        """Inyecta la instancia real del backend al inicio de la app."""
        cls._instance = api_instance

    @classmethod
    def get(cls):
        """Devuelve la instancia del backend."""
        if cls._instance is None:
            raise Exception("ApiProvider: Debes inicializar el API antes de usarlo (ApiProvider.set).")
        return cls._instance