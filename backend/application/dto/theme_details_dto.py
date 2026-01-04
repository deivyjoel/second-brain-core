from dataclasses import dataclass

@dataclass(frozen=True)
class ThemeDetailDTO:
    theme_id: int
    name: str
    parent_id: int | None
