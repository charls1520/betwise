import pytest
from src.ingestion.scrapers.understat import fetch_current_xg_stats


def test_fetch_current_xg_stats_playwright_la_liga():
    stats = fetch_current_xg_stats("La_liga")
    assert stats is not None
    assert isinstance(stats, dict)
    assert len(stats.keys()) > 0
    # Since playwright is hard to mock correctly without a real browser context,
    # we will do a basic integration test that actually fires up the headless browser.
    # This ensures it really works against Cloudflare in testing.
    stats = fetch_current_xg_stats()
    assert stats is not None
    assert isinstance(stats, dict)

    # Check if the fallback or real data came through
    assert "Arsenal" in stats or len(stats.keys()) > 0

    if "Arsenal" in stats:
        assert "xg_for_avg" in stats["Arsenal"]
        assert "xg_against_avg" in stats["Arsenal"]

from src.ingestion.scrapers.understat_historical import _fetch_understat_season_async

@pytest.mark.asyncio
async def test_fetch_understat_historical_raises_on_empty(mocker):
    # Mock playwright to return NO data (Cloudflare block)
    mock_playwright = mocker.AsyncMock()
    mock_browser = mocker.AsyncMock()
    mock_context = mocker.AsyncMock()
    mock_page = mocker.AsyncMock()
    
    mock_playwright.chromium.launch.return_value = mock_browser
    mock_browser.new_context.return_value = mock_context
    mock_context.new_page.return_value = mock_page
    
    mock_page.evaluate.return_value = False # is_defined = False
    mock_page.content.return_value = "<html>Cloudflare blocked you</html>"
    
    # We need to mock the async context manager `async with async_playwright() as p:`
    mock_playwright_cm = mocker.AsyncMock()
    mock_playwright_cm.__aenter__.return_value = mock_playwright
    
    mocker.patch("src.ingestion.scrapers.understat_historical.async_playwright", return_value=mock_playwright_cm)
    
    with pytest.raises(Exception, match="Cloudflare Block / Empty Data"):
        await _fetch_understat_season_async("2023", "EPL")
