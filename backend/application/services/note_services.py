from backend.infrastructure.repositories.note_repository import NoteRepository
from backend.application.services.utils import generate_unique_name 

class NoteService:
    def __init__(self, note_repo: NoteRepository):
        self.note_repo = note_repo

    def exists(self, note_id: int) -> bool:
        return self.note_repo.get_by_id(note_id) is not None

    def get_unique_name_for_theme(self, base_name: str, theme_id: int | None = None) -> str:
        """
        Obtiene un nombre único (ej: "Nota (2)") basado en los nombres 
        que ya existen dentro de un tema específico.
        """

        if theme_id:
            notes = self.note_repo.get_notes_by_theme_id(theme_id)
        else:
            notes = self.note_repo.get_notes_without_theme_id()
        
        existing_names = [n.name for n in notes]
        
        return generate_unique_name(base_name, existing_names)
    
    def get_names_in_theme_id(self, theme_id: int | None = None) -> list[str]:
        notes = self.note_repo.get_notes_by_theme_id(theme_id) if theme_id else self.note_repo.get_notes_without_theme_id()
        return [n.name for n in notes if notes]
