from backend.domain.errors.theme_errors import (
    InvalidThemeNameError,
    DuplicateThemeNameError,
    InvalidThemeHierarchyError,
)

from backend.domain.dto.new_theme_dto import NewThemeDTO
from datetime import datetime



"""
Theme on last_edited_at:
Updated only when the entity's core state changes (e.g., modifying name).
"""
class Theme:
    __slots__ = ("_id", "_name", "_parent_id", "_last_edited_at", 
                 "_created_at")

    def __init__(self, id: int, name: str, parent_id: int | None, 
                 last_edited_at: datetime,
                 created_at: datetime):
        self._id = id
        self._name = name
        self._parent_id = parent_id
        self._last_edited_at = last_edited_at
        self._created_at = created_at


    # --- Helpers ---
    def _update_last_edit_time(self, now: datetime):
        self._last_edited_at = now
        
    # --- Creación ---
    @staticmethod
    def create(
        name: str,
        sibling_names: set[str],
        parent_id: int | None = None,
    ) -> NewThemeDTO:
        clean_name = name.strip()
        if not clean_name:
            raise InvalidThemeNameError("El nombre no puede estar vacío")
        
        normalized_existing = {n.strip().lower() for n in sibling_names}

        if clean_name.lower() in normalized_existing:
            raise DuplicateThemeNameError("Ya existe un tema con ese nombre")

        return NewThemeDTO(
            name=name,
            parent_id=parent_id
        )

    # --- Cambios ---
    def change_name(self, new_name: str, sibling_names: set[str], now: datetime) -> None:
        new_name_clean = new_name.strip()

        if new_name_clean.lower() == self._name.strip().lower():
            return
        
        if not new_name_clean:
            raise InvalidThemeNameError("El nombre no puede estar vacío")
        
        normalized_existing = {n.strip().lower() for n in sibling_names}

        if new_name_clean.lower() in normalized_existing:
            raise DuplicateThemeNameError("No puede haber dos notas con el mismo nombre")

        self._name = new_name
        self._update_last_edit_time(now)

    def change_parent_id(
        self,
        new_parent_id: int | None,
        sibling_names: set[str],
        descendants_ids: set[int]
    ) -> None:
        normalized_existing = {n.strip().lower() for n in sibling_names}

        if self._name.lower() in normalized_existing:
            raise DuplicateThemeNameError("Ya existe un tema con ese nombre")

        if new_parent_id == self._id:
            raise InvalidThemeHierarchyError(
                "Un tema no puede ser su propio padre"
            )

        if new_parent_id in descendants_ids:
            raise InvalidThemeHierarchyError(
                "No puedes mover un tema dentro de uno de sus descendientes"
            )

        self._parent_id = new_parent_id

