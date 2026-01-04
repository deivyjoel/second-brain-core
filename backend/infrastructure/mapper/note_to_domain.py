from backend.infrastructure.dto.note_record_dto import NoteRecordDTO
from backend.infrastructure.repositories.time_repository import TimeRepository

from backend.domain.models.note import Note

def convert_to_note_domain(note: NoteRecordDTO, session) -> Note:
    time_repo = TimeRepository(session)
    minutes = time_repo.get_total_minutes_by_note(note.id)
    return Note(
        id=note.id,
        name = note.name,
        content = note.content,
        minutes = minutes,
        theme_id = note.theme_id,
        last_edited_at=note.last_edited_at,
        created_at=note.created_at
    )