from abc import ABC

from .abstract import AbstractLoggerConfig
from .console import ConfigConsoleHandler
from .utils import ConfigFormatter, ConfigLogger


class StreamLogger(AbstractLoggerConfig, ABC):
    def _use_stream(self) -> None:
        formatter = ConfigFormatter(
            name="ws_stream",
            class_name="MeowthLogger.formatters.DefaultFormatter",
        )
        self.formatters.append(formatter)

        handler = ConfigConsoleHandler(
            name="ws_stream",
            class_name="logging.StreamHandler",
            level=self.settings.logger_level,
            formatter=formatter,
            stream=self.settings.stream,
        )
        self.handlers.append(handler)

        logger = ConfigLogger(
            name="console",
            level=self.settings.logger_level,
            propagate=False,
            handlers=[handler],
        )
        self.loggers.append(logger)
