from bs4 import BeautifulSoup
from src.ingestion.scrapers.scrapling_base import fetch_page_content

class TransfermarktScraper:
    def fetch_page_content(self, url: str) -> str:
        return fetch_page_content(url)
        
    def get_absences(self, team_url: str) -> list:
        html = self.fetch_page_content(team_url)
        if not html:
            return []
            
        soup = BeautifulSoup(html, 'html.parser')
        absences = []
        # Extremely simplified logic
        player_td = soup.find('td', class_='hauptlink')
        reason_td = soup.find('td', class_='ausfall')
        
        if player_td and reason_td:
            absences.append({
                'player': player_td.text.strip(),
                'reason': reason_td.text.strip()
            })
            
        return absences