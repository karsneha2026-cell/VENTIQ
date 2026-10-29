
import urllib.request
import urllib.error
import json

url = "http://127.0.0.1:5000/api/bookings"

booking = {
    "event_id": 1,
    "customer_name": "Test Customer",
    "customer_email": "test@example.com",
    "tickets": 2
}

data = json.dumps(booking).encode("utf-8")

request = urllib.request.Request(
    url,
    data=data,
    headers={"Content-Type": "application/json"},
    method="POST"
)

try:
    with urllib.request.urlopen(request) as response:
        print("Status:", response.status)
        print(response.read().decode("utf-8"))

except urllib.error.HTTPError as error:
    print("Status:", error.code)
    print(error.read().decode("utf-8"))

except Exception as error:
    print("Error:", error)
