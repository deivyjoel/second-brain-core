from backend.application.backend_api import BackendAPI

class ApiProvider:
    """
    Service locator to centralize access to the backend.
    """
    _instance = None

    @classmethod
    def set(cls, api_instance: BackendAPI):
        """Store the backend instance to be used globally."""
        cls._instance = api_instance

    @classmethod
    def get(cls):
        """Retrieve the stored backend instance or raise an error if not set."""
        if cls._instance is None:
            raise Exception("ApiProvider: The API must be initialized before use (ApiProvider.set).")
        return cls._instance