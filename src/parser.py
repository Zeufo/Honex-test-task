import abc
import re
import typing

import bs4
from loguru import logger


class Parser(abc.ABC):
    @staticmethod
    def parse(*args, **kwargs) -> typing.Any:
        pass


class AvitoParser(Parser):
    @staticmethod
    def parse(html: str) -> list[dict]:
        if not html:
            return []

        soup = bs4.BeautifulSoup(html, "html.parser")
        cards = soup.select('[data-marker="item"]')

        results = []
        for card in cards:
            try:
                results.append(AvitoParser._parse_card(card))
            except Exception as e:
                logger.warning(f"Не удалось разобрать карточку объявления: {e}")
        return results

    @staticmethod
    def _parse_card(card: bs4.Tag) -> dict:
        title_tag = card.select_one('[data-marker="item-title"]')
        title = title_tag.get_text(strip=True) if title_tag else None

        link = None
        if title_tag and title_tag.has_attr("href"):
            href = title_tag["href"]
            href_str = href[0] if isinstance(href, list) else str(href)
            link = href_str if href_str.startswith("http") else f"https://www.avito.ru{href_str}"

        price = AvitoParser._extract_price(card)

        address_tag = card.select_one('[data-marker="item-address"]')
        location = address_tag.get_text(strip=True) if address_tag else None

        condition_tag = card.select_one('[data-marker="item-condition"]')
        condition = condition_tag.get_text(strip=True) if condition_tag else None

        return {
            "title": title,
            "price": price,
            "location": location,
            "condition": condition,
            "link": link,
        }

    @staticmethod
    def _extract_price(card: bs4.Tag) -> typing.Optional[int]:
        price_tag = card.select_one('[data-marker="item-price"]')
        if not price_tag:
            return None

        meta_price = price_tag.select_one('meta[itemprop="price"]')
        if meta_price and meta_price.has_attr("content"):
            content = meta_price["content"]
            raw = content[0] if isinstance(content, list) else str(content)
        else:
            raw = price_tag.get_text()

        digits = re.sub(r"[^\d]", "", raw or "")
        if not digits:
            return None
        return int(digits)
