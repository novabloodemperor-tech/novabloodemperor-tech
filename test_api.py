import requests
import json

# Test data - a student with good grades
test_data = {
    "cluster_points": 42.0,
    "grades": {
        "Mathematics": "B+",
        "English": "B",
        "Physics": "B-",
        "Chemistry": "C+"
    }
}

try:
    # Send POST request to our API
    response = requests.post(
        'http://127.0.0.1:8000/api/check-eligibility/',
        json=test_data,
        headers={'Content-Type': 'application/json'}
    )
    
    print("Status Code:", response.status_code)
    print("Response:")
    print(json.dumps(response.json(), indent=2))
    
except Exception as e:
    print("Error:", e)
