from log import logger
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from backend.infrastructure.repositories.sql_alchemy import models
from backend.domain.models.note import Note
from backend.domain.dto.new_note_dto import NewNoteDTO
from backend.infrastructure.dto.note_record_dto import NoteRecordDTO
from backend.infrastructure.mapper.note_to_domain import convert_to_note_domain
from backend.infrastructure.dto.note_record_lite_dto import NoteRecordLiteDTO
from backend.infrastructure.errors.db import RepositoryError, UniqueConstraintViolation


class NoteRepository():
    def __init__(self, session):
        self.session = session
        logger.info("NoteRepository initialized succesfully:: %s", session)
    
    def _to_domain(self, obj: models.NoteModel) -> Note:
        """Converts database model to domain entity."""
        note = NoteRecordDTO(
            id = obj.id,
            name = obj.name,
            theme_id = obj.theme_id,
            content = obj.content or "",
            last_edited_at=obj.last_edited_at,
            created_at = obj.created_at
        )
        return convert_to_note_domain(note, self.session)
    
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
            self.session.rollback()
            logger.exception("update_note(id=%s) [IntegrityError]: %s", note._id, e)
            raise UniqueConstraintViolation("unique_violation") from e
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.exception("update_note(id=%s) [SQLAlchemyError]: %s", note._id, e)
            raise RepositoryError("db_error") from e
        except Exception as e:
            self.session.rollback()
            logger.exception("update_note(id=%s) [Unexpected error]", note._id)
            raise RepositoryError("unexpected_error") from e
        
    def get_by_id(self, note_id: int) -> Note | None:
        try:
            obj = self.session.get(models.NoteModel, note_id)
            logger.info("get_by_id(id=%s) [Success]", note_id)
            return self._to_domain(obj) if obj else None
        except SQLAlchemyError as e:
            logger.exception("get_note(id=%s) [SQLAlchemyError]: %s", note_id, e)
            raise RepositoryError("db_error") from e
        except Exception as e:
            logger.exception("get_note(id=%s) [Unexpected error]", note_id)
            raise RepositoryError("unexpected_error") from e
        
    # --- QUERIES ---
    def _query_notes(self, **filters) -> list[NoteRecordLiteDTO]:
        try:
            objs = self.session.query(models.NoteModel).filter_by(**filters).all()
            logger.info("query_notes(filters=%s) [Succcess]", filters)
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