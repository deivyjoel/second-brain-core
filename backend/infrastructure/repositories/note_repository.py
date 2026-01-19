from log import logger
from sqlalchemy import delete
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from backend.infrastructure.repositories.sql_alchemy import models
from backend.infrastructure.dto.note_record_lite_dto import NoteRecordLiteDTO
from backend.infrastructure.errors.db import RepositoryError, UniqueConstraintViolation
from backend.infrastructure.repositories._time_repository import TimeRepository

from backend.domain.models.note import Note
from backend.domain.dto.new_note_dto import NewNoteDTO


class NoteRepository():
    def __init__(self, session):
        self.session = session
        self.time_repo = TimeRepository(session)
        logger.info("NoteRepository initialized succesfully:: %s", session)

    def _to_domain(self, note: models.NoteModel) -> Note:
        minutes = self.time_repo.get_total_minutes_by_note(note.id)
        return Note(
            id=note.id,
            name = note.name,
            content = note.content or "",
            minutes = minutes,
            theme_id = note.theme_id,
            last_edited_at=note.last_edited_at,
            created_at=note.created_at
        )
    
    def _to_dto(self, obj: models.NoteModel) -> NoteRecordLiteDTO:
        """Converts database model to dto."""
        return NoteRecordLiteDTO(
            id = obj.id,
            name = obj.name,
            theme_id = obj.theme_id,
            last_edited_at = obj.last_edited_at,
            created_at = obj.created_at
        )

    # --- CRUD ---
    def add(self, note: NewNoteDTO) -> int:
        obj = models.NoteModel(
            name=note.name, 
            theme_id=note.theme_id
        )
        try:
            self.session.add(obj)
            self.session.commit()
            logger.info("add_note(id=%s) [Success]", obj.id)
            return obj.id
        except IntegrityError as e:
            self.session.rollback()
            logger.exception("add_note(name=%s) [IntegrityError - Possible duplicate]: %s", note.name, e)
            raise UniqueConstraintViolation("unique_violation") from e
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.exception("add_note(name=%s) [SQLAlchemyError]: %s", note.name, e)
            raise RepositoryError("db_error") from e
        except Exception as e:
            self.session.rollback()
            logger.exception("add_note(name=%s) [Unexpected error]", note.name)
            raise RepositoryError("unexpected_error") from e

    def delete(self, note_id: int) -> None:
        note_obj = self.session.get(models.NoteModel, note_id)
        if not note_obj:
            logger.warning("delete_note(id=%s) [Not found]", note_id)
            raise RepositoryError("not_found")
        try:
            self.session.delete(note_obj)
            self.session.commit()
            logger.info("delete_note(id=%s) [Success]", note_id)
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.exception("delete_note(id=%s) [SQLAlchemyError]: %s", note_id, e)
            raise RepositoryError("db_error") from e
        except Exception as e:
            self.session.rollback()
            logger.exception("delete_note(id=%s) [Unexpected error]", note_id)
            raise RepositoryError("unexpected_error") from e

    def update(self, note: Note) -> None:
        note_obj = self.session.get(models.NoteModel, note._id)
        if not note_obj:
            logger.warning("update_note(id=%s) [Not found]", note._id)
            raise RepositoryError("not_found")

        note_obj.name = note._name
        note_obj.content = note._content
        note_obj.theme_id = note._theme_id
        note_obj.last_edited_at = note._last_edited_at

        try:
            self.session.commit()
            logger.info("update_note(id=%s) [Sucess]", note._id)

        except IntegrityError as e:
            logger.exception("update_note(id=%s) [IntegrityError]: %s", note._id, e)
            raise UniqueConstraintViolation("unique_violation") from e
        except SQLAlchemyError as e:
            logger.exception("update_note(id=%s) [SQLAlchemyError]: %s", note._id, e)
            raise RepositoryError("db_error") from e
        except Exception as e:
            logger.exception("update_note(id=%s) [Unexpected error]", note._id)
            raise RepositoryError("unexpected_error") from e

    def delete_many(self, note_ids: list[int]) -> None:
        """ Delete multiple notes at once."""
        if not note_ids: return
                
        try:
            stmt = delete(models.NoteModel).where(models.NoteModel.id.in_(note_ids))
            self.session.execute(stmt)
            self.session.commit()
            logger.info("delete_many_notes(ids=%s) [Success]", note_ids)
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.exception("delete_many_notes [SQLAlchemyError]: %s", e)
            raise RepositoryError("db_error") from e
        except Exception as e:
            self.session.rollback()
            logger.exception("delete_many_notes [Unexpected error]")
            raise RepositoryError("unexpected_error") from e
        
    # --- QUERIES ---
    def get_by_id(self, note_id: int) -> Note | None:
        try:
            obj = self.session.get(models.NoteModel, note_id)
            logger.info("get_note_by_id(id=%s) [Success]", note_id)
            return self._to_domain(obj) if obj else None
        except SQLAlchemyError as e:
            logger.exception("get_note_by_id(id=%s) [SQLAlchemyError]: %s", note_id, e)
            raise RepositoryError("db_error") from e
        except Exception as e:
            logger.exception("get_note_by_id(id=%s) [Unexpected error]", note_id)
            raise RepositoryError("unexpected_error") from e
        
    def _query_notes(self, **filters) -> list[NoteRecordLiteDTO]:
        try:
            objs = self.session.query(models.NoteModel).filter_by(**filters).all()
            logger.info("query_notes(filters=%s) [Success] - %d notes found", filters, len(objs))
            return [self._to_dto(obj) for obj in objs]
        except SQLAlchemyError as e:
            logger.exception("query_notes(filters=%s) [SQLAlchemyError]: %s", filters, e)
            raise RepositoryError("db_error") from e
        except Exception as e:
            logger.exception("query_notes(filters=%s) [Unexpected error]", filters)
            raise RepositoryError("unexpected_error") from e
        
    def get_all_notes(self) -> list[NoteRecordLiteDTO]:
        return self._query_notes()

    def get_notes_by_theme_id(self, theme_id: int) -> list[NoteRecordLiteDTO]:
        return self._query_notes(theme_id=theme_id)

    def get_notes_without_theme_id(self) -> list[NoteRecordLiteDTO]:
        return self._query_notes(theme_id=None)

    # --- TIME WRAPPERS ---
    def add_time_record(self, note_id: int, minutes: float) -> int:
        return self.time_repo.add(minutes, note_id)
    
    def get_active_days_count(self, note_id: int) -> int:
        return self.time_repo.count_active_days_by_note(note_id)

    def get_time_records_count(self, note_id: int) -> int:
        return self.time_repo.count_by_note(note_id)