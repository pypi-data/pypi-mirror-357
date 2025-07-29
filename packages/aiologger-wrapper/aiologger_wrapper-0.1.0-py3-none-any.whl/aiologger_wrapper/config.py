from datetime import datetime
from logging import DEBUG
from pathlib import Path
from typing import Dict

from aiologger import Logger  # type: ignore
from aiologger.handlers.files import AsyncFileHandler  # type: ignore
from aiologger.formatters.base import Formatter  # type: ignore


from aiologger_wrapper.enums import Levels

LOGGERS_BY_DATE: Dict[str, Logger] = {}  # Dictionary for storing loggers by dates


async def logger(
        # Required
        level: Levels,
        message: str,
        directory_path: Path | str,
        # Optional
        directory_name: Path | str = Path("logs"),
        logger_name: str = "SERVICE"
) -> None:
    """
        Asynchronous logger with writing to a file, organized by dates (Basic type):

        YourProject/
        └── logs/
             └── 01.01.2025.log
             └── 02.01.2025.log
             └── ....

        :param level: Registered logging level via enums -> Levels
        :param message: Any message in str format
        :param directory_path: Path where the log folder will be created (Example: Path(__file__).parent or /logs or ..)
        :param directory_name: Name of the folder for logs
        :param logger_name: Logger name in logs

        Example:
        await logger(level=Levels.INFO, message="Hello World!")
        01.01.2025.log -> 2025-01-01 11:11:11,111 - SERVICE - INFO - Hello World!

        await logger(level=Levels.INFO, message="Hello World!", directory_path="../testpath", directory_name="testname")
        await logger(level=Levels.INFO, message="Hello World!", directory_name=Path("testpath"))
    """
    if isinstance(directory_path, str):
        directory_path = Path(directory_path)
    if isinstance(directory_name, str):
        directory_name = Path(directory_name)

    formatter: Formatter = Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    current_date: str = datetime.now().strftime("%d.%m.%Y")

    log_dir = directory_path / directory_name  # / -> Pathlib operator for combining paths
    log_dir.mkdir(mode=0o755, exist_ok=True)  # mode=(755 - owner reads/writes, others only read)

    log_filename: Path = log_dir / f"{current_date}.log"

    # Closing loggers for old dates
    old_loggers = [date for date in LOGGERS_BY_DATE if date != current_date]
    for old_date_logger in old_loggers:
        old_logger = LOGGERS_BY_DATE.pop(old_date_logger)
        await old_logger.shutdown()

    # Initializing a new logger for the current date
    if current_date not in LOGGERS_BY_DATE:
        custom_logger = Logger(name=logger_name)

        file_handler = AsyncFileHandler(  # Setting up a file handler
            filename=str(log_filename),
            mode="a",
            encoding="utf-8",
        )
        file_handler.formatter = formatter
        file_handler.level = DEBUG  # Minimum logging level

        custom_logger.add_handler(file_handler)
        LOGGERS_BY_DATE[current_date] = custom_logger
    else:
        custom_logger = LOGGERS_BY_DATE[current_date]

    log_level: str = level.value
    match log_level:
        case "DEBUG":
            await custom_logger.debug(message)
        case "INFO":
            await custom_logger.info(message)
        case "WARNING":
            await custom_logger.warning(message)
        case "ERROR":
            await custom_logger.error(message)
        case "CRITICAL":
            await custom_logger.critical(message)
        case _:
            await custom_logger.error(f"Invalid logging level: {level}, message: {message}")


async def shutdown_loggers():
    """Более безопасное закрытие с поэтапной очисткой"""
    for date in list(LOGGERS_BY_DATE.keys()):
        logs: Logger = LOGGERS_BY_DATE.get(date)  # type: ignore
        if logs:
            try:
                await logs.shutdown()
            except Exception as err:
                await logger(level=Levels.CRITICAL, message=f"Shutdown error for date {date} -- {err}")
            finally:
                LOGGERS_BY_DATE.pop(date, None)
