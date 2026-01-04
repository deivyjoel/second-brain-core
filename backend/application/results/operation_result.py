from typing import Generic, TypeVar, Optional

T = TypeVar("T")

class OperationResult(Generic[T]):
    def __init__(self, successful: bool, info: str, obj: Optional[T]):
        self._successful = successful
        self._info = info
        self._obj = obj

    @property
    def successful(self) -> bool:
        return self._successful

    @property
    def info(self) -> str:
        return self._info

    @property
    def obj(self) -> Optional[T]:
        return self._obj
