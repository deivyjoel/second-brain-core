from backend.application.use_cases.note_use_cases import (
    create_note, delete_note, get_note_details, get_note_analytics,
    get_notes_without_themes, list_notes_by_theme, move_to_theme,
    register_time_to_note, rename_note, update_note_content, get_unique_note_name,
    get_notes_descendants
)
from backend.application.use_cases.theme_use_cases import (
    create_theme, delete_theme, get_theme_analytics, get_theme_details, 
    list_child_themes, list_root_themes, list_themes, remove_theme, 
    rename_theme, get_unique_theme_name, get_themes_descendants
)

from backend.infrastructure.repositories.note_repository import NoteRepository
from backend.infrastructure.repositories.theme_repository import ThemeRepository
from backend.infrastructure.repositories.time_repository import TimeRepository
from backend.infrastructure.repositories.analytics_repository import AnalyticsRepository
from backend.infrastructure.repositories.search_efficiency_repository import SearchEfficiencyRepository

from backend.application.services.analyzer_services import AnalyzerService
from backend.application.services.note_services import NoteService
from backend.application.services.theme_services import ThemeService

class BackendAPI:
    """
    Fachada centralizada para el frontend.
    Coordina Repositorios y Servicios para alimentar los Casos de Uso.
    """

    def __init__(self, note_repo: NoteRepository, theme_repo: ThemeRepository, 
                 time_repo: TimeRepository, analy_repo: AnalyticsRepository,
                 search_repo: SearchEfficiencyRepository):
        # Repositorios
        self._note_repo = note_repo
        self._theme_repo = theme_repo
        self._time_repo = time_repo
        self._analy_repo = analy_repo
        self._search_repo = search_repo
        
        # Servicios (Inyectamos los repositorios necesarios)
        self._analyzer_service = AnalyzerService()
        self._note_service = NoteService(self._note_repo)
        self._theme_service = ThemeService(self._theme_repo)

    # --- Operaciones de Notas ---

    def create_note(self, name: str, theme_id: int | None = None):
        return create_note(self._note_repo, self._note_service, name, theme_id)

    def delete_note(self, note_id: int):
        return delete_note(self._note_repo, note_id)

    def rename_note(self, note_id: int, new_name: str):
        return rename_note(self._note_repo, self._note_service, note_id, new_name)

    def move_note_to_theme(self, note_id: int, new_theme_id: int | None = None):
        return move_to_theme(self._note_repo, self._theme_repo, self._note_service, note_id, new_theme_id)

    def update_note_content(self, note_id: int, content: str):
        return update_note_content(self._note_repo, note_id, content)

    def get_note_details(self, note_id: int):
        return get_note_details(self._note_repo, note_id)

    def get_note_analytics(self, note_id: int):
        return get_note_analytics(self._time_repo, self._note_repo, self._analyzer_service, note_id)

    def list_notes_by_theme(self, theme_id: int):
        return list_notes_by_theme(self._note_repo, self._theme_repo, theme_id)

    def get_notes_without_themes(self):
        return get_notes_without_themes(self._note_repo)

    def register_time_to_note(self, note_id: int, minutes: float):
        return register_time_to_note(self._note_repo, self._time_repo, minutes, note_id)
    
    def get_unique_note_name(self, name: str, theme_id: int | None = None):
        return get_unique_note_name(self._theme_repo, self._note_service, name, theme_id)
    
    def get_notes_descendants(self, theme_id: int):
        return get_notes_descendants(theme_id, self._search_repo)

    # --- Operaciones de Temas ---

    def create_theme(self, name: str, parent_id: int | None = None):
        return create_theme(self._theme_repo, self._theme_service, name, parent_id)

    def delete_theme(self, theme_id: int):
        return delete_theme(self._theme_repo, theme_id)

    def rename_theme(self, theme_id: int, new_name: str):
        return rename_theme(self._theme_repo, self._theme_service, theme_id, new_name)

    def remove_theme(self, theme_id: int, new_parent_id: int | None = None):
        return remove_theme(self._theme_repo, self._theme_service, theme_id, 
                            self._search_repo, new_parent_id)

    def get_unique_theme_name(self, name: str, theme_id: int | None = None):
        return get_unique_theme_name(self._theme_repo, self._theme_service, name, theme_id)

    def list_themes(self):
        return list_themes(self._theme_repo)

    def list_root_themes(self):
        return list_root_themes(self._theme_repo)

    def list_child_themes(self, parent_id: int):
        return list_child_themes(self._theme_repo, parent_id)

    def get_theme_details(self, theme_id: int):
        return get_theme_details(self._theme_repo, theme_id)

    def get_theme_analytics(self, theme_id: int):
        return get_theme_analytics(
            self._analy_repo,
            self._search_repo, 
            self._theme_repo, 
            self._analyzer_service, 
            theme_id
        )

    def get_themes_descendants(self, theme_id: int):
        return get_themes_descendants(theme_id, self._search_repo)