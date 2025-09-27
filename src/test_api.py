import requests
import json
from datetime import datetime, timedelta

# Test data
test_request = {
    "destination": "Paris",
    "departure_location": "New York",
    "start_date": (datetime.now() + timedelta(days=20)).strftime("%Y-%m-%d"),
    "end_date": (datetime.now() + timedelta(days=25)).strftime("%Y-%m-%d"),
    "budget": 3000.0,
    "travelers": 2,
    "preferences": ["luxury"],
    "special_requirements": "Direct flights preferred"
}

# Make the request
response = requests.post(
    "http://localhost:8000/api/plan-trip",
    json=test_request,
    headers={"Content-Type": "application/json"}
)

# Print the response
print("\nStatus Code:", response.status_code)
print("\nResponse:")
print(json.dumps(response.json(), indent=2))