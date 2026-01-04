from backend.domain.errors.note_errors import (
    InvalidNoteNameError,
    DuplicateNoteNameError,
    InvalidMinutesError,
)
from backend.domain.dto.new_note_dto import NewNoteDTO   
from datetime import datetime



"""
Note on last_edited_at:
Updated only when the entity's core state changes (e.g., modifying content or adding minutes).
"""
class Note:
    __slots__ = ("_id", "_name", "_content", 
                 "_theme_id", "_minutes", "_last_edited_at", "_created_at")

    def __init__(
        self,
        id: int,
        name: str,
        content: str,
        minutes: float,
        last_edited_at : datetime,
        created_at: datetime,
        theme_id: int | None = None
    ):
        self._id = id
        self._name = name
        self._content = content
        self._theme_id = theme_id
        self._minutes = minutes
        self._last_edited_at = last_edited_at
        self._created_at = created_at


    # --- Helpers ---
    def _update_last_edit_time(self, now: datetime):
        self._last_edited_at = now
    
    # --- Creación ---
    @staticmethod
    def create(
        name: str,
        existing_names: set[str],
        theme_id: int | None = None,
    ) -> NewNoteDTO:
        #1. Se limpia espacios
        clean_name = name.strip()
        if not clean_name:
            raise InvalidNoteNameError("El nombre no puede estar vacío")
        
        normalized_existing = {n.strip().lower() for n in existing_names}

        if clean_name.lower() in normalized_existing:
            raise DuplicateNoteNameError("Ya existe una nota con ese nombre")

        return NewNoteDTO(
            name=name,
            theme_id=theme_id
        )

    # --- Cambios ---
    def change_name(self, new_name: str, existing_names: set[str]) -> None:
        new_name_clean = new_name.strip()

        if new_name_clean.lower() == self._name.strip().lower():
            return
        
        if not new_name_clean:
            raise InvalidNoteNameError("El nombre no puede estar vacío")

        normalized_existing = {n.strip().lower() for n in existing_names}
        if new_name_clean.lower() in normalized_existing:
            raise DuplicateNoteNameError("No puede haber dos notas con el mismo nombre")

        self._name = new_name_clean

    def change_theme_id(
        self,
        new_theme_id: int | None,
        existing_names: set[str]
    ) -> None:
        normalized_existing = {n.strip().lower() for n in existing_names}
        if self._name.lower() in normalized_existing:
            raise DuplicateNoteNameError()

        self._theme_id = new_theme_id

    # --- Contenido y tiempo ---
    def set_content(self, content: str, now: datetime) -> None:
        self._content = content
        #Update
        self._update_last_edit_time(now)

    def add_minutes(self, minutes: float, now: datetime) -> None:
        if minutes < 0:
            raise InvalidMinutesError("Minuto debe ser positivo")
        self._minutes += minutes
        self._update_last_edit_time(now)

    def set_minutes(self, minutes: float) -> None:
        if minutes < 0:
            raise InvalidMinutesError("Minuto debe ser positivo")
        self._minutes = minutes
