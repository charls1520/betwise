from src.ingestion.scrapers.fbref import FBrefScraper

def test_fbref_scraper_possession():
    scraper = FBrefScraper()
    # Mocking fetch_page_content
    scraper.fetch_page_content = lambda url: "<html><td data-stat='possession'>55</td></html>"
    
    possession = scraper.get_possession("mock_url")
    assert possession == 55.0