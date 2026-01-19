from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class NoteAnalyticsDTO:
    """DTO to transport note analytics data."""
    name: str
    created_at: datetime
    last_edited_at: datetime
    minutes_total: float
    n_sessions: int
    n_days_active: int
    n_words_total: int
    n_content_words_total: int
    n_u_content_words_totals: int
    lexical_diversity_rate: float
