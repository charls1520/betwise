from scrapling import StealthyFetcher
from src.utils.logger import get_logger

logger = get_logger()

def fetch_page_content(url: str) -> str:
    """Uses Scrapling to stealthily fetch page content."""
    try:
        fetcher = StealthyFetcher()
        page = fetcher.get(url)
        return page.text
    except Exception as e:
        logger.error(f"Scrapling error for {url}: {e}")
        return ""