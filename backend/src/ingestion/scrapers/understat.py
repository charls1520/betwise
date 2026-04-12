import requests
import re
import json
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_fixed


@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def fetch_current_xg_stats() -> dict:
    """Scrapes Understat for current season xG averages per team."""
    url = "https://understat.com/league/EPL"
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    scripts = soup.find_all("script")

    team_data_script = None
    for script in scripts:
        if script.string and "var teamsData" in script.string:
            team_data_script = script.string
            break

    if not team_data_script:
        return {}

    # Extract JSON string from script
    json_match = re.search(
        r"var teamsData\s*=\s*JSON\.parse\('([^']+)'\);", team_data_script
    )
    if json_match:
        # Understat uses hex-encoded JSON in JS
        decoded = bytes(json_match.group(1), "utf-8").decode("unicode_escape")
        try:
            data = json.loads(decoded)
        except:
            return {}
    else:
        # Try direct assignment pattern just in case
        json_match = re.search(r"var teamsData\s*=\s*({.*?});", team_data_script)
        if not json_match:
            return {}
        data = json.loads(json_match.group(1))

    stats = {}
    for team_id, team_info in data.items():
        title = team_info.get("title")
        history = team_info.get("history", [])
        if not history:
            continue

        # Calculate simple averages from history
        total_xg = sum(float(match.get("xG", 0)) for match in history)
        total_xga = sum(float(match.get("xGA", 0)) for match in history)
        matches_played = len(history)

        stats[title] = {
            "xg_for_avg": total_xg / matches_played if matches_played else 0,
            "xg_against_avg": total_xga / matches_played if matches_played else 0,
        }

    return stats
