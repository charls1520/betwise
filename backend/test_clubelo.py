import re
from src.ingestion.scrapers.clubelo import fetch_clubelo_history

teams = ['Man City', "Nott'm Forest", 'Newcastle', 'Man United', 'Wolves', 'Brighton', 'Bournemouth', 'Sheffield United', 'Luton', 'Aston Villa', 'ManUtd']
for t in teams:
    clean_t = re.sub(r'[^a-zA-Z0-9]', '', t)
    df = fetch_clubelo_history(clean_t)
    if df.empty and 'Forest' in t:
        df = fetch_clubelo_history('Forest')
        if not df.empty: clean_t = 'Forest'
    elif df.empty and 'Utd' in t:
        df = fetch_clubelo_history(clean_t.replace('Utd', 'United'))
        if not df.empty: clean_t = clean_t.replace('Utd', 'United')
    print(f'{t} -> {clean_t} returned {len(df)} rows')
