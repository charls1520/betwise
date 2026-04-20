import json
import re
import asyncio
from playwright.async_api import async_playwright
import pandas as pd

async def _fetch_understat_season_async(year: str, league_id: str) -> dict:
    url = f"https://understat.com/league/{league_id}/{year}"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            await page.goto(url, wait_until="networkidle", timeout=15000)
            is_defined = await page.evaluate("typeof teamsData !== 'undefined'")
            
            if is_defined:
                data = await page.evaluate("teamsData")
            else:
                content = await page.content()
                match = re.search(r"var teamsData\s*=\s*JSON\.parse\('([^']+)'\);", content)
                if match:
                    decoded = bytes(match.group(1), "utf-8").decode("unicode_escape")
                    data = json.loads(decoded)
                else:
                    return {}
            
            matches_data = []
            for team_id, team_info in data.items():
                title = team_info.get("title")
                history = team_info.get("history", [])
                for match in history:
                    matches_data.append({
                        "Team": title,
                        "Date": match.get("date").split(" ")[0],
                        "xG": float(match.get("xG", 0)),
                        "xGA": float(match.get("xGA", 0))
                    })
            return {"matches": matches_data}
        finally:
            await browser.close()

def fetch_understat_historical_season(year: str, league_id: str = "EPL") -> pd.DataFrame:
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
    data = loop.run_until_complete(_fetch_understat_season_async(year, league_id))
    if not data or "matches" not in data:
        return pd.DataFrame()
    
    df = pd.DataFrame(data["matches"])
    df["Date"] = pd.to_datetime(df["Date"])
    return df