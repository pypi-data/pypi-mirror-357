# Datetime formats ---- >
DUMP_LOGFILE_DATE_FORMAT = "%Hh %d-%m-%Y"
FILE_DATE_FORMAT = "%H.%M"
FOLDER_DATE_FORMAT = "%Y-%m-%d"
LOGSTRING_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
REQUEST_DATESTRING_FORMAT = "%H:%M %d/%m/%Y"

# Logger Formatter ---- >
DEFAULT_FORMATTER = (
    "[{datetime}] {levelname} in {filename} line {line}: {message}"
)

# RegExp for get log from logline ---- >
LOGSTRING_DATE_REGEXP = r"\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]"

# Max attempts for read logline date ---- >
LOGFILE_ITERATE_MAX_ATTEMPTS = 30

# Default settings ---- >
DEFAULT_ENCODING = "utf-8"
DEFAULT_LOGGING_FILENAME = "logging.log"
DEFAULT_LOGGING_LEVEL = "INFO"
DEFAULT_PATH = "logs"
