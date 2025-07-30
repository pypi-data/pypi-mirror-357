import io
from datetime import datetime, timedelta

from MeowthLogger.app.settings import LoggerSettings
from MeowthLogger.constants import (
    DEFAULT_LOGGING_FILENAME,
    DUMP_LOGFILE_DATE_FORMAT,
)
from MeowthLogger.errors import LoggerNotUsingFileSystem
from MeowthLogger.utilities.dates import (
    convert_request_datestring,
    set_null_minutes,
)

from .files import DirectoriesTree, RootLogFile


class LogParser:
    """### Parser for load logs from logs directory and return streaming
    #### Usage:
    ```
    parser = LogParser(settings)
    date_from = "13:00 01/01/1999"
    stream: io.BytesIO = parser.stream_logs(date_from)

    date_to = "13:00 01/01/2099"
    stream: io.BytesIO = parser.stream_logs(date_from, date_to)
    ```

    #### Stream name was look as "(13h 01-01-1999) (13h 01-01-2099).log"
    U can add custom headder for filename
    ```
    stream = parser.stream_logs(date_from, stream_name_header="LOGGER!")
    ```
    Filename should be look as "LOGGER!(13h 01-01-1999) (13h 01-01-2099).log"

    Or set custom name
    ```
    stream = parser.stream_logs(date_from)
    stream.name = "LOGGER.log"
    ```
    """

    settings: LoggerSettings

    @classmethod
    def prepare_dates(
        cls, date_from: str, date_to: str
    ) -> tuple[datetime, datetime]:
        """Preparing dates before load logs files"""
        date_from = set_null_minutes(convert_request_datestring(date_from))

        date_to = set_null_minutes(
            convert_request_datestring(date_to) if date_to else datetime.now()
        ) + timedelta(hours=1)

        if date_from >= date_to:
            raise ValueError("Not valid dates")

        return date_from, date_to

    @staticmethod
    def prepare_filename(
        date_from: datetime, date_to: datetime, header: str = None
    ) -> str:
        """Preparing filename for dumping file"""

        # func for prepare dates to string
        def prepare_date(date: datetime) -> str:
            return date.strftime(DUMP_LOGFILE_DATE_FORMAT)

        return (
            ""
            + (header if header else "")
            + f"({prepare_date(date_from)})"
            + " "
            + f"({prepare_date(date_to)})"
            + ".log"
        )

    def stream_logs(
        self,
        date_from: datetime,
        date_to: datetime = None,
        stream_name_header: str = None,
    ) -> io.BytesIO:
        self.__validate_settings()

        date_from, date_to = self.prepare_dates(date_from, date_to)

        # Initialise bytes for writing in
        dump_file = io.BytesIO()

        dir_tree = DirectoriesTree(self.settings.path)
        if dir_tree.dirs:
            dir_tree.sort_files(date_from, date_to)

        for dir in dir_tree.dirs:
            dump_file.write(dir.read())

        if date_to > datetime.now():
            root_logfile = RootLogFile(
                DEFAULT_LOGGING_FILENAME, self.settings.path
            )
            dump_file.write(root_logfile.read())

        # change filename
        dump_file.name = self.prepare_filename(
            date_from, date_to, stream_name_header
        )
        # saving file
        dump_file.seek(0)

        return dump_file

    def __validate_settings(self) -> None:
        if not self.settings.use_files:
            raise LoggerNotUsingFileSystem
