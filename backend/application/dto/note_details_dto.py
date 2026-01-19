from dataclasses import dataclass

@dataclass(frozen=True)
class NoteDetailDTO:
    """DTO for transporting complete note information. Contains content data."""
    id: int
    name: str
    theme_id: int | None
    content: str 




    