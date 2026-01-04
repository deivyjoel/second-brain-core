from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from log import logger

from backend.infrastructure.repositories.sql_alchemy import models
from backend.infrastructure.errors.db import RepositoryError
from backend.infrastructure.dto.note_record_lite_dto import NoteRecordLiteDTO

class SearchEfficiencyRepository:
    def __init__(self, session: Session):
        self.session = session
        logger.info("SearchEfficiencyRepository initialized successfully")

    def get_notes_from_theme_and_descendants(self, theme_id: int) -> list[int]:
        print("theme_id es", theme_id)
        """Obtiene todas las notas de un tema y de todos sus subtemas recursivamente."""
        try:
            # Definir la jerarquía recursiva de temas
            hierarchy = (
                select(models.ThemeModel.id)
                .where(models.ThemeModel.id == theme_id)
                .cte(name="theme_hierarchy", recursive=True)
            )

            hierarchy = hierarchy.union_all(
                select(models.ThemeModel.id)
                .where(models.ThemeModel.parent_id == hierarchy.c.id)
            )

            # Consultar solo los IDs de notas vinculadas a esos temas
            stmt = select(models.NoteModel.id).where(
                models.NoteModel.theme_id.in_(select(hierarchy.c.id))
            )

            note_ids = self.session.execute(stmt).scalars().all()
            logger.info(
                "get_notes_from_theme_and_descendants(theme_id=%s) [Success] - %d notes found",
                theme_id,
                len(note_ids),
            )
            return list(note_ids)
        
        except SQLAlchemyError as e:
            logger.exception("get_notes_from_descendants(theme_id=%s) [SQLAlchemyError]: %s", theme_id, e)
            raise RepositoryError("db_error") from e
        except Exception as e:
            logger.exception("get_notes_from_descendants(theme_id=%s) [Unexpected error]", theme_id)
            raise RepositoryError("unexpected_error") from e

    def get_theme_descendants_ids(self, root_theme_id: int) -> list[int]:
        """Obtiene solo los IDs de todos los temas hijos/descendientes."""
        try:
            hierarchy = (
                select(models.ThemeModel.id)
                .where(models.ThemeModel.id == root_theme_id)
                .cte(recursive=True, name="theme_ids_hierarchy")
            )

            hierarchy = hierarchy.union_all(
                select(models.ThemeModel.id)
                .where(models.ThemeModel.parent_id == hierarchy.c.id)
            )

            stmt = select(hierarchy.c.id)
            ids = self.session.execute(stmt).scalars().all()
            
            logger.info("get_theme_descendants_ids(root_id=%s) [Success]", root_theme_id)
            return list(ids)

        except SQLAlchemyError as e:
            logger.exception("get_theme_descendants_ids(root_id=%s) [SQLAlchemyError]: %s", root_theme_id, e)
            raise RepositoryError("db_error") from e
        except Exception as e:
            logger.exception("get_theme_descendants_ids(root_id=%s) [Unexpected error]", root_theme_id)
            raise RepositoryError("unexpected_error") from e

