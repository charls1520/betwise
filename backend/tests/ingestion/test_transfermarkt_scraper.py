from src.ingestion.scrapers.transfermarkt import TransfermarktScraper

def test_get_absences():
    scraper = TransfermarktScraper()
    scraper.fetch_page_content = lambda url: "<html><td class='hauptlink'>Messi</td><td class='ausfall'>Injured</td></html>"
    
    absences = scraper.get_absences("mock_url")
    assert len(absences) > 0
    assert absences[0]['player'] == "Messi"
    assert absences[0]['reason'] == "Injured"