from dataclasses import dataclass

@dataclass(frozen=True)
class ThemeDetailDTO:
    """DTO for transporting complete theme information."""
    theme_id: int
    name: str
    parent_id: int | None
