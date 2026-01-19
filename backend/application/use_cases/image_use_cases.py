import os

from backend.infrastructure.repositories.image_repository import ImageRepository
from backend.infrastructure.repositories.theme_repository import ThemeRepository
from backend.infrastructure.repositories.search_efficiency_repository import SearchEfficiencyRepository

from backend.application.decorators.usecase_guard import handle_usecase_errors
from backend.application.results.operation_result import OperationResult
from backend.application.dto.image_summary_dto import ImageSummaryDTO
from backend.application.dto.image_detail_dto import ImageDetailDTO
from backend.application.services.image_services import ImageService 

from backend.domain.models.image import Image
from backend.domain.dto.new_image_dto import NewImageDTO

# --- OPERATIONS ---
@handle_usecase_errors
def create_image(image_repo: ImageRepository, 
                 image_services: ImageService,
                 name: str, 
                 blob_data: bytes,
                 extension: str,
                 theme_id: int | None = None
                 ) -> OperationResult[int]:
    sibling_names = image_services.get_names_in_theme_id(theme_id)
    image_dto: NewImageDTO = Image.create(name, blob_data, set(sibling_names), extension, theme_id)
    image_id = image_repo.add(image_dto)
    
    return OperationResult(True, "Imagen guardada exitosamente", image_id)

@handle_usecase_errors
def delete_many_images(image_repo: ImageRepository, image_ids: list[int]) -> OperationResult[None]:
    image_repo.delete_many(image_ids)
    return OperationResult(True, "Imágenes eliminadas correctamente", None)

@handle_usecase_errors
def delete_image(image_repo: ImageRepository, image_id: int) -> OperationResult[None]:
    image = image_repo.get_by_id(image_id)
    if not image:
        return OperationResult(False, "La imagen no existe", None)
    
    image_repo.delete(image_id)
    return OperationResult(True, "Imagen eliminada correctamente", None)

@handle_usecase_errors
def rename_image(image_repo: ImageRepository, 
                 image_service: ImageService,
                 image_id: int, 
                 new_name: str) -> OperationResult[None]:
    image = image_repo.get_by_id(image_id)
    if not image:
        return OperationResult(False, "Imagen no encontrada", None)
    
    sibling_names = image_service.get_names_in_theme_id(image._theme_id)
    image.change_name(new_name, set(sibling_names))
    image_repo.update(image) 
    return OperationResult(True, "Imagen renombrada exitosamente", None)

@handle_usecase_errors
def move_image_to_theme(image_repo: ImageRepository, 
                        theme_repo: ThemeRepository,
                        image_service: ImageService,
                        image_id: int, 
                        new_theme_id: int | None = None) -> OperationResult[None]:
    image = image_repo.get_by_id(image_id)
    if not image:
        return OperationResult(False, "Imagen no encontrada", None)
    
    if new_theme_id is not None:
        if not theme_repo.get_by_id(new_theme_id):
            return OperationResult(False, "El tema destino no existe", None)
    
    sibling_names = image_service.get_names_in_theme_id(new_theme_id)
    image.change_theme_id(new_theme_id, set(sibling_names))
    image_repo.update(image)
    return OperationResult(True, "Imagen movida exitosamente", None)

# ------ QUERIES -----
@handle_usecase_errors
def get_image_details(image_repo: ImageRepository, image_id: int) -> OperationResult[ImageDetailDTO]:
    """Trae la imagen completa con sus bytes (blob_data)."""
    image = image_repo.get_by_id(image_id)
    if not image:
        return OperationResult(False, "Imagen no encontrada", None)
    
    image_dto = ImageDetailDTO(
        id = image._id, 
        name = image._name,
        file_path = image._file_path, 
        theme_id = image._theme_id,
        created_at = image._created_at
    )

    return OperationResult(True, "Datos de imagen obtenidos", image_dto)

@handle_usecase_errors
def list_images_by_theme(image_repo: ImageRepository, theme_id: int) -> OperationResult[list[ImageSummaryDTO]]:
    """Lista imágenes de forma ligera (solo ID y Nombre)."""
    images = image_repo.get_images_by_theme_id(theme_id)
    
    images_dto = [ImageSummaryDTO(
            id=image._id,
            name = image._name
    ) for image in images]
    
    return OperationResult(True, "Imágenes listadas", images_dto)

@handle_usecase_errors
def get_unique_image_name(
                    theme_repo: ThemeRepository,
                    image_service: ImageService,
                    name: str, theme_id: int | None = None) -> OperationResult[str]:
    if theme_id:
        theme = theme_repo.get_by_id(theme_id)
        if not theme:
            return OperationResult(False, "No se pudo obtener un unico nombre para una imagen porque el tema dado no existe", None)
    u_name = image_service.get_unique_name_for_theme(name, theme_id)
    return OperationResult(True, "", u_name)

@handle_usecase_errors
def list_images_without_theme(image_repo: ImageRepository) -> OperationResult[list[ImageSummaryDTO]]:
    images = image_repo.get_images_without_theme_id()
    
    images_dto = [ImageSummaryDTO(
            id=image._id,
            name = image._name
    ) for image in images]
    
    return OperationResult(True, "Imágenes en raíz listadas", images_dto)


@handle_usecase_errors
def get_image_extension(image_repo: ImageRepository, image_id: int) -> OperationResult[str]:
    image = image_repo.get_by_id(image_id)
    if not image:
        return OperationResult(False, "Imagen no encontrada", None)
    
    _, extension = os.path.splitext(image._file_path)
    
    if not extension:
        return OperationResult(False, "El registro no tiene una extensión válida", None)

    clean_ext = extension.lstrip('.').lower()
    
    return OperationResult(True, "Extensión obtenida", clean_ext)


@handle_usecase_errors
def get_image_ids_by_theme_hierarchy(theme_id: int, search_repo: SearchEfficiencyRepository) -> OperationResult[list[int]]:
    ids_images = search_repo.get_images_from_theme_and_descendants(theme_id)
    return OperationResult(True, "", ids_images)