import abc
import csv
import typing

from loguru import logger

FIELDNAMES = [
    "article",
    "query",
    "title",
    "price",
    "location",
    "condition",
    "link",
    "rank",
    "status",
    "checked_at",
]


class Export(abc.ABC):
    @staticmethod
    def export(*args, **kwargs) -> typing.Any:
        pass


class CsvExport(Export):
    @staticmethod
    def export(rows: list[dict], path: str) -> None:
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()
            for row in rows:
                writer.writerow({key: row.get(key, "") for key in FIELDNAMES})
        logger.info(f"Сохранено {len(rows)} строк в {path}")


class ExcelExport(Export):
    @staticmethod
    def export(rows: list[dict], path: str) -> None:
        try:
            from openpyxl import Workbook
        except ImportError:
            logger.warning(
                "openpyxl не установлен — пропускаю экспорт в .xlsx (result.csv уже сохранён)"
            )
            return

        wb = Workbook()
        ws = wb.active

        if ws is None:
            raise RuntimeError("Не удалось создать Excel-файл")

        ws.title = "result"
        ws.append(FIELDNAMES)
        for row in rows:
            ws.append([row.get(key, "") for key in FIELDNAMES])
        wb.save(path)
        logger.info(f"Сохранено {len(rows)} строк в {path}")
