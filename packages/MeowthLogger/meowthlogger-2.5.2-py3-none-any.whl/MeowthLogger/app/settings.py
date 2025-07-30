from typing import Optional

from ..utilities.log_streaming.stream_manager import Stream


class LoggerSettings:
    """### Settings of root logger
    #### Parameters
    - logger_level: level of logger. Example: "INFO" or "DEBUG"
    - use_files: bool argument for use with files mode or without
    - encoding: file encoding mode. Example: "utf-8"
    - path: logging files path. Example: "logs/logfiles"
    - use_uvicorn: bool argument for use with uvicorn
    """

    def __init__(
        self,
        logger_level: str,
        use_files: bool,
        log_alive_seconds: Optional[int],
        encoding: str,
        path: str,
        use_uvicorn: bool,
        stream: Optional[Stream],
    ) -> None:
        self.logger_level = logger_level
        self.use_files = use_files
        self.log_alive_seconds = log_alive_seconds
        self.encoding = encoding
        self.path = path
        self.use_uvicorn = use_uvicorn
        self.stream = stream
