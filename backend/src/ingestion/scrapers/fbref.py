from bs4 import BeautifulSoup
from src.ingestion.scrapers.scrapling_base import fetch_page_content

class FBrefScraper:
    def fetch_page_content(self, url: str) -> str:
        return fetch_page_content(url)
        
    def get_possession(self, match_url: str) -> float:
        html = self.fetch_page_content(match_url)
        if not html:
            return None
        soup = BeautifulSoup(html, 'html.parser')
        # Simplified parsing logic
        poss_td = soup.find('td', {'data-stat': 'possession'})
        if poss_td:
            return float(poss_td.text.strip())
        return None