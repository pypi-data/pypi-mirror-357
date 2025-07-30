import os
from abc import ABC
from datetime import datetime


class Dictable(ABC):
    """Abstraction for jsonify objects"""

    def json(self) -> dict:
        raise NotImplementedError


class DateNameFile(ABC):
    """Absctraction for read files path and compare by dates"""

    path: str
    name: str
    date: datetime

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} '{self.name}'>"

    def __lt__(self, other) -> bool:  # noqa: ANN001
        if isinstance(other, self.__class__):
            return self.date < other.date
        raise ValueError(f"Other not {self.__class__.__name__} class")

    @property
    def path_join(self) -> str:
        return os.path.join(self.path, self.name)
