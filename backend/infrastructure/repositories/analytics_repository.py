from log import logger
from sqlalchemy import func, distinct
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from backend.infrastructure.repositories.sql_alchemy import models
from backend.infrastructure.errors.db import RepositoryError
from backend.infrastructure.dto.theme_raw_stats_dto import ThemeRawStatsDTO

class AnalyticsRepository:
    def __init__(self, session: Session):
        self.session = session
        logger.info("AnalyticsRepository initialized succesfully:: %s", session)

    def get_time_and_note_counts(self, family_theme_ids: list[int], theme_id: int) -> ThemeRawStatsDTO:
        """Retrieves aggregated time and note metrics for a specified list of themes."""
        try:
            result = (
                self.session.query(
                    func.count(distinct(models.NoteModel.id)).label("notes"),
                    func.coalesce(func.sum(models.TimeModel.minutes), 0).label("minutes"),
                    func.count(distinct(func.date(models.TimeModel.created_at))).label("days")
                )
                .select_from(models.NoteModel)
                .outerjoin(models.TimeModel, models.NoteModel.id == models.TimeModel.note_id)
                .filter(models.NoteModel.theme_id.in_(family_theme_ids))
                .first()
            )
            
            logger.info("get_time_and_note_counts(theme_id=%s) [Success]", theme_id)
            return ThemeRawStatsDTO(
                total_notes = result.notes if result else 0,
                minutes = result.minutes if result else 0,
                active_days = result.days if result else 0,
                n_subthemes = len(family_theme_ids) - 1
            )

        except SQLAlchemyError as e:
            logger.error("get_time_and_note_counts(id=%s) [SQLAlchemyError]: %s", theme_id, e)
            raise RepositoryError("db_error") from e
        except Exception as e:
            logger.exception("get_time_and_note_counts(id=%s) [Unexpected error]", theme_id)
            raise RepositoryError("unexpected_error") from e

    def count_direct_notes(self, theme_id: int) -> int:
        """Counts notes that pertain exclusively to the given theme."""
        try:
            count = (
                self.session.query(func.count(models.NoteModel.id))
                .filter(models.NoteModel.theme_id == theme_id)
                .scalar()
            )
            logger.info("count_direct_notes(theme_id=%s) [Success]", theme_id)
            return count or 0
        except SQLAlchemyError as e:
            logger.error("count_direct_notes(id=%s) [SQLAlchemyError]: %s", theme_id, e)
            raise RepositoryError("db_error") from e
        except Exception as e:
            logger.exception("count_direct_notes(id=%s) [Unexpected error]", theme_id)
            raise RepositoryError("unexpected_error") from e

    def get_aggregated_content(self, family_theme_ids: list[int], theme_id: int) -> str:
        """Retrieves the content for lexical analysis."""
        try:
            notes_content = (
                self.session.query(models.NoteModel.content)
                .filter(models.NoteModel.theme_id.in_(family_theme_ids))
                .all()
            )
            logger.info("get_aggregated_content(theme_id=%s) [Success]", theme_id)
            return " ".join([c[0] for c in notes_content if c[0]])
        except SQLAlchemyError as e:
            logger.error("get_aggregated_content(id=%s) [SQLAlchemyError]: %s", theme_id, e)
            raise RepositoryError("db_error") from e
        except Exception as e:
            logger.exception("get_aggregated_content(id=%s) [Unexpected error]", theme_id)
            raise RepositoryError("unexpected_error") from e