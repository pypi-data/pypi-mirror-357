import logging
import os
import time
from datetime import datetime

from MeowthLogger.constants import DEFAULT_FORMATTER


class AbstractFormatter(logging.Formatter):
    def __init__(self) -> None:
        logging.Formatter.__init__(self, "")

    def format(self, record: str) -> str:
        return self.prepare_log_string(
            datetime=time.strftime(
                self.default_time_format, self.converter(record.created)
            ),
            levelname=self.prepare_levelname(record.levelno),
            filename=record.pathname.replace(os.path.abspath(""), "."),
            line=str(record.lineno),
            message=record.getMessage(),
        )

    def prepare_log_string(
        self,
        datetime: datetime,
        levelname: str,
        filename: str,
        line: int,
        message: str,
    ) -> str:
        return DEFAULT_FORMATTER.format(
            datetime=datetime,
            levelname=levelname,
            filename=filename,
            line=line,
            message=message,
        )

    def prepare_levelname(self, levelname: int) -> str:
        match levelname:
            case logging.INFO:
                return f"INFO"
            case logging.ERROR:
                return f"ERROR"
            case logging.WARN:
                return f"WARNING"
            case logging.DEBUG:
                return f"DEBUG"
            case logging.CRITICAL:
                return f"CRITICAL"
            case _:
                return f"LEVEL :{levelname}"
