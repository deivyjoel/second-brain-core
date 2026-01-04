from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class NewThemeDTO:
    name: str
    parent_id: int | None



