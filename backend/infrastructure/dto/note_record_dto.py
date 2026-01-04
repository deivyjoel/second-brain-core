from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class NoteRecordDTO:
    id: int
    name: str
    theme_id: int | None
    content: str
    last_edited_at: datetime
    created_at: datetime





    