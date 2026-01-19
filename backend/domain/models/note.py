from datetime import datetime

from backend.domain.errors.note_errors import (
    InvalidNoteNameError,
    DuplicateNoteNameError,
    InvalidMinutesError,
)
from backend.domain.dto.new_note_dto import NewNoteDTO   



class Note:
    __slots__ = ("_id", "_name", "_content", 
                 "_theme_id", "_minutes", "_last_edited_at", "_created_at",
                 "_new_times")

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
    
    # --- Creation ---
    @staticmethod
    def create(
        name: str,
        sibling_names: set[str],
        theme_id: int | None = None,
    ) -> NewNoteDTO:
        clean_name = name.strip()
        if not clean_name:
            raise InvalidNoteNameError("El nombre no puede estar vacío")
        
        normalized_sib_names = {n.strip().lower() for n in sibling_names}

        if clean_name.lower() in normalized_sib_names:
            raise DuplicateNoteNameError("Ya existe una nota con ese nombre en este tema")

        return NewNoteDTO(
            name=name,
            theme_id=theme_id
        ) # RETURN DTO

    # --- Changes ---
    def change_name(self, new_name: str, sibling_names: set[str]) -> None:
        new_name_clean = new_name.strip()

        if new_name_clean.lower() == self._name.strip().lower():
            return
        
        if not new_name_clean:
            raise InvalidNoteNameError("El nombre no puede estar vacío")

        normalized_sib_names = {n.strip().lower() for n in sibling_names}
        if new_name_clean.lower() in normalized_sib_names:
            raise DuplicateNoteNameError("Ya existe una nota con ese nombre en este tema")

        self._name = new_name_clean

    def change_theme_id(
        self,
        new_theme_id: int | None,
        sibling_names: set[str]
    ) -> None:
        normalized_sib_names = {n.strip().lower() for n in sibling_names}
        if self._name.lower() in normalized_sib_names:
            raise DuplicateNoteNameError("Ya existe una nota con este nombre en el tema destino")

        self._theme_id = new_theme_id

    # --- Content and minutes
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

"""
Note on last_edited_at:
Updated only when the entity's core state changes (e.g., modifying content or adding minutes).
"""