
import urllib.request
import json

url = "http://127.0.0.1:5000/api/events"

event = {
    "title": "Midnight Music Festival",
    "category": "Concert",
    "event_date": "2026-11-15",
    "location": "Kolkata",
    "price": 999
}

data = json.dumps(event).encode("utf-8")

request = urllib.request.Request(
    url,
    data=data,
    headers={"Content-Type": "application/json"},
    method="POST"
)

try:
    with urllib.request.urlopen(request) as response:
        print(response.status)
        print(response.read().decode("utf-8"))
except Exception as error:
    print("Error:", error)
