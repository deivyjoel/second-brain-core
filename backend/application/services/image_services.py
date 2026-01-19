from backend.infrastructure.repositories.image_repository import ImageRepository

from backend.application.services.utils import generate_unique_name 

class ImageService:
    def __init__(self, image_repo: ImageRepository):
        self.image_repo = image_repo

    def exists(self, image_id: int) -> bool:
        return self.image_repo.get_by_id(image_id) is not None

    def get_unique_name_for_theme(self, base_name: str, theme_id: int | None = None) -> str:
        if theme_id:
            images = self.image_repo.get_images_by_theme_id(theme_id)
        else:
            images = self.image_repo.get_images_without_theme_id() 
        
        sibling_names = [img._name for img in images]
        
        return generate_unique_name(base_name, sibling_names)
    
    def get_names_in_theme_id(self, theme_id: int | None = None) -> list[str]:
        if theme_id:
            images = self.image_repo.get_images_by_theme_id(theme_id)
        else:
            images = self.image_repo.get_images_without_theme_id()
            
        return [img._name for img in images] if images else []