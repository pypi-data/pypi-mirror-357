from ..settings import LoggerSettings
from .abstract import AbstractLoggerConfig
from .console import ConsoleLogger
from .file import FileLogger
from .stream import StreamLogger
from .uvicorn import UvicornLogger


class MainLoggerConfig(
    FileLogger,
    ConsoleLogger,
    UvicornLogger,
    StreamLogger,
    AbstractLoggerConfig,
):

    def __init__(
        self,
        settings: LoggerSettings,
        version: int = 1,
    ) -> None:
        super().__init__(settings, version)

        self._use_console()

        if settings.use_files:
            self._use_files()

        if settings.use_uvicorn:
            self._use_uvicorn()

        if settings.stream:
            self._use_stream()
