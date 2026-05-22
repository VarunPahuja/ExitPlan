import os
from dotenv import load_dotenv
import urllib.request
import json

load_dotenv()

key = os.getenv("GEMINI_API_KEY")
print(f"Key found: {'Yes' if key else 'No'}")
print(f"Key starts with: {key[:8] if key else 'MISSING'}...")

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={key}"
body = json.dumps({"contents":[{"parts":[{"text":"Say hello in one word"}]}]}).encode()

try:
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req) as r:
        result = json.loads(r.read())
        print("SUCCESS:", result["candidates"][0]["content"]["parts"][0]["text"])
except Exception as e:
    print(f"FAILED: {e}")