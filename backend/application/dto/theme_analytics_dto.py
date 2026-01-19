from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class ThemeAnalyticsDTO:
    """DTO to transport theme analytics data."""
    name: str
    created_at: datetime
    last_edited_at: datetime
    minutes_total: float
    n_notes_directly: int
    n_entities: int
    n_days_active: int
    n_content_words_total: int
    n_u_content_words_totals: int
