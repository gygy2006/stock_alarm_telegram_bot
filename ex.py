import requests
import json
import re
import pandas as pd

clinetID = "Imn6eQOWGk9p8prlV9cf"
clinetPW = "vymAq63_og"
headers = {"X-Naver-Client-Id": clinetID, "X-Naver-Client-Secret": clinetPW}
query = "query=계약&"
request = requests.get(
    f"https://openapi.naver.com/v1/search/news.json?{query}", headers=headers
)
json_data = request.json()

for data in json_data["items"]:
    data["description"] = re.sub(
        "<(/)?([a-zA-Z]*)(\\s[a-zA-Z]*=[^>]*)?(\\s)*(/)?>", "", data["description"]
    ).replace("&quot;", '"')
    print(data)
