import abc
import typing
from pathlib import Path

from loguru import logger

from config import CACHE_DIR


class Loader(abc.ABC):
    @staticmethod
    def load(*args, **kwargs) -> typing.Any:
        pass


class CacheLoader(Loader):
    @staticmethod
    def load(article: str, cache_dir: typing.Union[str, Path] = CACHE_DIR) -> typing.Optional[str]:
        path = Path(cache_dir) / f"{article}.html"
        if not path.exists():
            logger.warning(f"Нет тестового HTML для артикула {article}: {path}")
            raise RuntimeError(f"Нет тестового HTML для артикула {article}: {path}")

        return path.read_text(encoding="utf-8")
