# debug_test.py
import requests
import json

test_data = {
    "cluster_points": 10.0,  # Very low points to match many courses
    "grades": {
        "Mathematics": "C",
        "English": "C"
    }
}

print("🔍 Testing API response...")
try:
    response = requests.post(
        'https://novabloodemperor-tech-backend.onrender.com/api/check-eligibility/',
        json=test_data
    )
    
    print(f"Status Code: {response.status_code}")
    print("Full Response:")
    print(json.dumps(response.json(), indent=2))
    
except Exception as e:
    print(f"Error: {e}")