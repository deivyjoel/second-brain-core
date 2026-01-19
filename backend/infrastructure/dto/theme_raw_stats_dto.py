from dataclasses import dataclass

@dataclass(frozen=True)
class ThemeRawStatsDTO:
    """DTO to represent raw statistics of a theme."""
    total_notes: int
    minutes: float
    active_days: int
    n_subthemes: int