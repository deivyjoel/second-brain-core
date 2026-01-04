from backend.infrastructure.repositories.theme_repository import ThemeRepository
from backend.application.services.utils import generate_unique_name 

class ThemeService:
    def __init__(self, theme_repo: ThemeRepository):
        self.theme_repo = theme_repo

    def exists(self, theme_id: int) -> bool:
        """Verifica si un tema existe."""
        return self.theme_repo.get_by_id(theme_id) is not None

    def get_unique_name_for_theme(self, base_name: str, theme_id: int | None = None) -> str:
        """
        Obtiene un nombre único (ej: "Nota (2)") basado en los nombres 
        que ya existen dentro de un tema específico.
        """
        if theme_id:
            themes = self.theme_repo.get_themes_by_parent_id(theme_id)
        else:
            themes = self.theme_repo.get_themes_without_parent_id()
        
        existing_names = [t._name for t in themes]

        return generate_unique_name(base_name, existing_names)
    
    def get_names_in_theme_id(self, theme_id: int | None = None) -> list[str]:
        themes = self.theme_repo.get_themes_by_parent_id(theme_id) if theme_id else self.theme_repo.get_themes_without_parent_id()
        return [t._name for t in themes if themes]