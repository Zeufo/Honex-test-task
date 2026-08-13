from loguru import logger

from run import Process

try:
    Process.prepare()
    Process.start()

except KeyboardInterrupt:
    logger.warning("Прервано пользователем")
except Exception:
    logger.exception("Парсер завершился с ошибкой")
