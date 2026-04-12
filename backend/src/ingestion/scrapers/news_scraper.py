import feedparser
from tenacity import retry, stop_after_attempt, wait_fixed


@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def fetch_bbc_sports_news(limit: int = 10) -> list:
    """Fetches the latest football news from BBC Sport RSS."""
    rss_url = "http://feeds.bbci.co.uk/sport/football/rss.xml"
    feed = feedparser.parse(rss_url)

    articles = []
    for entry in feed.entries[:limit]:
        articles.append(
            {
                "title": entry.title,
                "link": entry.link,
                "published": entry.published,
                "summary": entry.summary if hasattr(entry, "summary") else "",
            }
        )
    return articles
