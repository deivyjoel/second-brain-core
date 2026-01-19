from dataclasses import dataclass

@dataclass(frozen=True)
class NewNoteDTO:
    """DTO for transporting new note data to the repository."""
    name: str
    theme_id: int | None



