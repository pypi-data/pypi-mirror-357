from abc import ABC

from .abstract import AbstractLoggerConfig
from .utils import ConfigFormatter, ConfigHandler, ConfigLogger


class ConfigFileHandler(ConfigHandler):
    def __init__(
        self,
        when: str,
        encoding: str,
        path: str,
        max_log_alive_time: int,
        *args,
        **kwargs
    ) -> None:
        self.when = when
        self.encoding = encoding
        self.path = path
        self.max_log_alive_time = max_log_alive_time
        super().__init__(*args, **kwargs)

    def json(self) -> dict:
        json = super().json()
        json.update(
            {
                "when": self.when,
                "encoding": self.encoding,
                "path": self.path,
                "max_log_alive_time": self.max_log_alive_time,
            }
        )
        return json


class FileLogger(AbstractLoggerConfig, ABC):
    def _use_files(self) -> None:
        default_formatter = ConfigFormatter(
            name="default",
            class_name="MeowthLogger.formatters.DefaultFormatter",
        )
        self.formatters.append(default_formatter)

        file_handler = ConfigFileHandler(
            name="file",
            class_name="MeowthLogger.handlers.FileHandler",
            level=self.settings.logger_level,
            formatter=default_formatter,
            when="midnight",
            encoding=self.settings.encoding,
            path=self.settings.path,
            max_log_alive_time=self.settings.log_alive_seconds,
        )
        self.handlers.append(file_handler)

        file_logger = ConfigLogger(
            name="file",
            level=self.settings.logger_level,
            propagate=False,
            handlers=[file_handler],
        )
        self.loggers.append(file_logger)
