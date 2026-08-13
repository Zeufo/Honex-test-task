import typing
from datetime import datetime

from loguru import logger

from config import (
    ALLOWED_REGION_HINTS,
    ARTICLES,
    BASE_URL,
    OUTPUT_CSV,
    OUTPUT_XLSX,
    REQUIRED_CONDITION_HINT,
    SEARCH_PARAMS,
    TOP_N,
)
from exporter import CsvExport, ExcelExport
from fetcher import AvitoFetcher
from loader import CacheLoader
from logger_config import setup_logger
from parser import AvitoParser


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _passes_filters(item: dict) -> bool:
    if item.get("price") is None:
        return False

    condition = (item.get("condition") or "").lower()
    if condition and REQUIRED_CONDITION_HINT not in condition:
        return False
    if not condition:
        return False

    location = (item.get("location") or "").lower()
    if location and not any(hint in location for hint in ALLOWED_REGION_HINTS):
        return False
    if not location:
        return False

    return True


def _dedupe(items: list[dict]) -> list[dict]:
    seen_links = set()
    unique = []
    for item in items:
        link = item.get("link")
        key = link if link else (item.get("title"), item.get("price"))
        if key in seen_links:
            continue
        seen_links.add(key)
        unique.append(item)
    return unique


class Process:
    @staticmethod
    def prepare() -> None:
        setup_logger()

    @staticmethod
    def start() -> list[dict]:
        all_rows: list[dict] = []

        for article in ARTICLES:
            all_rows.extend(Process._process_article(article))

        CsvExport.export(all_rows, OUTPUT_CSV)
        ExcelExport.export(all_rows, OUTPUT_XLSX)
        return all_rows

    @staticmethod
    def _process_article(article: str) -> list[dict]:
        checked_at = _now()
        params = {"q": article, **SEARCH_PARAMS}

        html = AvitoFetcher.fetch(BASE_URL, params)
        source = "live"

        if html is None:
            logger.info(f"[{article}] live-запрос недоступен, пробую локальный тестовый HTML...")
            html = CacheLoader.load(article)
            source = "cache"

        if html is None:
            logger.error(f"[{article}] нет ни live-ответа, ни тестового HTML")
            return [Process._status_row(article, params["q"], "ошибка", checked_at)]

        raw_items = AvitoParser.parse(html)
        if not raw_items:
            logger.warning(f"[{article}] ({source}) объявлений на странице не найдено")
            return [Process._status_row(article, params["q"], "не найдено", checked_at)]

        filtered = [i for i in raw_items if _passes_filters(i)]
        filtered = _dedupe(filtered)
        filtered.sort(key=lambda i: i["price"])
        top = filtered[:TOP_N]

        if not top:
            logger.warning(f"[{article}] ({source}) нет подходящих объявлений после фильтрации")
            return [Process._status_row(article, params["q"], "не найдено", checked_at)]

        logger.info(f"[{article}] ({source}) отобрано {len(top)} объявлений")
        rows = []
        for rank, item in enumerate(top, start=1):
            rows.append(
                {
                    "article": article,
                    "query": params["q"],
                    "title": item.get("title"),
                    "price": item.get("price"),
                    "location": item.get("location"),
                    "condition": item.get("condition"),
                    "link": item.get("link"),
                    "rank": rank,
                    "status": "ok",
                    "checked_at": checked_at,
                }
            )
        return rows

    @staticmethod
    def _status_row(article: str, query: str, status: str, checked_at: str) -> dict:
        return {
            "article": article,
            "query": query,
            "title": None,
            "price": None,
            "location": None,
            "condition": None,
            "link": None,
            "rank": None,
            "status": status,
            "checked_at": checked_at,
        }
