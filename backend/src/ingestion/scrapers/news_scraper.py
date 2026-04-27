import feedparser
import requests
from tenacity import retry, stop_after_attempt, wait_fixed
from src.utils.logger import get_logger

logger = get_logger()

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def fetch_bbc_sports_news(limit: int = 10) -> list:
    """Fetches the latest football news from BBC Sport RSS."""
    rss_url = "http://feeds.bbci.co.uk/sport/football/rss.xml"
    
    try:
        # Use requests with a strict timeout to prevent feedparser from hanging
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(rss_url, headers=headers, timeout=15)
        response.raise_for_status()
        feed = feedparser.parse(response.content)
    except Exception as e:
        logger.error(f"Error fetching BBC news: {e}")
        return []

    articles = []
    for entry in feed.entries[:limit]:
        articles.append(
            {
                "title": entry.title,
                "url": entry.link,
                "published": entry.published,
                "summary": entry.summary if hasattr(entry, "summary") else "",
            }
        )
    return articles
