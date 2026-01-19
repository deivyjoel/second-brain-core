from datetime import datetime

from backend.domain.errors.image_errors import (
    InvalidImageNameError,
    DuplicateImageNameError,
    InvalidImageExtensionError
)
from backend.domain.dto.new_image_dto import NewImageDTO 

class Image:
    __slots__ = ("_id", "_name", "_file_path", "_theme_id", "_created_at")

    def __init__(
        self,
        id: int,
        name: str,
        file_path: str,
        created_at: datetime,
        theme_id: int | None = None
    ):
        self._id = id
        self._name = name
        self._file_path = file_path
        self._theme_id = theme_id
        self._created_at = created_at

    # --- Creation ---
    @staticmethod
    def create(
        name: str,
        blob_data: bytes,
        sibling_names: set[str],
        extension: str,
        theme_id: int | None = None,
    ) -> NewImageDTO:
        clean_name = name.strip()
        extension_clean = extension.strip().lower()
        if not clean_name:
            raise InvalidImageNameError("El nombre de la imagen no puede estar vacío")
        
        normalized_sib_names = {n.strip().lower() for n in sibling_names}
        if clean_name.lower() in normalized_sib_names:
            raise DuplicateImageNameError("Ya existe una imagen con ese nombre en este tema")

        if extension_clean not in ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp']:
            raise InvalidImageExtensionError("Extensión de imagen no soportada")

        return NewImageDTO(
            name=clean_name,
            blob_data=blob_data,
            extension=extension_clean,
            theme_id=theme_id
        ) #RETURN DTO

    # --- Changes ---
    def change_name(self, new_name: str, sibling_names: set[str]) -> None:
        new_name_clean = new_name.strip()

        if new_name_clean.lower() == self._name.lower():
            return
        
        if not new_name_clean:
            raise InvalidImageNameError("El nombre no puede estar vacío")

        normalized_sib_names = {n.strip().lower() for n in sibling_names}
        if new_name_clean.lower() in normalized_sib_names:
            raise DuplicateImageNameError("Ya existe una imagen con ese nombre en este tema")

        self._name = new_name_clean

    def change_theme_id(
        self,
        new_theme_id: int | None,
        sibling_names: set[str]
    ) -> None:
        normalized_sib_names = {n.strip().lower() for n in sibling_names}
        if self._name.lower() in normalized_sib_names:
            raise DuplicateImageNameError("Ya existe una imagen con este nombre en el tema destino")

        self._theme_id = new_theme_id