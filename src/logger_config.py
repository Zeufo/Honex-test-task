import sys

from loguru import logger


def setup_logger() -> None:
    logger.remove()

    console_format = (
        "<green>{time:HH:mm:ss}</green> | "
        "<level>{level: <7}</level> | "
        "<cyan>{name}:{function}:{line}</cyan> - <level>{message}</level>"
    )

    logger.add(sys.stderr, format=console_format, level="DEBUG", backtrace=True, diagnose=False)

    file_format = "{time:YYYY-MM-DD HH:mm:ss} | {level: <7} | {name}:{function}:{line} - {message}"

    logger.add(
        "logs/bot.log",
        format=file_format,
        level="INFO",
        rotation="25 MB",
        retention="10 days",
        compression="zip",
        encoding="utf-8",
        backtrace=True,
        diagnose=False,
    )
