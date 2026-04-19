import json
import re
import asyncio
import nest_asyncio
from playwright.async_api import async_playwright
from tenacity import retry, stop_after_attempt, wait_fixed

# Patch asyncio to allow nested event loops (useful for FastAPI/Jupyter)
nest_asyncio.apply()

async def _fetch_understat_async() -> dict:
    url = "https://understat.com/league/EPL"

    async with async_playwright() as p:
        # Launch headless browser
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        try:
            # Go to the page and wait for network to be mostly idle (bypasses basic CF checks)
            await page.goto(url, wait_until="networkidle", timeout=15000)

            # The data is inside a script tag.
            # We can execute JS on the page to extract the variable directly if the page loaded successfully.
            # However, if CF blocks us, teamsData might be undefined.

            # First, check if teamsData is defined in the window object
            is_defined = await page.evaluate("typeof teamsData !== 'undefined'")

            if is_defined:
                # If the JS variable exists, extract it directly! No regex needed.
                data = await page.evaluate("teamsData")
            else:
                # Fallback: grab all script tags and try regex if it's there but not evaluated
                content = await page.content()
                match = re.search(
                    r"var teamsData\s*=\s*JSON\.parse\('([^']+)'\);", content
                )
                if match:
                    decoded = bytes(match.group(1), "utf-8").decode("unicode_escape")
                    data = json.loads(decoded)
                else:
                    raise Exception("teamsData not found on page.")

            stats = {}
            for team_id, team_info in data.items():
                title = team_info.get("title")
                history = team_info.get("history", [])
                if not history:
                    continue

                total_xg = sum(float(match.get("xG", 0)) for match in history)
                total_xga = sum(float(match.get("xGA", 0)) for match in history)
                matches_played = len(history)

                stats[title] = {
                    "xg_for_avg": total_xg / matches_played if matches_played else 0,
                    "xg_against_avg": total_xga / matches_played
                    if matches_played
                    else 0,
                }
            return stats

        except Exception as e:
            print(f"Playwright Scraper Error: {e}")
            raise e
        finally:
            await browser.close()


@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def fetch_current_xg_stats() -> dict:
    """Synchronous wrapper for the async Playwright scraper."""
    # Create a new event loop for this thread if necessary, or run in the current one
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(_fetch_understat_async())
