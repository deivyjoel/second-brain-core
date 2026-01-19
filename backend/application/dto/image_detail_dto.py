from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class ImageDetailDTO:
    """DTO for transporting complete image information for rendering."""
    id: int
    name: str
    file_path: str
    theme_id: int | None
    created_at: datetime