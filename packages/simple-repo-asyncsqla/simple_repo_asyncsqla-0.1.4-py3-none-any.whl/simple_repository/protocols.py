from typing import Any, Protocol, Self


class SqlaModel(Protocol):
    __tablename__: str
    id: Any


class DomainModel(Protocol):
    id: Any

    @classmethod
    def model_validate(cls, obj: Any, *args, **kwagrs) -> Self: ...
    def model_dump(self, *args, exclude_unset: bool = False, **kwagrs) -> dict[str, Any]: ...


class Schema(Protocol):
    def model_dump(self, *args, exclude_unset: bool = False, **kwagrs) -> dict[str, Any]: ...
