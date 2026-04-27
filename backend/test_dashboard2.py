import os, json, glob, sys
sys.path.append('/app')
from src.ingestion.normalizer import TeamNormalizer
from src.ml.inference import predict_matches
from src.ml.reliability import calculate_value_edge, meets_data_threshold

def get_dashboard_data():
    raw_dir = "data/raw"
    if not os.path.exists(raw_dir): return {"matches": [], "suggestions": []}
        
    odds_files = glob.glob(f"{raw_dir}/**/odds_*.json", recursive=True)
    if not odds_files: return {"matches": [], "suggestions": []}
        
    latest_file = sorted(odds_files, key=os.path.getmtime)[-1]
    with open(latest_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        raw_odds = data.get("matches", [])

    if not raw_odds: return {"matches": [], "suggestions": []}

    xg_stats = {}
    xg_files = glob.glob(f"{raw_dir}/**/xg_*.json", recursive=True)
    if xg_files:
        latest_xg = sorted(xg_files, key=os.path.getmtime)[-1]
        with open(latest_xg, "r", encoding="utf-8") as f:
            xg_stats = json.load(f)
            
    elo_stats = {}
    elo_files = glob.glob(f"{raw_dir}/**/elo_*.json", recursive=True)
    if elo_files:
        latest_elo = sorted(elo_files, key=os.path.getmtime)[-1]
        with open(latest_elo, "r", encoding="utf-8") as f:
            elo_stats = json.load(f).get("stats", {})

    canonical_teams = list(xg_stats.keys()) if xg_stats else []
    normalizer = TeamNormalizer(canonical_teams)

    valid_odds = []
    for match in raw_odds:
        home_norm = normalizer.normalize(match.get("home_team", ""))
        away_norm = normalizer.normalize(match.get("away_team", ""))

        if home_norm and home_norm in xg_stats and away_norm and away_norm in xg_stats:
            match["home_xg"] = xg_stats[home_norm].get("xg_for_avg")
            match["away_xg"] = xg_stats[away_norm].get("xg_for_avg")
            match["home_elo"] = elo_stats.get(home_norm, elo_stats.get(match.get("home_team"), 1500.0))
            match["away_elo"] = elo_stats.get(away_norm, elo_stats.get(match.get("away_team"), 1500.0))
            valid_odds.append(match)

    predictions = predict_matches(valid_odds, model_dir="models") if valid_odds else []

    dashboard_data = []
    suggestions = []
    for idx, match in enumerate(valid_odds):
        pred = predictions[idx] if idx < len(predictions) else {}
        home_prob = pred.get("prob_home_win", 0.0)
        home_odds = 2.0
        bookmakers = match.get("bookmakers", [])
        if bookmakers and len(bookmakers) > 0:
            markets = bookmakers[0].get("markets", [])
            if markets and len(markets) > 0:
                outcomes = markets[0].get("outcomes", [])
                for outcome in outcomes:
                    if outcome.get("name") == match.get("home_team"):
                        home_odds = outcome.get("price", 2.0)
                        break

        edge = calculate_value_edge(home_prob, home_odds)
        match_obj = {
            "id": idx, "home_team": match.get("home_team"), "away_team": match.get("away_team"),
            "prob_home_win": home_prob, "prob_draw": pred.get("prob_draw", 0.0),
            "prob_away_win": pred.get("prob_away_win", 0.0), "home_odds": home_odds,
            "home_edge": edge, "match_time": match.get("commence_time", "TBA"),
            "league": match.get("sport_title", "PREMIER LEAGUE"), "is_reliable": match.get("is_reliable", True)
        }
        dashboard_data.append(match_obj)
    return {"matches": dashboard_data, "suggestions": suggestions}

res = get_dashboard_data()
print("MATCHES:", len(res.get("matches", [])))
if res.get("matches"):
    print("First match:", json.dumps(res["matches"][0], indent=2))
else:
    print("No matches. Result was:", res)
