import urllib.request, json

req = urllib.request.Request(
    "http://localhost:8000/ask/",
    data=json.dumps({
        "query": "Can I work part-time on a student visa in Germany?",
        "country_code": "DE",
        "user_profile": {"nationality": "IN"}
    }).encode(),
    headers={"Content-Type": "application/json"},
    method="POST"
)

with urllib.request.urlopen(req) as r:
    for line in r:
        print(line.decode().strip())