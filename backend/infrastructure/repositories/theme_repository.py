from log import logger
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import delete

from backend.infrastructure.repositories.sql_alchemy import models
from backend.infrastructure.errors.db import RepositoryError, UniqueConstraintViolation

from backend.domain.models.theme import Theme
from backend.domain.dto.new_theme_dto import NewThemeDTO


class ThemeRepository():
    def __init__(self, session):
        self.session = session
        logger.info("ThemeRepository initialized succesfully: %s", session)

    def _to_domain(self, obj: models.ThemeModel) -> Theme:
        """Converts database model to domain entity."""
        return Theme(
            id = obj.id,
            name = obj.name,
            parent_id = obj.parent_id,
            created_at = obj.created_at,
            last_edited_at = obj.last_edited_at
        )
    
    # --- CRUD ---
    def add(self, theme: NewThemeDTO) -> int:
        obj = models.ThemeModel(
            name=theme.name, 
            parent_id=theme.parent_id,
            )
        try:
            self.session.add(obj)
            self.session.commit()
            logger.info("add_theme(id=%s) [Success]", obj.id)
            return obj.id
        except IntegrityError as e:
            self.session.rollback()
            logger.exception("add_theme(name=%s) [IntegrityError - Possible duplicate]: %s", theme.name, e)
            raise UniqueConstraintViolation("unique_violation") from e
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.exception("add_theme(name=%s) [SQLAlchemyError]: %s", theme.name, e)
            raise RepositoryError("db_error") from e
        except Exception as e:
            self.session.rollback()
            logger.exception("add_theme(name=%s) [Unexpected error]", theme.name)
            raise RepositoryError("unexpected_error") from e
        
    def delete(self, theme_id: int) -> None:
        theme_obj = self.session.get(models.ThemeModel, theme_id)
        if not theme_obj:
            logger.warning("delete_theme(id=%s) [Not Found]", theme_id)
            raise RepositoryError("not_found")
        try:
            self.session.delete(theme_obj)
            self.session.commit()
            logger.info("delete_theme(id=%s) [Success]", theme_id)
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.exception("delete_theme(id=%s) [SQLAlchemyError]: %s", theme_id, e)
            raise RepositoryError("db_error") from e
        except Exception as e:
            self.session.rollback()
            logger.exception("delete_theme(id=%s) [Unexpected error]", theme_id)
            raise RepositoryError("unexpected_error") from e

    def update(self, theme: Theme) -> None:
        theme_obj = self.session.get(models.ThemeModel, theme._id)
        if not theme_obj:
            logger.warning("update_theme(id=%s) [Not Found]", theme._id)
            raise RepositoryError("not_found")

        theme_obj.name = theme._name
        theme_obj.parent_id = theme._parent_id
        theme_obj.last_edited_at = theme._last_edited_at

        try:
            self.session.commit()
            logger.info("update_theme(id=%s) [Success]", theme._id)
        except IntegrityError as e:
            self.session.rollback()
            logger.exception("update_theme(id=%s) [IntegrityError]: %s", theme._id, e)
            raise UniqueConstraintViolation("unique_violation") from e
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.exception("update_theme(id=%s) [SQLAlchemyError]: %s", theme._id, e)
            raise RepositoryError("db_error") from e
        except Exception as e:
            self.session.rollback()
            logger.exception("update_theme(id=%s) [Unexpected error]", theme._id)
            raise RepositoryError("unexpected_error") from e

    def delete_many(self, theme_ids: list[int]) -> None:
        """Delete multiple themes at once."""
        if not theme_ids: return

        try:
            stmt = delete(models.ThemeModel).where(models.ThemeModel.id.in_(theme_ids))
            self.session.execute(stmt)
            self.session.commit()
            logger.info("delete_many_themes(ids=%s) [Success]", theme_ids)
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.exception("delete_many_themes [SQLAlchemyError]: %s", e)
            raise RepositoryError("db_error") from e
        except Exception as e:
            self.session.rollback()
            logger.exception("delete_many_themes [Unexpected error]")
            raise RepositoryError("unexpected_error") from e
        
    # --- QUERIES ---
    def get_by_id(self, theme_id: int) -> Theme | None:
        try:
            obj = self.session.get(models.ThemeModel, theme_id)
            logger.info("get_theme_by_id(id=%s) [Success]", theme_id)
            return self._to_domain(obj) if obj else None
        except SQLAlchemyError as e:
            logger.exception("get_theme_by_id(theme_id=%s) [SQLAlchemyError]: %s", theme_id, e)
            raise RepositoryError("db_error") from e
        except Exception as e:
            self.session.rollback()
            logger.exception("get_theme_by_id(theme_id=%s) [Unexpected error]", theme_id)
            raise RepositoryError("unexpected_error") from e
        
    def _query_themes(self, **filters) -> list[Theme]:
        try:
            objs = self.session.query(models.ThemeModel).filter_by(**filters).all()
            logger.info("query_themes(filters=%s) [Success] - %d themes found", filters, len(objs))
            return [self._to_domain(obj) for obj in objs]
        except SQLAlchemyError as e:
            logger.exception("query_themes(filters=%s) [SQLAlchemyError]: %s", filters, e)
            raise RepositoryError("db_error") from e
        except Exception as e:
            self.session.rollback()
            logger.exception("query_themes(filters=%s) [Unexpected error]", filters)
            raise RepositoryError("unexpected_error") from e

    def get_all_themes(self) -> list[Theme]:
        return self._query_themes()

    def get_themes_by_parent_id(self, theme_id: int) -> list[Theme]:
        return self._query_themes(parent_id=theme_id)

    def get_themes_without_parent_id(self) -> list[Theme]:
        return self._query_themes(parent_id = None)