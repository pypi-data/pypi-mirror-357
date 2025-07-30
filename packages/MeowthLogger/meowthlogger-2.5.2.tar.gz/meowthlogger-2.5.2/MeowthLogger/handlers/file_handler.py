import os
import shutil
from datetime import datetime, timedelta
from logging.handlers import TimedRotatingFileHandler

from MeowthLogger.app.parser.files import DirectoriesTree
from MeowthLogger.constants import (
    DEFAULT_LOGGING_FILENAME,
    FOLDER_DATE_FORMAT,
    LOGFILE_ITERATE_MAX_ATTEMPTS,
)
from MeowthLogger.errors import NotValidFile
from MeowthLogger.utilities.custom_hour import Hour
from MeowthLogger.utilities.dates import date_from_logstring, set_null_minutes


class LogFile:
    def __init__(self, path: str) -> None:
        self.path = path

    def get_last_date(self) -> datetime:
        with open(self.path, "rb") as file:
            lines = file.readlines()
            try:
                date = self.find_date(lines)
            except:
                return datetime.now()
        return date

    def find_date(self, lines: list[str]) -> datetime:
        attempts = 0
        for line in lines[::-1]:
            if attempts >= LOGFILE_ITERATE_MAX_ATTEMPTS:
                raise NotValidFile(self.path)
            try:
                return date_from_logstring(line.decode("utf-8"))
            except:
                continue

        raise NotValidFile(self.path)


class FileHandler(TimedRotatingFileHandler):
    def __init__(
        self, path: str, max_log_alive_time: int, *args, **kwargs
    ) -> None:
        self.max_log_alive_time = max_log_alive_time
        self.path = path
        self.generate_root_path()
        super().__init__(
            filename=os.path.join(self.path, DEFAULT_LOGGING_FILENAME),
            *args,
            **kwargs,
        )
        self.start_rollover()

    # Rollovering block ---- >
    def start_rollover(self) -> None:
        now = set_null_minutes(datetime.now())
        last_date = set_null_minutes(self.last_logstream_date)
        if last_date < now:
            self.doRollover()

    def doRollover(self) -> None:
        self.close_stream()
        if self.max_log_alive_time is None:
            self.clear_files()

        date_from = set_null_minutes(self.last_logstream_date) + timedelta(
            hours=1
        )

        file_path = self.generate_file_path(date_from)
        self.rotate(self.baseFilename, self.rotation_filename(file_path))
        self.open_stream()
        self.rolloverAt = self.computeRollover()

    def computeRollover(self, *args) -> datetime:
        now = datetime.now()
        rollover_at = (
            now
            - timedelta(
                minutes=now.minute,
                seconds=now.second,
                microseconds=now.microsecond,
            )
            + timedelta(hours=1)
        )
        self.rolloverAt = rollover_at
        return rollover_at

    def shouldRollover(self, *args) -> bool:
        if not self.is_exists_base_file():
            self.rolloverAt = self.computeRollover()
            return False
        elif datetime.now() >= self.rolloverAt:
            return True
        return False

    # Rollovering block ---- <

    # Clearing block ---- >
    def clear_files(self) -> None:
        delta = timedelta(seconds=self.max_log_alive_time)
        dt_del = datetime.now() - delta

        tree = DirectoriesTree(self.path)

        filtered = list(filter(lambda dir: dir.date <= dt_del, tree.dirs))

        if filtered:
            while len(filtered) > 1:
                path = filtered.pop(0)
                shutil.rmtree(path.path_join)

            files = filtered[0].files
            files = list(filter(lambda file: file.date < dt_del, files))

            while len(files):
                file = files.pop()
                os.remove(file.path_join)

    # Clearing block ---- <

    # Streaming block ---- >>
    def close_stream(self) -> None:
        try:
            self.stream.close()
        except:
            pass
        self.stream = None

    def open_stream(self) -> None:
        self.stream = self._open()

    # Streaming block ---- <<

    # Files pathes block ---- >>

    # Base file ---- >
    @property
    def base_file_path(self) -> str:
        return os.path.join(self.path, DEFAULT_LOGGING_FILENAME)

    def is_exists_base_file(self) -> bool:
        return os.path.exists(self.base_file_path)

    # Base file ---- <

    # Path generators ---- >
    def generate_root_path(self) -> None:
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def generate_folder_path(self, date: datetime) -> str:
        folder_path = os.path.join(self.path, self.prepare_foldername(date))

        if not os.path.exists(folder_path):
            os.mkdir(folder_path)

        return folder_path

    def generate_file_path(self, date: datetime) -> str:
        folder_path = self.generate_folder_path(date)

        file_path = os.path.join(
            folder_path, self.prepare_log_filename(Hour(date.hour))
        )

        if os.path.exists(file_path):
            os.remove(file_path)

        return file_path

    # Path generators ---- <

    # Path prepearers ---->
    @staticmethod
    def prepare_foldername(date: datetime) -> str:
        return date.strftime(FOLDER_DATE_FORMAT)

    @staticmethod
    def prepare_log_filename(hour: Hour) -> str:
        return f"{hour.previous_hour}.00-{hour}.00.log"

    # Path prepearers ----<

    # Files pathes block ---- <<

    # Utils ---- >>
    @property
    def last_logstream_date(self) -> datetime:
        log_file = LogFile(self.base_file_path)

        try:
            date = log_file.get_last_date()
        except:
            return datetime.now()

        return date

    # Utils ---- <<
