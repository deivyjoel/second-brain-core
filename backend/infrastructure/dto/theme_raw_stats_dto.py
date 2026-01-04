from dataclasses import dataclass

@dataclass(frozen=True)
class ThemeRawStatsDTO:
    total_notes: int
    minutes: float
    active_days: int
    n_subthemes: int