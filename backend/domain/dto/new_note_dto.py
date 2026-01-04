from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class NewNoteDTO:
    name: str
    theme_id: int | None



