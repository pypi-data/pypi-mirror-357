import os
from datetime import datetime, timedelta

from MeowthLogger.constants import DEFAULT_LOGGING_FILENAME, FOLDER_DATE_FORMAT
from MeowthLogger.utilities.abstractions import DateNameFile


class LogFile(DateNameFile):
    def __init__(self, day: datetime, name: str, path: str) -> None:
        self.path = path
        self.name = name
        hour = int(name[:2])
        self.date = day + timedelta(hours=hour)

    def read(self) -> bytes:
        with open(self.path_join, "rb") as file:
            return file.read()


class RootLogFile(LogFile):
    def __init__(self, name: str, path: str) -> None:
        self.name = name
        self.path = path


class LogDirectory(DateNameFile):
    name: str
    date: datetime

    files: list[LogFile]

    def __init__(self, name: str, path: str) -> None:
        self.name = name
        self.date = datetime.strptime(
            name,
            FOLDER_DATE_FORMAT,
        )
        self.path = path
        self.files = self.get_files()

    def get_files(self) -> list[LogFile]:
        files_list = os.listdir(self.path_join)

        return sorted(
            LogFile(self.date, file_name, self.path_join)
            for file_name in files_list
        )

    def read(self) -> bytes:
        return b"".join([file.read() for file in self.files])


class DirectoriesTree:
    """Tree of logfiles directory
    Used for sorting files by dates
    """

    dirs: list[LogDirectory]

    def __init__(self, path: str) -> None:
        dir_list = os.listdir(path)

        if DEFAULT_LOGGING_FILENAME in dir_list:
            dir_list.remove(DEFAULT_LOGGING_FILENAME)

        self.dirs = sorted(
            [LogDirectory(dir_name, path) for dir_name in dir_list]
        )

    def sort_files(self, date_from: datetime, date_to: datetime) -> None:
        """Sorting self all files by requested dates"""

        if not self.dirs:
            return

        # Filter directories list
        self.dirs = list(
            filter(
                lambda dir: dir.date > date_from - timedelta(days=1)
                and dir.date < date_to,
                self.dirs,
            )
        )

        if self.dirs:
            # Sort files for first directory
            self.dirs[0].files = list(
                filter(
                    lambda file: file.date > date_from - timedelta(hours=1),
                    self.dirs[0].files,
                )
            )

            # Sort files for last directory
            self.dirs[-1].files = list(
                filter(lambda file: file.date < date_to, self.dirs[-1].files)
            )
