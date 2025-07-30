from logging import getLogger
from logging.config import dictConfig
from typing import Optional

from MeowthLogger.constants import (
    DEFAULT_ENCODING,
    DEFAULT_LOGGING_LEVEL,
    DEFAULT_PATH,
)

from ..utilities.log_streaming.stream_manager import Stream
from .config import MainLoggerConfig
from .parser import LogParser
from .settings import LoggerSettings


class AbstractLogger:
    def __init__(self, logger) -> None:  # noqa: ANN001
        self.info = logger.info
        self.critical = logger.critical
        self.debug = logger.debug
        self.error = logger.error
        self.warning = logger.warning


class Logger(LogParser, AbstractLogger):
    settings: LoggerSettings

    def __init__(
        self,
        logger_level: str = DEFAULT_LOGGING_LEVEL,
        use_files: bool = True,
        log_alive_seconds: Optional[int] = 604800,
        encoding: str = DEFAULT_ENCODING,
        path: str = DEFAULT_PATH,
        use_uvicorn: bool = False,
        stream: Optional[Stream] = None,
    ) -> None:

        self.settings = LoggerSettings(
            logger_level=logger_level,
            use_files=use_files,
            log_alive_seconds=log_alive_seconds,
            encoding=encoding,
            path=path,
            use_uvicorn=use_uvicorn,
            stream=stream,
        )

        if stream:
            stream.setup_logger(self)

        dictConfig(self.__config)
        super().__init__(getLogger())

    @property
    def __config(self) -> dict:
        return MainLoggerConfig(self.settings).json()
