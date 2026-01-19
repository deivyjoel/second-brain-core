from dataclasses import dataclass

@dataclass(frozen=True)
class ImageSummaryDTO:
    """DTO to list images in the UI (Explorer/List View)."""
    id: int
    name: str