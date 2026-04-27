import sys
sys.path.append('/app')
import json
from src.main import get_dashboard_data

res = get_dashboard_data()
print("MATCHES:", len(res.get("matches", [])))
if res.get("matches"):
    print("First match:", json.dumps(res["matches"][0], indent=2))
else:
    print("No matches. Result was:", res)
