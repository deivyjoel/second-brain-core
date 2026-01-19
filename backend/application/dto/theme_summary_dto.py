from dataclasses import dataclass

@dataclass(frozen=True)
class ThemeSummaryDTO:
    """DTO to list themes in the UI (Explorer/List View)."""
    id: int
    name: str

