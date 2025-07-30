from abc import ABC

from .abstract import AbstractLoggerConfig
from .utils import ConfigLogger


class UvicornLogger(AbstractLoggerConfig, ABC):
    def _use_uvicorn(self) -> None:
        self.loggers.append(
            ConfigLogger(
                name="uvicorn.access",
                level="INFO",
                handlers=self.handlers,
                propagate=False,
            )
        )

        self.loggers.append(
            ConfigLogger(
                name="uvicorn.error",
                level="INFO",
                handlers=self.handlers,
                propagate=False,
            )
        )
