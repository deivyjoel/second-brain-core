from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class NoteRecordLiteDTO:
    """DTO to represent a lightweight note record without content data."""
    id: int
    name: str
    theme_id: int | None
    last_edited_at: datetime
    created_at: datetime