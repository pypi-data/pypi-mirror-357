import typing

from .base import BaseLogger

T = typing.TypeVar("T")

class DevNullLogger(BaseLogger):
    def print(self, data: T, *args) -> None:
        pass

    def pbar(
        self,
        data: typing.Iterable[T],
        total: int = None,
        desc: typing.Optional[str] = None
    ) -> typing.Iterable[T]:
        return data

    def zip(
        self,
        *iterables, 
        desc: typing.Optional[str] = None
    ):
        return zip(*iterables)

    def set_pbar_postfix(self, pbar: typing.Any, data: dict):
        pass
