from pathlib import Path

ARTICLES = [
    "223112R020",
    "233002F700",
]

BASE_URL = "https://www.avito.ru/moskva_i_mo"

SEARCH_PARAMS = {
    "condition": "new",
    "s": "104",
}

TOP_N = 5

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CACHE_DIR = PROJECT_ROOT / "cache"

OUTPUT_CSV = str(PROJECT_ROOT / "result.csv")
OUTPUT_XLSX = str(PROJECT_ROOT / "result.xlsx")

REQUEST_TIMEOUT = 10
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

ALLOWED_REGION_HINTS = ("моск",)
REQUIRED_CONDITION_HINT = "нов"
