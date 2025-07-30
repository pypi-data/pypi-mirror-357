class NotDateLogString(Exception):
    def __init__(self) -> None:
        super().__init__("It's not date log string")


class NotValidFile(ValueError):
    def __init__(self, path: str) -> None:
        super().__init__(f"File {path} is not valid log file")


class NotValidLogsDateFormat(ValueError):
    def __init__(self) -> None:
        super().__init__(
            "Not valid datetime string format, format is hh:mm DD/MM/YYYY"
        )


class LoggerNotUsingFileSystem(Exception):
    def __init__(self) -> None:
        super().__init__("Logger not using file system")
