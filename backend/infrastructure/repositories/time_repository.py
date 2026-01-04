from log import logger
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import func
from backend.infrastructure.repositories.sql_alchemy import models
from backend.infrastructure.errors.db import RepositoryError, UniqueConstraintViolation


class TimeRepository:
    def __init__(self, session):
        self.session = session
        logger.info("TimeRepository initialized succesfully: %s", session)

    # --- CRUD ---
    def add(self, minutes: float, note_id: int) -> int:
        obj = models.TimeModel(minutes=minutes, note_id=note_id)
        try:
            self.session.add(obj)
            self.session.commit()
            logger.info("add(id=%s, minutes=%s, note_id=%s) [Success]", obj.id, round(minutes, 3), note_id)
            return obj.id
        except IntegrityError as e:
            self.session.rollback()
            logger.exception("add(minutes=%s, note_id=%s) [IntegrityError - Possible duplicate]: %s", round(minutes, 3), note_id, e)
            raise UniqueConstraintViolation("unique_violation") from e
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.exception("add(minutes=%s, note_id=%s) [SQLAlchemyError]: %s", round(minutes, 3), note_id, e)
            raise RepositoryError("db_error") from e
        except Exception as e:
            self.session.rollback()
            logger.exception("add(minutes=%s, note_id=%s) [Unexpected error]", round(minutes, 3), note_id)
            raise RepositoryError("unexpected_error") from e
        
    def count_by_note(self, note_id: int) -> int:
        try:
            count = (
                self.session
                .query(func.count(models.TimeModel.id))
                .filter(models.TimeModel.note_id == note_id)
                .scalar()
            )
            logger.info("count_by_note(id=%s) [Success]", note_id)
            return count or 0
        except SQLAlchemyError as e:
            logger.exception("count_by_note(id=%s) [SQLAlchemyError]: %s", note_id, e)
            raise RepositoryError("db_error") from e
        except Exception as e:
            logger.exception("count_by_note(id=%s) [Unexpected error]", note_id)
            raise RepositoryError("unexpected_error") from e
    
    """
    Number of distinct date(YYYY - MM - DD) for which at least one
    TimeModel record exists for that note_id
    """
    def count_active_days_by_note(self, note_id: int) -> int:
        try:
            count = (
                self.session
                .query(
                    func.count(
                        func.distinct(
                            func.date(models.TimeModel.created_at)
                        )
                    )
                )
                .filter(models.TimeModel.note_id == note_id)
                .scalar()
            )

            logger.info("count_active_days_by_note(id=%s) [Success]", note_id)
            return count or 0
        except SQLAlchemyError as e:
            logger.exception(
                "count_active_days_by_note(id=%s) [SQLAlchemyError]: %s",
                note_id, e)
            raise RepositoryError("db_error") from e
        except Exception as e:
            logger.exception("count_active_days_by_note(id=%s) [Unexpected error]", note_id)
            raise RepositoryError("unexpected_error") from e
        

    def get_total_minutes_by_note(self, note_id: int) -> int:
        try:
            total = (
                    self.session.query(
                        func.coalesce(func.sum(models.TimeModel.minutes), 0)
                    )
                    .filter(models.TimeModel.note_id == note_id)
                    .scalar()
                )
            logger.info("get_total_minutes_by_note(id=%s) [Success]", note_id)
            return total or 0
        except SQLAlchemyError as e:
            logger.exception(
                "get_total_minutes_by_note(id=%s) [SQLAlchemyError]: %s",
                note_id, e
            )
            raise RepositoryError("db_error") from e
        except Exception as e:
            logger.exception("get_total_minutes_by_note(id=%s) [Unexpected error]", note_id)
            raise RepositoryError("unexpected_error") from e