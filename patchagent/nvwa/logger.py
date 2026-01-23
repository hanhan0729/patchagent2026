import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

# ANSI escape sequences for colored and bold output
COLORS = {
    "HEADER": "\033[95m",  # Purple
    "OKBLUE": "\033[94m",
    "OKGREEN": "\033[92m",
    "OKCYON": "\033[96m",
    "WARNING": "\033[93m",
    "FAIL": "\033[91m",
    "ENDC": "\033[0m",
    "BOLD": "\033[1m",
    "UNDERLINE": "\033[4m",
}

LEVEL_COLORS = {
    logging.DEBUG: COLORS["OKGREEN"],
    logging.INFO: COLORS["OKBLUE"],
    logging.WARNING: COLORS["BOLD"] + COLORS["WARNING"],
    logging.ERROR: COLORS["BOLD"] + COLORS["FAIL"],
    logging.CRITICAL: COLORS["BOLD"] + COLORS["HEADER"],
}


class ColoredFormatter(logging.Formatter):
    def __init__(self, fmt, datefmt, style="%"):
        super().__init__(fmt, datefmt, style)  # type: ignore

    def format(self, record):
        level_color = LEVEL_COLORS.get(record.levelno, COLORS["ENDC"])
        message = super().format(record)
        message = f"{level_color}{message}{COLORS['ENDC']}"
        return message


class CustomLogger(logging.Logger):
    def __init__(self, name, level=logging.NOTSET):
        super().__init__(name, level)

    def green(self, message, *args, **kwargs):
        for msg in message.split("\n"):
            self._log(logging.INFO, COLORS["BOLD"] + COLORS["OKGREEN"] + msg + COLORS["ENDC"] + COLORS["ENDC"], args, **kwargs)

    def purple(self, message, *args, **kwargs):
        for msg in message.split("\n"):
            self._log(logging.INFO, COLORS["BOLD"] + COLORS["HEADER"] + msg + COLORS["ENDC"] + COLORS["ENDC"], args, **kwargs)

    def cyon(self, message, *args, **kwargs):
        for msg in message.split("\n"):
            self._log(logging.INFO, COLORS["BOLD"] + COLORS["OKCYON"] + msg + COLORS["ENDC"] + COLORS["ENDC"], args, **kwargs)


def setup_logger(log_file=None, level=logging.INFO, max_size=10000000, backups=5):
    """
    Creates a logger instance with colored and bold console output for certain levels.
    Automatically names log files based on the current date and time if not specified.
    """
    logger = CustomLogger(__name__)
    logger.setLevel(level)

    if not log_file:
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_file = os.path.join(log_dir, f"{current_time}.log")

    file_handler = RotatingFileHandler(log_file, maxBytes=max_size, backupCount=backups)
    file_handler.setLevel(level)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)

    colored_formatter = ColoredFormatter("[%(asctime)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

    file_handler.setFormatter(colored_formatter)
    console_handler.setFormatter(colored_formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


logging.setLoggerClass(CustomLogger)
log = setup_logger()

if __name__ == "__main__":
    log.debug("This is a debug message")
    log.info("This is an info message")
    log.warning("This is a warning message")
    log.error("This is an error message")
    log.green("This\n is a green message")
    log.purple("This is a purple message\n")
    log.cyon("This is a yellow\n message")
