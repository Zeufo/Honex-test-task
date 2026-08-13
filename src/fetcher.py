import abc
import typing

import requests
from loguru import logger
from tenacity import (
    retry,
    stop_after_attempt,
    stop_after_delay,
    wait_fixed,
)

from config import REQUEST_TIMEOUT, USER_AGENT

BLOCK_MARKERS = ("captcha", "доступ ограничен", "просим прощения за неудобства")


class Fetcher(abc.ABC):
    @staticmethod
    def fetch(*args, **kwargs) -> typing.Any:
        pass


@typing.final
class AvitoFetcher(Fetcher):
    """Делает live-запрос к Avito. При сетевой ошибке, ошибочном статусе
    или обнаруженной странице блокировки возвращает None — вызывающий код
    (run.py) в этом случае переключается на локальные тестовые HTML."""

    @staticmethod
    @retry(
        stop=(stop_after_attempt(2) | stop_after_delay(30)),
        wait=wait_fixed(1),
        reraise=False,
    )
    def _get(link: str, params: dict) -> requests.Response:
        headers = {"User-Agent": USER_AGENT, "Accept-Language": "ru-RU,ru;q=0.9"}
        return requests.get(link, params=params, headers=headers, timeout=REQUEST_TIMEOUT)

    @staticmethod
    def fetch(link: str, params: dict) -> typing.Optional[str]:
        try:
            response = AvitoFetcher._get(link, params)
        except Exception as e:
            logger.warning(f"Не удалось получить {link} с параметрами {params}: {e}")
            return None

        if response is None or response.status_code != 200:
            status = getattr(response, "status_code", "нет ответа")
            logger.warning(f"{link} вернул статус {status}, считаем недоступным")
            return None

        text_lower = response.text.lower()
        found_markers = [marker for marker in BLOCK_MARKERS if marker in text_lower]
        if found_markers:
            logger.warning(
                f"{link} отдал 200, но похоже на страницу блокировки/каптчи "
                f"(размер ответа {len(response.text)} байт, найдены маркеры: {found_markers})"
            )
            return None

        return response.text
