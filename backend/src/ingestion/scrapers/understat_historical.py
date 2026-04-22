import json
import re
import asyncio
import random
from playwright.async_api import async_playwright
import pandas as pd

async def _fetch_understat_season_async(year: str, league_id: str) -> dict:
    url = f"https://understat.com/league/{league_id}/{year}"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Setup realistic context
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()
        
        # Abort unneeded resources to save bandwidth and speed up
        await page.route("**/*", lambda route: route.abort() 
                         if route.request.resource_type in ["image", "stylesheet", "font", "media"] 
                         else route.continue_())
        
        try:
            # Human jitter before navigating
            await asyncio.sleep(random.uniform(2.0, 4.0))
            await page.goto(url, wait_until="networkidle", timeout=30000)
            
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
                    raise Exception("Cloudflare Block / Empty Data")
            
            matches_data = []
            for team_id, team_info in data.items():
                title = team_info.get("title")
                history = team_info.get("history", [])
                if not history:
                    continue
                for match in history:
                    h_team = match.get("h", {}).get("title", "")
                    a_team = match.get("a", {}).get("title", "")
                    matches_data.append({
                        "Team": title,
                        "HomeTeam_Und": h_team,
                        "AwayTeam_Und": a_team,
                        "Date": match.get("date").split(" ")[0],
                        "xG": float(match.get("xG", 0)),
                        "xGA": float(match.get("xGA", 0))
                    })
            if not matches_data:
                raise Exception("Cloudflare Block / Empty Data")
                
            return {"matches": matches_data}
        except Exception as e:
            print(f"Playwright Scraper Error for {league_id} {year}: {e}")
            raise e
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