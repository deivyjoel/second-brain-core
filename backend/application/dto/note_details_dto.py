from dataclasses import dataclass

@dataclass(frozen=True)
class NoteDetailDTO:
    id: int
    name: str
    theme_id: int | None
    content: str 




    