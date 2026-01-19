from log import logger
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from backend.infrastructure.repositories._image_storage import ImageStorage, ImageStorageError
from backend.infrastructure.repositories.sql_alchemy import models
from backend.infrastructure.errors.db import RepositoryError, UniqueConstraintViolation

from backend.domain.models.image import Image 
from backend.domain.dto.new_image_dto import NewImageDTO

class ImageRepository():
    def __init__(self, session):
        self.session = session
        self.image_store = ImageStorage()
        logger.info("ImageRepository initialized successfully: %s", session)

    def _to_domain(self, img: models.ImageModel) -> Image:
        return Image(
            id=img.id,
            name=img.name,
            file_path=img.file_path,
            theme_id=img.theme_id,
            created_at=img.created_at
        )

    # --- CRUD ---
    def add(self, image: NewImageDTO) -> int:
        file_path = None
        is_committed = False
        try:
            # 1. Save the file (errors will be captured)
            file_path = self.image_store.save(
                name=image.name,
                extension=image.extension,
                blob_data=image.blob_data
            )
            # 2. Add record to the database
            obj = models.ImageModel(
                name=image.name,
                file_path=file_path, 
                theme_id=image.theme_id
            )
            self.session.add(obj)
            self.session.commit()
            is_committed = True
            logger.info("add_image(id=%s) [Success]", obj.id)
            return obj.id

        except ImageStorageError as e:
            logger.exception("add_image(name=%s) [StorageError]: %s", image.name, e)
            raise RepositoryError("file_error") from e

        except IntegrityError as e:
            self.session.rollback()
            logger.exception("add_image(name=%s) [IntegrityError]: %s", image.name, e)
            raise UniqueConstraintViolation("unique_violation") from e
        
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.exception("add_image(name=%s) [SQLAlchemyError]: %s", image.name, e)
            raise RepositoryError("db_error") from e
        
        finally:
            """
            If file saving fails, there was never a possibility of a commit.
            An exception is simply raised.
            Otherwise, if file saving succeeds and the database operation fails,
            the previously saved file is deleted.
            """
            if not is_committed and file_path:
                self.image_store.undo_save(file_path)


    def delete(self, image_id: int) -> None:
        image_obj = self.session.get(models.ImageModel, image_id)
        if not image_obj:
            logger.warning("delete_image(id=%s) [Not found]", image_id)
            raise RepositoryError("not_found")
        moved = False
        is_commited = False
        try:
            # 1. Delete the file (errors will be captured)
            self.image_store.move_to_trash(image_obj.file_path)
            moved = True 
            
            # 2. Delete record in the database
            self.session.delete(image_obj)
            self.session.commit()
            is_commited = True

            logger.info("delete_image(id=%s) [Success]", image_id)

        except ImageStorageError as e:
            logger.exception("delete_image(id=%s) [StorageError]: %s", image_id, e)
            raise RepositoryError("file_error") from e
        
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.exception("delete_image(id=%s) [SQLAlchemyError]: %s", image_id, e)
            raise RepositoryError("db_error") from e
        
        except Exception as e:
            self.session.rollback()
            logger.exception("delete_image(id=%s) [Unexpected error]", image_id)
            raise RepositoryError("unexpected_error") from e
        
        finally:
            if not is_commited and moved:
                self.image_store.restore_from_trash(image_obj.file_path)


    def update(self, image: Image) -> None:
        image_obj = self.session.get(models.ImageModel, image._id)
        if not image_obj:
            logger.warning("update_image(id=%s) [Not found]", image._id)
            raise RepositoryError("not_found")

        image_obj.name = image._name
        image_obj.theme_id = image._theme_id

        try:
            self.session.commit()
            logger.info("update_image(id=%s) [Success]", image._id)

        except IntegrityError as e:
            self.session.rollback()
            logger.exception("update_image(id=%s) [IntegrityError]: %s", image._id, e)
            raise UniqueConstraintViolation("unique_violation") from e
        
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.exception("update_image(id=%s) [SQLAlchemyError]: %s", image._id, e)
            raise RepositoryError("db_error") from e

    def delete_many(self, image_ids: list[int]) -> None:
        if not image_ids:
            return

        moved_files = [] 
        is_commited = False
        
        try:
            stmt_select = select(models.ImageModel.file_path).where(models.ImageModel.id.in_(image_ids))
            file_paths = self.session.execute(stmt_select).scalars().all()
            moved_files = self.image_store.move_to_trash_many(file_paths)
            stmt_delete = delete(models.ImageModel).where(models.ImageModel.id.in_(image_ids))
            self.session.execute(stmt_delete)

            self.session.commit()
            is_commited = True
            
            logger.info("delete_many_images(ids=%s) [Success] - %d files moved to trash", image_ids, len(moved_files))

        except ImageStorageError as e:
            logger.exception("delete_many_images(ids=%s) [StorageError]: %s", image_ids, e)
            raise RepositoryError("file_error") from e
    
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.exception("delete_many_notes [SQLAlchemyError]: %s", e)
            raise RepositoryError("db_error") from e
        except Exception as e:
            self.session.rollback()
            logger.exception("delete_many_notes [Unexpected error]")
            raise RepositoryError("unexpected_error") from e
        finally:
            if not is_commited and moved_files:
                self.image_store.restore_many_from_trash([f for sublist in moved_files for f in sublist])
        
    # --- QUERIES ---
    def get_by_id(self, image_id: int) -> Image | None:
        try:
            obj = self.session.get(models.ImageModel, image_id)
            logger.info("get_image_by_id(id=%s) [Success]", image_id)
            return self._to_domain(obj) if obj else None
        
        except SQLAlchemyError as e:
            logger.exception("get_image_by_id(id=%s) [SQLAlchemyError]: %s", image_id, e)
            raise RepositoryError("db_error") from e
        
    def _query_images(self, **filters) -> list[Image]:
        try:
            objs = self.session.query(models.ImageModel).filter_by(**filters).all()
            logger.info("query_images(filters=%s) [Success] - %d images found", filters, len(objs))
            return [self._to_domain(obj) for obj in objs]
        
        except SQLAlchemyError as e:
            logger.exception("query_images(filters=%s) [SQLAlchemyError]: %s", filters, e)
            raise RepositoryError("db_error") from e

    def get_all_images(self):
        return self._query_images()

    def get_images_by_theme_id(self, theme_id: int):
        return self._query_images(theme_id=theme_id)

    def get_images_without_theme_id(self):
        return self._query_images(theme_id=None)