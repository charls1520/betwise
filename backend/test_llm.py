import traceback
from src.rag.config import init_llama_index
from src.ingestion.normalizer import TeamNormalizer
from src.ingestion.scrapers.understat_historical import fetch_understat_historical_season

init_llama_index()
# simulating historical.py
try:
    fetch_understat_historical_season("2023", "EPL")
except Exception:
    pass

n = TeamNormalizer(['Newcastle United'])

try:
    print("Asking LLM without retries...")
    res = n._ask_llm.__wrapped__(n, 'Newcastle')
    print("Result:", res)
except Exception as e:
    print("Exception caught:")
    traceback.print_exc()