from dataclasses import dataclass

@dataclass(frozen=True)
class NoteSummaryDTO:
    id: int
    name: str


