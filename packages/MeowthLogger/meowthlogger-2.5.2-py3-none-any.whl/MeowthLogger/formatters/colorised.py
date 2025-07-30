import logging
from datetime import datetime

from colorama import Back, Fore, Style

from .formatter import AbstractFormatter


class ColorisedFormatter(AbstractFormatter):
    def prepare_log_string(
        self,
        datetime: datetime,
        levelname: str,
        filename: str,
        line: str,
        message: str,
    ) -> str:

        datetime = f"{Style.DIM}{datetime}{Style.NORMAL}"
        filename = f"{Fore.LIGHTYELLOW_EX}{filename}{Fore.RESET}"
        line = f"{Fore.LIGHTYELLOW_EX}{line}{Fore.RESET}"

        return super().prepare_log_string(
            datetime,
            levelname,
            filename,
            line,
            message,
        )

    def prepare_levelname(self, levelname: int) -> str:
        match levelname:
            case logging.INFO:
                return f"{Fore.GREEN}INFO{Fore.RESET}"
            case logging.ERROR:
                return f"{Fore.RED}ERROR{Fore.RESET}"
            case logging.WARN:
                return f"{Fore.YELLOW}WARNING{Fore.RESET}"
            case logging.DEBUG:
                return f"{Fore.LIGHTBLACK_EX}DEBUG{Fore.RESET}"
            case logging.CRITICAL:
                return f"{Back.RED} CRITICAL {Back.RESET}"
            case _:
                return f"LEVEL :{levelname}"
