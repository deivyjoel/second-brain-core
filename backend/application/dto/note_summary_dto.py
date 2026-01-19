from dataclasses import dataclass

@dataclass(frozen=True)
class NoteSummaryDTO:
    """DTO to list notes in the UI (Explorer/List View)."""
    id: int
    name: str


