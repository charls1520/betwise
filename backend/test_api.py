import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import sys

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

url = "https://understat.com/league/EPL/2023"
r = requests.get(url, headers=headers, verify=False)
print("Length:", len(r.text))
if "teamsData" in r.text:
    print("teamsData FOUND in requests!")
else:
    print("teamsData NOT FOUND in requests!")
