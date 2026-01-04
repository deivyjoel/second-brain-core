from dataclasses import dataclass

@dataclass(frozen=True)
class ThemeSummaryDTO:
    id: int
    name: str

