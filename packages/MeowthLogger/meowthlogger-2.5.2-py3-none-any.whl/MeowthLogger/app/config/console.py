from abc import ABC

from .abstract import AbstractLoggerConfig
from .utils import ConfigFormatter, ConfigHandler, ConfigLogger


class ConfigConsoleHandler(ConfigHandler):
    def __init__(self, stream: str, *args, **kwargs) -> None:
        self.stream = stream
        super().__init__(*args, **kwargs)

    def json(self) -> dict:
        json = super().json()
        json.update(
            {
                "stream": self.stream,
            }
        )
        return json


class ConsoleLogger(AbstractLoggerConfig, ABC):
    def _use_console(self) -> None:
        colorised_formatter = ConfigFormatter(
            name="colorised",
            class_name="MeowthLogger.formatters.ColorisedFormatter",
        )
        self.formatters.append(colorised_formatter)

        console_handler = ConfigConsoleHandler(
            name="console",
            class_name="logging.StreamHandler",
            level=self.settings.logger_level,
            formatter=colorised_formatter,
            stream="ext://sys.stdout",
        )
        self.handlers.append(console_handler)

        console_logger = ConfigLogger(
            name="console",
            level=self.settings.logger_level,
            propagate=False,
            handlers=[console_handler],
        )
        self.loggers.append(console_logger)
