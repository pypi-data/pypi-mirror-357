from MeowthLogger.utilities.abstractions import Dictable


class ConfigFormatter(Dictable):
    def __init__(self, name: str, class_name: str) -> None:
        self.name = name
        self.class_name = class_name

    def json(self) -> dict:
        return {
            "()": self.class_name,
        }


class ConfigHandler(Dictable):
    def __init__(
        self,
        name: str,
        class_name: str,
        formatter: ConfigFormatter,
        level: str,
    ) -> None:
        self.name = name
        self.class_name = class_name
        self.formatter = formatter
        self.level = level

    def json(self) -> dict:
        return {
            "class": self.class_name,
            "formatter": self.formatter.name,
            "level": self.level,
        }


class ConfigLogger(Dictable):
    def __init__(
        self,
        name: str,
        level: str,
        handlers: list[ConfigHandler],
        propagate: bool,
    ) -> None:
        self.name = name
        self.level = level
        self.handlers = handlers
        self.propagate = propagate

    def json(self) -> dict:
        return {
            "level": self.level,
            "propagate": self.propagate,
            "handlers": [handler.name for handler in self.handlers],
        }


class ConfigRoot(Dictable):
    def __init__(self, level: str, handlers: list[ConfigHandler]) -> None:
        self.level = level
        self.handlers = handlers

    def json(self) -> dict:
        return {
            "level": self.level,
            "handlers": [handler.name for handler in self.handlers],
        }
