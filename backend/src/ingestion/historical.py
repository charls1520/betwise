import pandas as pd
import requests
import io


def download_football_data_co_uk(
    seasons: list = ["2324", "2223", "2122", "2021", "1920"],
) -> pd.DataFrame:
    """Downloads historical Premier League CSVs from football-data.co.uk and concatenates them."""
    base_url = "https://www.football-data.co.uk/mmz4281/{}/E0.csv"
    dfs = []

    for season in seasons:
        url = base_url.format(season)
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            df = pd.read_csv(io.StringIO(response.text))

            # Keep only relevant columns to avoid bloat
            cols_to_keep = [
                "Date",
                "HomeTeam",
                "AwayTeam",
                "FTHG",
                "FTAG",
                "FTR",
                "HST",
                "AST",
                "HC",
                "AC",
            ]
            # Some older seasons might lack certain columns, so we intersect
            cols = [c for c in cols_to_keep if c in df.columns]

            df = df[cols].copy()
            dfs.append(df)
        except Exception as e:
            print(f"Failed to download season {season}: {e}")

    if dfs:
        return pd.concat(dfs, ignore_index=True)
    return pd.DataFrame()
